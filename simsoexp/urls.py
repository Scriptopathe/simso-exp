from django.conf.urls import url
from . import views

urlpatterns = [
	url('^$', views.index, name='index'),
	url('^view/scheduler/([0-9]*)$', views.view_scheduler, name="view_scheduler"),
	url('^view/testset/([0-9]*)$', views.view_testset, name="view_testset"),
	url('^notifications/$', views.notifications, name="notifications"),
	url('^contributions/$', views.contributions, name="contributions"),
	url('^account/settings/$', views.account_settings, name="account_settings"),
	url('^categories/$', views.categories, name="categories"),
	# 'Ajax' views
	url('^account/settings/save/$', views.post_account_settings, name="post_account_settings"),
	url('^upload/scheduler$', views.scheduler_upload_form, name='scheduler_upload_form'),
	url('^categories/description/([0-9]*)$', views.post_category_description, name="post_category_description"),
	url('^validation/action/$', views.validation_action, name="validation_action"),
	url('^category/add/$', views.add_category, name="add_category"),
	url('^notifications/read/$', views.user_read_notification, name="notifications_read"),
	url('^notifications/unread_count$', views.unread_notifications_count, name="notifications_count"),
	# Download views
	url('^download/scheduler/([0-9]*)$', views.download_scheduler, name="view_scheduler"),
	url('^download/testset/([0-9]*)$', views.download_testset, name="download_testset"),
	# API views
	url('^api/categories/$', views.api_get_categories, name='categories'),
	url('^api/testsets/category/(.*)$', views.api_get_testsets, name='testsets'),
	url('^api/testsets/name/([\w|\.]*)$', views.api_get_testset_by_name, name='testsets_name'),
	url('^api/testsets/id/([0-9]*)$', views.api_get_testset_by_id, name='testsets_id'),
	url('^api/testfiles/([0-9]*)$', views.api_get_test_files, name='testfiles'),
	url('^api/conf_file/([0-9]*)$', views.api_get_conf_file, name='conf_file'),
	url('^api/schedulers/upload/', views.upload_scheduler, name='scheduler_upload'),
	url('^api/schedulers/sha/(.*)$', views.api_get_schedulers_by_sha, name='schedulers_sha'),
	url('^api/schedulers/name/([\w|\.]*)$', views.api_get_scheduler_by_name, name='schedulers_name'),
	url('^api/results/id/([0-9]*)$', views.api_get_result, name='metrics_by_id'),
	url('^api/results/([0-9]*)/([0-9]*)$', views.api_get_results, name='metrics'),
	url('^api/schedulers/data/([0-9]*)$', views.api_get_scheduler_data, name="schedulers_code"),
	url('^api/experiment/upload$', views.api_upload_experiment, name="api_upload_experiment"),
	url('^api/testsets/upload$', views.api_upload_testset, name="api_upload_testset"),
	
	url('^logout$', views.logout, name="logout")
]