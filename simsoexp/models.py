from django.db import models
from django.contrib.auth.models import User
import pickle

class UserSettings(models.Model):
	# User to whom the settings are bound.
	user = models.OneToOneField(User, related_name="settings",on_delete=models.CASCADE)
	
	# Mail notifications
	enable_mail_notifications = models.BooleanField(default=True)

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
	
	def __str__(self):
		return "Conf " + str(self.id)

class TestCategory(models.Model):
	# Name of the test category
	name = models.CharField(max_length=255)
	# Description of the category
	description = models.TextField()
	
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
	# Contributor
	contributor = models.ForeignKey(User)
	# Description of the category
	description = models.TextField()
	def categories_str(self):
		return ','.join([cat.name for cat in self.categories.all()])
	
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

class Metric(models.Model):
	# Name of the metric
	name = models.TextField()
	# Sum of the values of the metric
	count = models.FloatField()
	# Average value of the metric
	avg = models.FloatField()
	# Standard deviation of the metric
	std = models.FloatField()
	# Median of the metric
	median = models.FloatField()
	# Minimum value of the metric
	minimum = models.FloatField()
	# Maximum value of the metric
	maximum = models.FloatField()
	
	def __str__(self):
		return "{} : sum={}, avg={}, std={}, median={}, min={}, max={}".format(self.name, 
			self.count, self.avg, self.std, self.median, self.minimum, self.maximum)
		
	

class Results(models.Model):
	# The scheduling policy used to get those results.
	scheduling_policy = models.ForeignKey(SchedulingPolicy)
	# The test set used to get those results.
	test_set = models.ForeignKey(TestSet)
	# User that submitted the results
	contributor = models.ForeignKey(User)
	# True if approved by the admin
	approved = models.BooleanField(default=False)
	# Metrics
	metrics = models.ManyToManyField(Metric)
	
	@property
	def name(self):
		return str(self)
		
	def __str__(self):
		return "Result of testset '" + self.test_set.name + \
			"' with scheduling policy '" + self.scheduling_policy.name + "'";
	
