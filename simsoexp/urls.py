from django.conf.urls import url
from . import views

urlpatterns = [
	url('^$', views.index, name='index'),
	url('^validation/action/$', views.validation_action, name="validation_action"),
	url('^notifications/$', views.notifications, name="notifications"),
	url('^notifications/read/$', views.user_read_notification, name="notifications_read"),
	url('^notifications/unread_count$', views.unread_notifications_count, name="notifications_count"),
	url('^contributions/$', views.contributions, name="contributions"),
	url('^api/testsets/category/(.*)$', views.api_get_testsets, name='testsets'),
	url('^api/testsets/id/([0-9]*)$', views.api_get_testsets_by_id, name='testsets_id'),
	url('^api/testfiles/([0-9]*)$', views.api_get_test_files, name='testfiles'),
	url('^api/conf_file/([0-9]*)$', views.api_get_conf_file, name='conf_file'),
	url('^api/schedulers/upload/', views.upload_scheduler, name='scheduler_upload'),
	url('^api/schedulers/sha/(.*)$', views.api_get_schedulers_by_sha, name='schedulers_sha'),
	url('^api/schedulers/name/(.*)$', views.api_get_schedulers_by_name, name='schedulers_name'),
	url('^api/results/id/([0-9]*)$', views.api_get_result, name='metrics_by_id'),
	url('^api/results/([0-9]*)/([0-9]*)$', views.api_get_results, name='metrics'),
	url('^api/schedulers/data/([0-9]*)$', views.api_get_scheduler_data, name="schedulers_code"),
	url('^api/experiment/upload$', views.api_upload_experiment, name="api_upload_experiment"),
	
	url('^logout$', views.logout, name="logout")
]