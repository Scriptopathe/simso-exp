from django.db import models
import pickle

# Create your models here.
class ConfigurationFile(models.Model):
	# Name of the configuration file.
	name = models.CharField(max_length=255)
	# Pickled conf object
	conf = models.TextField()
	
	def get_conf(self):
		return pickle.loads(self.conf)
	
	def set_conf(self, conf):
		self.conf = pickle.dumps(conf)
	
class TestSet(models.Model):
	# Name of the test set. It does not have to be unique.
	name = models.CharField(max_length=255)
	# Files contained in the test set
	files = models.ManyToManyField(ConfigurationFile)
	
class SchedulingPolicy(models.Model):
	# Name of the policy. Is does not have to be unique
	name = models.CharField(max_length=255)
	# Text of the code
	code = models.TextField()
	# Sha1 hash of the code
	sha1 = models.TextField()
	# MD5 hash of the code
	md5 = models.TextField()
	
class Results(models.Model):
	# Pickled python object containing the metrics
	metrics = models.TextField()
	# The scheduling policy used to get those results.
	scheduling_policy = models.ForeignKey(SchedulingPolicy)
	# The test set used to get those results.
	test_set = models.ForeignKey(TestSet)
	
	def get_metrics(self):
		return pickle.loads(self.metrics)
	
	def set_metrics(self, metrics):
		self.metrics = pickle.dumps(conf)
	
