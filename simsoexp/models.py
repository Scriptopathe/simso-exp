from django.db import models
import pickle

# Create your models here.
class ConfigurationFile(models.Model):
	# Name of the configuration file.
	name = models.CharField(max_length=255)
	# XML conf file
	conf = models.TextField()
	
	def __str__(self):
		return self.name

class TestCategory(models.Model):
	# Name of the test category
	name = models.CharField(max_length=255)
	# Description of the test category
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
	
	def __str__(self):
		return self.name
	
class SchedulingPolicy(models.Model):
	# Name of the policy. Is does not have to be unique
	name = models.CharField(max_length=255)
	# Text of the code
	code = models.TextField()
	# Sha1 hash of the code
	sha1 = models.TextField()
	# MD5 hash of the code
	md5 = models.TextField()
	
	def __str__(self):
		return self.name
	
class Results(models.Model):
	# XML file containing the metrics
	metrics = models.TextField()
	# The scheduling policy used to get those results.
	scheduling_policy = models.ForeignKey(SchedulingPolicy)
	# The test set used to get those results.
	test_set = models.ForeignKey(TestSet)
	
	def get_metrics(self):
		return pickle.loads(self.metrics)
	
	def set_metrics(self, metrics):
		self.metrics = pickle.dumps(conf)
		
	def __str__(self):
		return "Result of testset '" + self.test_set.name + \
			"' with scheduling policy '" + self.scheduling_policy.name + "'";
	
