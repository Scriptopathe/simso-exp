from django.conf.urls import url
from . import views

urlpatterns = [
	url('^$', views.index, name='index'),
	url('^api/testsets/(.*)$', views.api_get_testsets, name='testsets'),
	url('^api/conffiles/(.*)$', views.api_get_conf_files, name='conffiles')
	
]