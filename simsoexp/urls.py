from django.conf.urls import url
from . import views

urlpatterns = [
	url('^$', views.index, name='index'),
	url('^validation/action/$', views.scheduler_validation_action, name="scheduler_validation_action"),
	url('^validation/$', views.manage_validation, name="manage_validation"),
	url('^api/testsets/(.*)$', views.api_get_testsets, name='testsets'),
	url('^api/testfiles/([0-9]*)$', views.api_get_test_files, name='testfiles'),
	url('^api/conf_file/([0-9]*)$', views.api_get_conf_file, name='conf_file'),
	url('^api/schedulers/upload/', views.upload_scheduler, name='scheduler_upload'),
	url('^api/schedulers/sha/(.*)$', views.api_get_schedulers_by_sha, name='schedulers_sha'),
	url('^api/schedulers/name/(.*)$', views.api_get_schedulers_by_name, name='schedulers_name'),
	url('^api/metrics/id/([0-9]*)$', views.api_get_metric, name='metrics_by_id'),
	url('^api/metrics/([0-9]*)/([0-9]*)$', views.api_get_metrics, name='metrics'),
	url('^api/schedulers/data/([0-9]*)$', views.api_get_scheduler_data, name="schedulers_code"),
	url('^logout$', views.logout, name="logout")
]