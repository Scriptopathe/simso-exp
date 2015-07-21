# This file contains high-level api designed to work with simso
import sys
from .api import Api
from simso.configuration import Configuration
import os

class DBMetrics:
	def __init__(self, db, identifier):
		self.db = db
		self.identifier = identifier
		self.__testset_id = None
		self.__scheduler_id = None
		self.__metrics = None
		if db.preload:
			self.__load_metrics()
	
	def __load_metrics(self):
		m = self.db.api.get_metric(self.identifier)
		self.__testset_id = m[0]
		self.__scheduler_id = m[1]
		self.__metrics = m[2]

	@property	
	def testset_id(self):
		"""Gets the id of the test set associated with these metrics"""
		if self.__testset_id == None:
			self.__load_metrics()
		return self.__testset_id
	
	@property
	def scheduler_id(self):
		"""
		Gets the id of the scheduler associated with these metrics
		"""
		if self.__scheduler_id == None:
			self.__load_metrics()
		return self.__scheduler_id
	
	def __getitem__(self, index):
		"""
		Gets the metric with the given name.
		Available metrics are : 
			preemptions
			sys_preempt
			migrations
			task_migrations
			norm_laxity
			on_schedule
			timers
			aborted_jobs
			jobs
		"""
		if self.__metrics == None:
			self.__load_metrics()
		
		return self.__metrics[index]
	
	def all(self):
		"""Returns all the set of metrics"""
		return self.__metrics
	
	def __repr__(self):
		return "<DBMetrics id={} testset={} scheduler={}>".format(
			self.identifier, self.testset_id, self.scheduler_id
		)
		
class DBTestSet:
	def __init__(self, db, identifier):
		self.db = db
		self.identifier = identifier
		self.__conf_files = None
		if db.preload:
			self.__load_conf_files()
		
	def __load_conf_files(self):
		files = self.db.api.get_testset_files(self.identifier);
		self.__conf_files = [DBConfFile(self.db, self, f) for f in files]
	
	@property
	def conf_files(self):
		"""Gets a list of tuples DBConfFile object for each
		configuration file in this test set"""
		if self.__conf_files == None:
			self.__load_conf_files()
		return self.__conf_files
	
	def __repr__(self):
		return "<DBTestSet id={}>".format(self.identifier)

class DBConfFile:
	def __init__(self, db, testset, identifier):
		self.db = db
		self.identifier = identifier
		self.testset = testset
		self.__name = None
		self.__content = None
		self.__configuration = None
	
	def __load_data(self):
		data = self.db.api.get_conf_file(self.identifier)
		self.__name, self.__content = data
		
	def __load_configuration(self):
		directory = self.db.local_conf_dir + "/testset_" + str(self.testset.identifier);
		if not os.path.exists(directory):
			os.makedirs(directory)
		filename = directory + "/" + str(self.identifier) + ".xml";
		
		# Writes the configuration to a file
		f = open(filename, 'w+')
		f.write(self.content)
		f.close()
		
		# Loads it
		self.__configuration = Configuration(filename)
	
	@property
	def name(self):
		"""
		Gets this configuration file's name
		"""
		if self.__name == None:
			self.__load_data()
		return self.__name
	
	@property
	def content(self):
		"""
		Gets this configuration file's content as a string.
		"""
		if self.__content == None:
			self.__load_data()
		return self.__content
	
	@property
	def configuration(self):
		"""
		Gets the Simso configuration object represented by this configuration file
		"""
		if self.__configuration == None:
			self.__load_configuration()
		return self.__configuration
		
	def __repr__(self):
		return "<DBConfFile id={} name={}>".format(self.identifier, self.name)
		
class DBScheduler:
	def __init__(self, db, identifier):
		self.db = db
		self.identifier = identifier
		self.__code = None
		self.__name = None
		self.__class_name = None
		self.__cls = None
		if db.preload:
			self.__load_data()
	
	def __load_data(self):
		data = self.db.api.get_scheduler_data(self.identifier)
		self.__name, self.__class_name, self.__code = data
	
	def __load_cls(self):
		# Executes the class code in the ns namespace.
		ns = {}
		exec(self.code, ns)
		self.__cls = ns[self.class_name]
	
	@property
	def cls(self):
		"""
		Gets the scheduler's class object.
		"""
		if(self.__cls == None):
			self.__load_cls()
		return self.__cls
		
	@property
	def code(self):
		"""Gets this scheduler's code"""
		if self.__code == None:
			self.__load_data()
		return self.__code
	
	@property
	def name(self):
		"""Gets this scheduler visible name"""
		if self.__name == None:
			self.__load_data()
		return self.__name
	
	@property
	def class_name(self):
		"""Gets the scheduler's main class in the scheduler's code"""
		if self.__class_name == None:
			self.__load_data()
		return self.__class_name
	
	def __repr__(self):
		return "<DBScheduler id={} name={} class_name={}>".format(self.identifier, self.name, self.class_name)

class SimsoDatabase:
	def __init__(self, address):
		"""
		Initializes a connection to the Simso Experiment server
		at the given address (includes port number)
		Ex: http://example.com:8000/
		"""
		self.base_addr = address.rstrip('/');
		self.api = Api(address)
		self.preload = False
		self.__init_cache()
		
	def __init_cache(self):
		self.local_cache_dir = os.path.expanduser("~") + "/.simsoexpcache"
		self.local_conf_dir = self.local_cache_dir + "/configurations"
		if not os.path.exists(self.local_cache_dir):
			os.makedirs(self.local_cache_dir)
			os.makedirs(self.local_conf_dir)
		
	def testset(self, identifier):
		"""Gets a testset given its id."""
		return DBTestSet(self, identifier)
	
	def scheduler(self, identifier):
		return DBScheduler(self, identifier)
	
	def metrics(self, testset_id, scheduler_id):
		m = self.api.get_metrics(testset_id, scheduler_id)
		return [DBMetrics(self, identifier) for identifier in m]
		
	def testsets(self, category=""):
		"""Gets a list of testset given a category"""
		sets = self.api.get_testsets_by_category(category)
		tests = [DBTestSet(self, identifier) for identifier, name in sets]
		return tests
	
	def schedulers(self, name=""):
		"""
		Gets a list of DBScheduler objects matching the given name
		Usually there is only one matching result.
		"""
		scheds = self.api.get_schedulers_by_name(name)
		scheds = [DBScheduler(self, sched_id) for sched_id in scheds]
		return scheds