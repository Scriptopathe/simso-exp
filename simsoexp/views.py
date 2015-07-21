from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as user_logout
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views

import base64
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

def logout(request):
	"""Logs out the user"""
	user_logout(request)
	return redirect(auth_views.login)

def index(request):
	template = loader.get_template('simsoexp/index.html')
	context = RequestContext(request, {
		'test' : 'this is a string variable'
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

@login_required
def api_get_schedulers_by_name(request, name):
	"""
	Gets the scheduler(s) corresponding to the given name.
	
	:param name: Base 64 encoded scheduler name.
	"""
	response = None
	name = str(decode_base64(name))
	
	if(name == ""):
		response = SchedulingPolicy.objects.all()
	else:
		response = SchedulingPolicy.objects.filter(name__exact=name)
	
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