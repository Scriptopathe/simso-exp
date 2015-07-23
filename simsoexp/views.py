from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import logout as user_logout
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
import hashlib
import base64
from math import ceil
from models import *

def decode_base64(data):
    """Decode base64, padding being optional.

    :param data: Base64 data as an ASCII byte string
    """
    missing_padding = 4 - len(data) % 4
    if missing_padding:
        data += b'='* missing_padding
    return base64.decodestring(data)

def b64(data):
	return base64.b64encode(data)
	
def paginate(requestFunction, page, pageSize=10, dispPages=5):
	"""
	Given a requesr function, a page number and a page size, 
	returns a tuple (count, page, start, end, items, pagesDisp, pagesCount)
	"""
	itemCount = requestFunction().count()
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
	
	return (itemCount, page, start, end, requestFunction()[start:end], pagesDisp, pagesCount)
	
def logout(request):
	"""Logs out the user"""
	user_logout(request)
	return redirect(auth_views.login)


@login_required
def contributions(request):
	"""
	View where an user can see his contributions (validated or not validated
	"""
	template = loader.get_template('contributions.html')
	name = request.user.username + ".schedulers.";
	context = RequestContext(request, {
		'scheds' : SchedulingPolicy.objects.filter(contributor=request.user)
	})
	return HttpResponse(template.render(context))

@user_passes_test(lambda u: u.is_superuser)
def manage_validation(request):
	"""
	View where the admins can validate database entries.
	"""
	template = loader.get_template('manage_validation.html')
	context = RequestContext(request, {
		'scheds' : get_schedulers_by_name("", False),
	})
	return HttpResponse(template.render(context))

@user_passes_test(lambda u: u.is_superuser)
def scheduler_validation_action(request):
	"""
	View which only removes / validates schedulers.
	"""
	action = request.GET['action']
	identifier = request.GET['id']
	objs = SchedulingPolicy.objects.filter(pk=int(identifier))
	if len(objs) == 0:
		return HttpResponse("error:bad id")
	sched = objs[0]
	
	if action == "delete":
		reason = request.GET['reason']
		notif = Notification()
		notif.title = "Submission of scheduler " + sched.name + " refused."
		notif.user = request.user
		notif.content = reason
		notif.save()
		#sched.delete()
		return HttpResponse("success")
	elif action == "validate":
		sched.approved = True
		sched.save()
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
		req = lambda: Notification.objects.filter(user=request.user, read=False)
	else:
		req = lambda: Notification.objects.filter(user=request.user)
		
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
	
	validated = get_schedulers_by_name(name, True)
	
	# If a validated scheduler with the same name exists,
	# throws an error.
	if(len(validated) > 0):
		return HttpResponse("error:name")
	
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
	sched.class_name = class_name
	sched.code = code
	sched.sha1 = hashlib.sha1(code).hexdigest()
	sched.save()
	return HttpResponse(ret_code)


@login_required
def index(request):
	template = loader.get_template('app.html')
	context = RequestContext(request, {
	})
	return HttpResponse(template.render(context))




@login_required
def api_get_schedulers_by_sha(request, sha):
	"""
	Gets the scheduler(s) corresponding to the given sha1 hex hash.
	"""
	response = None
	if(sha == ""):
		response = SchedulingPolicy.objects.all()
	else:
		response = SchedulingPolicy.objects.filter(sha1__exact=sha)
	
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
	
	response = SchedulingPolicy.objects.filter(id__exact=scheduler_id);
	if(len(response) > 0):
		s += b64(response[0].name) + "," + b64(response[0].class_name) + "," + b64(response[0].code)
	
	return HttpResponse(s)
	
@login_required
def api_get_metrics(request, testset_id, scheduler_id):
	"""
	Gets the metrics ids corresponding to the given testset and scheduler.
	"""
	reponse = None
	s = ""
	
	response = Results.objects.filter(
		test_set__id__exact=testset_id, 
		scheduling_policy__id__exact=scheduler_id)
		
	for res in response:
		s += str(res.id) + ","
	
	return HttpResponse(s.rstrip(','))


@login_required
def api_get_metric(request, metric_id):
	"""
	Gets all the metrics associated to the given metric_id.
	Gives testset_id and scheduler_id first, then key values in the following format :
		base64(key),base64(value)
	"""
	response = None
	s = ""
	response = Results.objects.filter(pk=metric_id)
	
	all_metrics = ['preemptions', 'sys_preempt', 
		'migrations', 'task_migrations', 'norm_laxity',
		'on_schedule', 'timers', 'aborted_jobs', 'jobs']
	
	
	if(len(response) > 0):
		res = response[0]
		s += str(res.test_set.id) + ","
		s += str(res.scheduling_policy.id) + ","
		for metric in all_metrics:
			s += b64(metric) + "," + b64(str(getattr(res, metric))) + ","
	
	return HttpResponse(s.rstrip(','))

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
	
@login_required
def api_get_schedulers_by_name(request, name):
	"""
	Gets the scheduler(s) corresponding to the given name.
	
	:param name: Base 64 encoded scheduler name.
	"""
	name = str(decode_base64(name))
	
	response = get_schedulers_by_name(name, True)
	
	s = ""
	for sched in response:
		s += unicode(sched.id) + ","
	
	return HttpResponse(s.rstrip(','));

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
	
	s = "";
	for testset in response:
		s += b64(str(testset.id)) + "," + b64(testset.name) + ","
	
	return HttpResponse(s.rstrip(','))
	
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
	if(len(response) > 0):
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
	if len(response) > 0:
		name = b64(response[0].name)
		content = b64(response[0].conf)
		s = name + "," + content
	
	return HttpResponse(s)