from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout as user_logout
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from django.http import HttpResponseForbidden
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.contrib.sites.models import Site

import re
import urllib
import hashlib
import base64
import os
import zipfile
import StringIO
from math import ceil
from models import *


# -----------------------------------------------------------------------------
# Utils
# -----------------------------------------------------------------------------
name_reg = r'^([\w|\.]*)$'

def is_valid_name(name):
	"""
	Gets a value indicating if a ressource name is correct,
	e.g :
		- It contains only letters, numbers and underscores
	"""
	match = re.match(name_reg, name)
	return True if match else False
	
def get_test_category(request, name):
	"""
	Gets the test category with the given name.
	Creating a new test category is only allowed if the
	user is staff.
	"""
	cats = TestCategory.objects.filter(name=name)
	if len(cats) > 0:
		return cats[0]
	
	if request.user.is_staff:
		cat = TestCategory()
		cat.name = name
		cat.description = ""
		cat.save()
		return cat
	else:
		raise PermissionDenied("You are not allowed to create new categories. You must use existing ones.")
		
def get_schedulers_by_name(name="", need_validation=None):
	"""
	Gets the scheduler(s) corresponding to the given name.
	
	:param need_validation: if true : return only the validated 
	schedulers. If false : return only the non validated schedulers.
	If None : returns all schedulers.
	:param name: name of the scheduler.
	"""
	response = None
	if(name == ""):
		response = SchedulingPolicy.objects.all()
	else:
		response = SchedulingPolicy.objects.filter(name__exact=name)
	
	if need_validation != None:
		response = response.filter(approved=need_validation)
	
	return response
		
def b64(data):
	return base64.b64encode(data)
	
def decode_base64(data):
    """Decode base64, padding being optional.

    :param data: Base64 data as an ASCII byte string
    """
    missing_padding = 4 - len(data) % 4
    if missing_padding:
        data += b'='* missing_padding
    return base64.decodestring(data)

def save(data_array):
	"""call save on each value in data_array then return data_array. Used for convenience"""
	for data in data_array:
		data.save()
	return data_array

	
def paginate(request, page, pageSize=5, dispPages=15):
	"""
	Given a request function, a page number and a page size, 
	returns a tuple (count, page, start, end, items, pagesDisp, pagesCount)
	"""
	itemCount = request.count()
	if(itemCount == 0):
		return (0, 0, 0, 0, [], [0], 0)
	
	pagesCount = int(itemCount / pageSize) - (1 if (itemCount % pageSize == 0) else 0)
	page = min(pagesCount, max(0, int(page)))
		
	start = pageSize * page
	end = min((page+1)*pageSize, itemCount)
	
	# Fills the page numbers displayed to the user.
	pagesDisp = []
	if(pagesCount <= dispPages):
		pagesDisp = [x for x in range(0, pagesCount+1)]
	else:
		curPage = max(0, page-dispPages/2)
		for i in range(0, dispPages):
			pagesDisp.append(curPage)
			curPage += 1
			if curPage > pagesCount:
				break
	
	return (itemCount, page, start, end, request[start:end], pagesDisp, pagesCount)

# -----------------------------------------------------------------------------
# Views
# -----------------------------------------------------------------------------
@login_required
def index(request):
	template = loader.get_template('app.html')
	context = RequestContext(request, {
		'domain' : request.build_absolute_uri()
	})
	return HttpResponse(template.render(context))

@login_required
def scheduler_upload_form(request):
	template = loader.get_template('upload_scheduler.html')
	context = RequestContext(request, {
	})
	return HttpResponse(template.render(context))

@login_required
def logout(request):
	"""Logs out the user"""
	user_logout(request)
	return redirect(auth_views.login)


@login_required
def download_scheduler(request, identifier):
	scheds = SchedulingPolicy.objects.filter(pk=identifier)
	if len(scheds) == 0:
		raise Http404()
		
	filename = scheds[0].name + ".py"
	mimetype = "text/python"
	response = HttpResponse(scheds[0].code, content_type=mimetype)
	response["Content-Disposition"] = "attachment; filename={}".format(filename)
	return response

@login_required
def view_scheduler(request, identifier):
	"""View where the user can see and download the scheduler"""
	scheds = SchedulingPolicy.objects.filter(pk=identifier)
	if len(scheds) == 0:
		raise Http404()
	
	template = loader.get_template('scheduler.html')
	sched = scheds[0]
	context = RequestContext(request, {
		'sched' : sched,
	})
	return HttpResponse(template.render(context))

@login_required
def view_testset(request, identifier):
	"""View where the user can see a test set"""
	testsets = TestSet.objects.filter(pk=identifier)
	if len(testsets) == 0:
		raise Http404()
	
	template = loader.get_template('testset.html')
	context = RequestContext(request, {
		'testset' : testsets[0],
		'categories' : ','.join([cat.name for cat in testsets[0].categories.all()])
	})
	
	return HttpResponse(template.render(context))

@login_required
def download_testset(request, identifier):
	testsets = TestSet.objects.filter(pk=identifier)
	if len(testsets) == 0:
		raise Http404()
	testset = testsets[0]
	# Writes all the testset files to a zip archive
	zip_subdir = "testset " + str(identifier) + "/"
	s = StringIO.StringIO("")
	with zipfile.ZipFile(s, 'w') as zf:
		for f in testset.files.all():
			filename = zip_subdir + "test_" + str(f.id) + ".xml"
			zf.writestr(filename.encode('ascii'), f.conf.encode('ascii'))
	
	zip_content = s.getvalue()
	response = HttpResponse(zip_content, content_type="application/x-zip-compressed")
	response['Content-Disposition'] = 'attachment; filename=testset' + identifier + ".zip"
	return response
	
@login_required
def contributions(request):
	"""
	View where the users can view their contributions.
	The admins can also edit them.
	"""
	template = loader.get_template('manage_validation.html')
	itemType = request.GET.get('type', 'scheduler')
	display = request.GET.get('display', 'all') # my, all
	approved_str = request.GET.get('approved', 'all')
	page = int(request.GET.get('page', 0))
	
	# Processes the approved value
	approvedMap = {'all' : None, 'yes' : True, 'no' : False}
	approved = approvedMap.get(approved_str, None)
	
	# Creates the request
	req = None
	if itemType == 'scheduler':
		req = get_schedulers_by_name("", approved)
	elif itemType == 'testset':
		if approved == None:
			req = TestSet.objects.all()
		else:
			req = TestSet.objects.filter(approved=approved)
	else:
		if approved == None:
			req = Results.objects.all()
		else:
			req = Results.objects.filter(approved=approved)
	
	# Filter by user
	if display == "my":
		req = req.filter(contributor=request.user)
	else:
		# Don't show the non-approved entries to lambda users.
		if not request.user.is_staff:
			req = req.filter(Q(contributor=request.user) | Q(approved=True))
	
	
	# Call paginate
	count, page, start, end, items, pagesDisp, pagesCount = paginate(req, page, 10)
	
	context = RequestContext(request, {
		'count' : count,
		'page' : page,
		'start' : start,
		'end' : end,
		'items' : items,
		'pagesDisp' : pagesDisp,
		'pagesCount' : pagesCount,
		'type' : itemType,
		'display' : display,
		'approved' : approved_str
	})
	return HttpResponse(template.render(context))

@login_required
def validation_action(request):
	"""
	View which only removes / validates schedulers.
	"""
	action = request.GET['action']
	identifier = request.GET['id']
	item_type = request.GET['type']
	
	objs = None
	item = None
	if item_type == 'scheduler':
		objs = SchedulingPolicy.objects.filter(pk=int(identifier))
		if len(objs) == 0:
			return HttpResponse("error:bad id")
		item = objs[0]
	elif item_type == 'results':
		objs = Results.objects.filter(pk=int(identifier))
		if len(objs) == 0:
			return HttpResponse("error:bad id")
		item = objs[0]
	elif item_type == "testset":
		objs = TestSet.objects.filter(pk=int(identifier))
		if len(objs) == 0:
			return HttpResponse("error: bad id")
		item = objs[0]
	else:
		return HttpResponse("error: bad type")
	
	# Checks permission
	if not request.user.is_staff:
		allowed = item.contributor == request.user and action == "delete" and item.approved == False
		if not allowed:
			return HttpResponseForbidden()
	
	if action == "delete":
		reason = request.GET['reason']
		if reason != "<user>":
			notif = Notification()
			notif.title = "Submission of {} '{}' : refused.".format(item_type, item.name)
			notif.user = item.contributor
			notif.content = reason
			notif.ntype = "danger"
			notif.save()
		item.delete()
		return HttpResponse("success")
	elif action == "validate":
		item.approved = True
		item.save()
		notif = Notification()
		notif.title = "Submission of {} '{}' : approved.".format(item_type, item.name)
		notif.user = item.contributor
		notif.content = "Congratulations ! Your {} has been added to the database.".format(item_type)
		notif.ntype = "success"
		notif.save()
		return HttpResponse("success")
	else:
		return HttpResponse("error:bad action")
		

@login_required
def notifications(request):
	"""
	View where an user can view his notifications.
	"""
	page = 0
	if 'page' in request.GET:
		page = int(request.GET['page'])
	
	display = "unread"
	if 'display' in request.GET:
		display = request.GET['display']
	
	req = None
	if display == "unread":	
		req = Notification.objects.filter(user=request.user, read=False)
	else:
		req = Notification.objects.filter(user=request.user)
		
	count, page, start, end, items, pagesDisp, pagesCount = paginate(req, page)
	
	template = loader.get_template('notifications.html')
	context = RequestContext(request, {
		'display': display,
		'count' : count,
		'page' : page,
		'start' : start,
		'end' : end,
		'notifs' : items,
		'pagesDisp' : pagesDisp,
		'pagesCount' : pagesCount,
		'unread_count' : Notification.objects.filter(user=request.user, read=False).count()
	})
	
	return HttpResponse(template.render(context))

@login_required
def categories(request):
	"""
	View where the users can review the test categories.
	"""
	categories = TestCategory.objects.all();
	template = loader.get_template('categories.html')
	context = RequestContext(request, {
		'categories' : categories
	})
	return HttpResponse(template.render(context))

@csrf_exempt
@user_passes_test(lambda u : u.is_staff)
def post_category_description(request, identifier):
	"""
	View where the admin can save a category description.
	"""
	categories = TestCategory.objects.filter(pk=identifier)
	if categories.count() == 0:
		return HttpResponse("error: bad id");
		
	if not "description" in request.POST:
		return HttpResponse("error: missing description in post request.")
	
	category = categories[0]
	category.description = request.POST["description"]
	category.save()
	
	return HttpResponse("success")

@csrf_exempt
@user_passes_test(lambda u : u.is_staff)
def add_category(request):
	"""
	View where the admin can add a new category
	"""
	if not "description" in request.POST:
		return HttpResponse("error: missing description in post request.")
	if not "name" in request.POST:
		return HttpResponse("error: missing name in post request")
	
	category = TestCategory()
	category.name = request.POST["name"]
	category.description = request.POST["description"]
	category.save()
	return HttpResponse("success")
	
	
	
# -----------------------------------------------------------------------------
# Ajax
# -----------------------------------------------------------------------------
@login_required
def user_read_notification(request):
	"""
	Marks a notification as read
	"""
	identifier = request.GET['id']
	notifs = Notification.objects.filter(pk=identifier, user=request.user)
	if len(notifs) > 0:
		notifs[0].read = True
		notifs[0].save()
		return HttpResponse("success")
	
	return HttpResponse("error")
	
@login_required
def unread_notifications_count(request):
	return HttpResponse(str(Notification.objects.filter(user=request.user, read=False).count()))
		
# -----------------------------------------------------------------------------
# Upload
# -----------------------------------------------------------------------------
@login_required
def upload_scheduler(request):
	"""
	View called with a POST method when an user
	submits a scheduler.
	This view is requested with an AJAX request.
	"""
	name = request.user.username + ".schedulers." + request.POST['sched_name']
	class_name = request.POST['sched_class_name']
	code = request.POST['sched_content']
	
	if not is_valid_name(name):
		return HttpResponse("error:name:Only alphanumerical characters are allowed.")
	if not is_valid_name(class_name):
		return HttpResponse("error:class_name:Only alphanumerical characters are allowed.")
		
	validated = get_schedulers_by_name(name, True)
	
	# If a validated scheduler with the same name exists,
	# throws an error.
	if(len(validated) > 0):
		return HttpResponse("error:name:A scheduler with the same name already exists.")
	
	sched = None
	
	# If there is an existing scheduler with the same name,
	# replace it.
	non_validated = get_schedulers_by_name(name, False)
	ret_code = ""
	if(len(non_validated) > 0):
		sched = non_validated[0]
		ret_code = "override"
	else:
		sched = SchedulingPolicy()
		ret_code = "new"
	
	sched.name = name
	sched.contributor = request.user
	sched.approved = request.user.is_staff
	sched.class_name = class_name
	sched.code = code
	sched.sha1 = hashlib.sha1(code).hexdigest()
	sched.save()
	return HttpResponse(ret_code)

@login_required
@csrf_exempt
def api_upload_testset(request):
	# Conf file or testset id
	test_name = request.user.username + ".testsets." + request.POST["test_name"]
	test_description = request.POST["test_description"]
	conf_files = request.POST.getlist('conf_files')
	test_categories = request.POST.getlist('categories')
	testset = None
	
	# Name checking
	for cat in test_categories:
		if not is_valid_name(cat):
			return HttpResponse("error: invalid category name '{}'." + 
				" Should only contain alphanumerical characters.".format(cat))
	
	if not is_valid_name(test_name):
		return HttpResponse("error: invalid test name '{}'.".format(test_name) + 
			" Should only contain alphanumerical characters.")
	
	# Tests with the same name
	tests = TestSet.objects.filter(name=test_name)
	if tests.count() > 0:
		# If the testset is not approved yet, we can override it.
		if request.user == tests[0].contributor and not tests[0].approved:
			testset = tests[0]
		else:
			# Else : we throw an error.
			return HttpResponse("error: the test name " + test_name + " is already taken.")
	
	# Gets the categories
	categories = None
	try:
		categories = [get_test_category(request, cat) for cat in test_categories]
	except PermissionDenied as e:
		return HttpResponse("error: " + e.message)
		
	# Creates all the conf files
	files = []
	for i in range(0, len(conf_files)):
		f = ConfigurationFile()
		f.conf = conf_files[i]
		files.append(f)
		
	# Creates the test set object if it doesn't exist yet.
	if testset == None:	
		testset = TestSet()
	
	testset.name = test_name
	testset.approved = request.user.is_staff
	testset.description = test_description
	testset.contributor = request.user
	testset.save()
	testset.categories = categories
	testset.files = save(files)
	testset.save()
	
	return HttpResponse("success")
	
@login_required
@csrf_exempt
def api_upload_experiment(request):
	# Metrics
	metrics = request.POST.getlist('metrics')
	metrics_db = []
	for metric in metrics:
		m = Metric()
		values = metric.rsplit(',')
		m.name, m.count, m.avg, m.std, m.median, m.minimum, m.maximum = values
		metrics_db.append(m)
		
	# Conf file or testset id
	testset_id = request.POST["testset_id"]
	
	# Scheduler
	scheduling_policy_id = request.POST['scheduler']
	
	# Gets the scheduler
	schedulers = SchedulingPolicy.objects.filter(pk=scheduling_policy_id)
	if len(schedulers) == 0:
		return HttpResponse("error: no such scheduler")
	scheduler = schedulers[0]
	
	# Gets the testset
	testsets = TestSet.objects.filter(pk=testset_id)
	if len(testsets) == 0:
		return HttpResponse("error: no such testset")
	testset = testsets[0]
	
	# Creates the result object
	result = Results()
	result.approved = request.user.is_staff
	result.contributor = request.user
	result.test_set = testset
	result.scheduling_policy = scheduler
	result.save()
	result.metrics = save(metrics_db)
	result.save()
	
	return HttpResponse("success")

# -----------------------------------------------------------------------------
# API
# -----------------------------------------------------------------------------

@login_required
def api_get_schedulers_by_sha(request, sha):
	"""
	Gets the scheduler(s) corresponding to the given sha1 hex hash.
	"""
	response = None
	if(sha == ""):
		response = SchedulingPolicy.objects.all()
	else:
		response = SchedulingPolicy.objects.filter(sha1__exact=sha, approved=True)
	
	response = response.filter(approved=True)
	
	s = ""
	for sched in response:
		s += str(sched.id) + ","
	
	return HttpResponse(s.rstrip(','));
	
@login_required
def api_get_scheduler_data(request, scheduler_id):
	"""
	Gets the tuple (name, class_name, code) associated to the given scheduler id
	"""
	response = None
	s = ""
	
	response = SchedulingPolicy.objects.filter(id__exact=scheduler_id, approved=True);
	if(len(response) > 0):
		s += b64(response[0].name) + "," + b64(response[0].class_name) + "," + b64(response[0].code)
	
	return HttpResponse(s)
	
@login_required
def api_get_results(request, testset_id, scheduler_id):
	"""
	Gets the result ids corresponding to the given testset and scheduler.
	"""
	reponse = None
	s = ""
	
	response = Results.objects.filter(
		test_set__id__exact=testset_id, 
		scheduling_policy__id__exact=scheduler_id, 
		approved=True)
		
	for res in response:
		s += str(res.id) + ","
	
	return HttpResponse(s.rstrip(','))


@login_required
def api_get_result(request, result_id):
	"""
	Gets the result associated to the given result_id.
	Gives testset_id and scheduler_id first, then all metrics.
	"""
	response = None
	s = ""
	response = Results.objects.filter(pk=result_id, approved=True)
	
	attrs = ['name', 'count', 'avg', 'std', 'median', 'minimum', 'maximum']
	
	if response.count() > 0:
		res = response[0]
		s += str(res.test_set.id) + ","
		s += str(res.scheduling_policy.id) + ","
		for metric in res.metrics.all():
			for attr in attrs:
				s += b64(str(getattr(metric, attr))) + ","
			
	
	return HttpResponse(s.rstrip(','))


	
@login_required
def api_get_scheduler_by_name(request, name):
	"""
	Gets the scheduler(s) corresponding to the given name.
	
	:param name: scheduler name.
	"""
	response = get_schedulers_by_name(name, True)
	
	if response.count() == 0:
		return HttpResponse("")

	return HttpResponse(str(response[0].id));

@login_required
def api_get_testsets(request, category):
	"""
	Gets a tuple (id, name) for each test in the database matching
	the given category. (if category = None, gives all tests)
	
	:param category: Base64 encoded category name.
	"""
	response = None
	category = str(decode_base64(category))
	
	if(category == ""):
		response = TestSet.objects.all()
	else:
		response = TestSet.objects.filter(categories__name__contains=category)
	
	response = response.filter(approved=True)
	
	s = "";
	for testset in response:
		s += b64(str(testset.id)) + "," + b64(testset.name) + ","
	
	return HttpResponse(s.rstrip(','))


def testset2str(testset):
	s = b64(testset.name) + "," + b64(testset.description) + ","
	s += str(testset.categories.count()) + ","
	for cat in testset.categories.all():
		s += b64(cat.name) + ","
	s += str(testset.files.count()) + ","
	for f in testset.files.all():
		s += str(f.id) + ","
	return s
	
@login_required
def api_get_testset_by_id(request, identifier):
	"""
	Gets a tuple (name, description, categoryCount, category1, category2, fileCount, file1, ...)
	for the testset with the given id.
	"""
	response = TestSet.objects.filter(pk=identifier, approved=True)
	if response.count() == 0:
		return HttpResponse("")
	
	testset = response[0]
	s = testset2str(testset)
	return HttpResponse(s)
	
@login_required
def api_get_testset_by_name(request, name):
	"""
	Gets the id of the testset with the given name if it exists.
	for the testset with the given name
	"""
	response = TestSet.objects.filter(name=name, approved=True)
	if response.count() == 0:
		return HttpResponse("")
	
	s = str(response[0].id)
	
	return HttpResponse(s)
	
@login_required
def api_get_test_files(self, testset_id):
	"""
	Gets a list of XML configuration files ids for the given test set id.
	
	:param testset_id: ID of the test set.
	"""
	response = None
	if(testset_id == ""):
		response = ConfigurationFile.objects.all()
	else:
		response = ConfigurationFile.objects.filter(testset__id=testset_id);
	
	s = ""
	if response.count() > 0:
		for conffile in response:
			identifier = str(conffile.id)
			s += identifier+","
	
	return HttpResponse(s.rstrip(','))

@login_required
def api_get_conf_file(self, file_id):
	"""
	Gets a tuple (name, content) for the configuration file with the given id.
	"""
	response = ConfigurationFile.objects.filter(pk=file_id)
	s = ""
	if response.count() > 0:
		s = response[0].conf
	
	return HttpResponse(s)

@login_required
def api_get_categories(self):
	"""
	Gets a list of all the categories.
	"""
	response = TestCategory.objects.all()
	s = ""
	for cat in response:
		s += b64(cat.name) + "," + b64(cat.description) + ","
	
	return HttpResponse(s.rstrip(','))