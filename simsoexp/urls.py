from django.conf.urls import url
from . import views

urlpatterns = [
	url('^$', views.index, name='index'),
	url('^api/testsets/(.*)$', views.api_get_testsets, name='testsets'),
	url('^api/conffiles/([0-9]*)$', views.api_get_conf_files, name='conffiles'),
	url('^api/schedulers/sha/(.*)$', views.api_get_schedulers_by_sha, name='schedulers_sha'),
	url('^api/schedulers/name/(.*)$', views.api_get_schedulers_by_name, name='schedulers_name'),
	url('^api/metrics/([0-9]*)/([0-9]*)$', views.api_get_metrics, name='metrics'),
	url('^api/schedulers/code/([0-9]*)$', views.api_get_scheduler_code, name="schedulers_code")
]