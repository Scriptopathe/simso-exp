from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
import base64
from models import *

def decode_base64(data):
    """Decode base64, padding being optional.

    :param data: Base64 data as an ASCII byte string
    :returns: The decoded byte string.

    """
    missing_padding = 4 - len(data) % 4
    if missing_padding:
        data += b'='* missing_padding
    return base64.decodestring(data)
	
def index(request):
	template = loader.get_template('simsoexp/index.html')
	context = RequestContext(request, {
		'test' : 'this is a string variable'
	})
	return HttpResponse(template.render(context))


def api_get_testsets(request, category):
	"""Gets a tuple (id, name) for each test in the database matching
	the given category. (if category = None, gives all tests)"""
	response = None
	category = str(decode_base64(category))
	
	if(category == "all"):
		response = TestSet.objects.all()
	else:
		response = TestSet.objects.filter(categories__name__contains=category)
	
	s = "";
	for testset in response:
		s += base64.b64encode(str(testset.id)) + "," + base64.b64encode(testset.name) + ","
	
	return HttpResponse(s)
	
def api_get_conf_files(self, testset_id):
	"""Gets a list of XML configuration files for the given test set id"""
	response = ConfigurationFile.objects.filter(testset__id=testset_id);
	s = ""
	if(len(response) > 0):
		for conffile in response:
			name = base64.b64encode(conffile.name)
			filecontent = base64.b64encode(conffile.conf)
			s += name+","+filecontent+","
	
	return HttpResponse(s)
	
	
	