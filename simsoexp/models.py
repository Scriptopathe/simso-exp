from django.db import models
from django.contrib.auth.models import User
import pickle

class Notification(models.Model):
	# The notification's title
	title = models.TextField()
	# The notification's description
	content = models.TextField()
	# The destination user of the notification.
	user = models.ForeignKey(User)
	# Indicates if this notification has been read.
	read = models.BooleanField(default=False)
	# Notification type (danger, success, warning) :
	ntype = models.CharField(max_length=255)
	
class ConfigurationFile(models.Model):
	# XML conf file
	conf = models.TextField()
	# True if approved by the admin
	approved = models.BooleanField(default=False)
	
	def __str__(self):
		return self.name

class TestCategory(models.Model):
	# Name of the test category
	name = models.CharField(max_length=255)
	# Description of the test category
	approved = models.BooleanField(default=False)
	
	def __str__(self):
		return self.name
	
class TestSet(models.Model):
	# Name of the test set. It does not have to be unique.
	name = models.CharField(max_length=255)
	# Files contained in the test set
	files = models.ManyToManyField(ConfigurationFile)
	# All the categories labels of this test set.
	categories = models.ManyToManyField(TestCategory)
	# True if approved by the admin
	approved = models.BooleanField(default=False)
	
	def __str__(self):
		return self.name
	
class SchedulingPolicy(models.Model):
	# Name of the policy. Is does not have to be unique
	name = models.CharField(max_length=255)
	# Text of the code
	code = models.TextField()
	# Sha1 hash of the code
	sha1 = models.TextField()
	# Class name of the Scheduler in the script
	class_name = models.TextField()
	# True if approved by the admin
	approved = models.BooleanField(default=False)
	# Contributor
	contributor = models.ForeignKey(User)
	
	def __str__(self):
		return self.name
	
class Results(models.Model):
	# The scheduling policy used to get those results.
	scheduling_policy = models.ForeignKey(SchedulingPolicy)
	# The test set used to get those results.
	test_set = models.ForeignKey(TestSet)
	# True if approved by the admin
	approved = models.BooleanField(default=False)
	
	# Metrics
	preemptions = models.IntegerField()
	sys_preempt = models.IntegerField()
	migrations = models.IntegerField()
	task_migrations = models.IntegerField()
	norm_laxity = models.IntegerField()
	on_schedule = models.IntegerField()
	timers = models.IntegerField()
	aborted_jobs = models.IntegerField()
	jobs = models.IntegerField()

	def __str__(self):
		return "Result of testset '" + self.test_set.name + \
			"' with scheduling policy '" + self.scheduling_policy.name + "'";
	
