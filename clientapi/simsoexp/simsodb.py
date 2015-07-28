# This file contains high-level api designed to work with simso
import sys
from .api import Api
from .metrics_collector import MetricsCollector
from simso.core import Model
from simso.configuration import Configuration
from simso.configuration.GenerateConfiguration import generate
import numpy
import os

class DBResults:
	def __init__(self, db, identifier):
		self.db = db
		self.identifier = identifier
		self.__testset_id = None
		self.__scheduler_id = None
		self.__metrics = None
		if db.preload:
			self.__load_metrics()
	
	def __load_metrics(self):
		m = self.db.api.get_result(self.identifier)
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
		"""
		if self.__metrics == None:
			self.__load_metrics()
		
		return self.__metrics[index]
	
	def all(self):
		"""Returns all the set of metrics"""
		if self.__metrics == None:
			self.__load_metrics()
			
		return self.__metrics
	
	def __repr__(self):
		return "<DBResults id={} testset={} scheduler={}>".format(
			self.identifier, self.testset_id, self.scheduler_id
		)
	
class DBTestSet:
	def __init__(self, db, identifier):
		self.db = db
		self.identifier = identifier
		self.__conf_files = None
		self.__name = None
		self.__description = None
		self.__categories = None
		if db.preload:
			self.__load_conf_files()
	
	def __load_data(self):
		name, description, categories, fileIds = self.db.api.get_testset(self.identifier)
		self.__categories = categories
		self.__name = name
		self.__description = description
		
	def __load_conf_files(self):
		files = self.db.api.get_testset_files(self.identifier);
		self.__conf_files = [DBConfFile(self.db, self, f) for f in files]
	
	@property
	def name(self):
		"""
		Gets the name of the test set
		"""
		if self.__name == None:
			self.__load_data()
		return self.__name
	
	@property
	def description(self):
		"""
		Gets the description of the test set.
		"""
		if self.__description == None:
			self.__load_data()
		return self.__description
	
	@property
	def categories(self):
		"""
		Gets this test set's categories
		"""
		if self.__categories == None:
			self.__load_data()
		return self.__categories
	
	@property
	def conf_files(self):
		"""Gets a list of tuples DBConfFile object for each
		configuration file in this test set"""
		if self.__conf_files == None:
			self.__load_conf_files()
		return self.__conf_files
	
	def __repr__(self):
		return "<DBTestSet id={}, name={}>".format(self.identifier, self.name)

class DBConfFile:
	def __init__(self, db, testset, identifier):
		self.db = db
		self.identifier = identifier
		self.testset = testset
		self.__content = None
		self.__configuration = None
	
	def __load_data(self):
		self.__content = self.db.api.get_conf_file(self.identifier)
		
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
		return "<DBConfFile id={}>".format(self.identifier)
		
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


		
class Experiment:
	"""
	Represent an experiment, which contains :
		- a set of configuration files
		- a scheduler
		- after run() : a set of metrics and results
	"""
	def __init__(self, db, conf_files, scheduler):
		"""
		Creates a new experiment
		
		:param db: The database instance bound to the experiment.
		:conf_files: Either a DBTestSet object or a a custom test set given as a 
		tuple (name, description, categories, list of Configuration objects), or
		a list of Configuration objects.
		
		
		Take care : you won't be able to upload your results if you used a custom test set,
		unless you are a Simso Experiment Database administrator.
		"""
		self.db = db
		self.results = []
		# Checks conf_files
		if isinstance(conf_files, DBTestSet):
			self.testset = conf_files
			self.testname = self.testset.name
			self.testdesc = self.testset.description
			self.conf_files = [f.configuration for f in conf_files.conf_files]
			self.categories = self.testset.categories
		elif isinstance(conf_files, list):
			for f in conf_files:
				assert(isinstance(f, Configuration))
			self.conf_files = conf_files
			self.testset = None
			self.testname = None
			self.testdesc = None
			self.categories = None
		else:
			assert(isinstance(conf_files, tuple))
			assert(isinstance(conf_files[0], str))
			assert(isinstance(conf_files[1], str))
			assert(isinstance(conf_files[2], list))
			assert(isinstance(conf_files[3], list))
			
			# Check categories
			for c in conf_files[2]:
				assert(isinstance(c, str))
			
			# Check files	
			for f in conf_files[3]:
				assert(isinstance(f, Configuration))
			
			self.testset = None
			self.testname = conf_files[0]
			self.testdesc = conf_files[1]
			self.categories = conf_files[2]
			self.conf_files = conf_files[3]
			
		# Check scheduler
		assert(isinstance(scheduler, DBScheduler))
		self.scheduler = scheduler
		
		self.metrics = {}

	
	def run(self):
		"""
		Runs the experiment and computes the metrics.
		"""
		
		self.results = []
		all_results = []
		for configuration in self.conf_files:
			model = Model(configuration)
			model.run_model()
			self.results.append(model.results)
			all_results.append(MetricsCollector(model.results))
		
		
		self.metrics = {} # sum, avg, std, med, min, max
		metric_keys = [key for key in all_results[0].metrics]
		for key in metric_keys:
			values = [res.metrics[key] for res in all_results]
			self.metrics[key] = [
				sum(values),
				numpy.average(values),
				numpy.std(values),
				numpy.median(values),
				min(values),
				max(values)
			]
		
	def upload(self):
		"""
		Uploads the experiment to Simso Experiment Database.
		
		Take care : you won't be able to upload your results if you used a custom test set,
		unless you are a Simso Experiment Database administrator.
		"""
		data = {}
		
		# Metrics
		data["metrics"] = []
		for metric in self.metrics:
			data["metrics"].append(','.join([metric] + [str(m) for m in self.metrics[metric]]))
		
		# Configuration files / testset
		if(self.testset == None):
			data["testset_id"] = "-1"
			data["conf_files"] = [generate(f) for f in self.conf_files]
		else:
			data["testset_id"] = str(self.testset.identifier)
			data["conf_files"] = []
		
		# Check integrity
		if self.testname == None or self.testdesc == None or self.categories == None:
			raise Exception("Cannot upload a testset with no metadata.")
		
		# Test name and description
		data["test_name"] = self.testname
		data["test_description"] = self.testdesc
		
		# Categories
		data["categories"] = self.categories
		
		# Scheduler
		data["scheduler"] = self.scheduler.identifier
		
		self.db.api.upload_experiment(data)
		
class SimsoDatabase:
	def __init__(self, address, username=None, password=None):
		"""
		Initializes a connection to the Simso Experiment server
		at the given address (includes port number)
		Ex: http://example.com:8000/
		"""
		self.base_addr = address.rstrip('/');
		self.api = Api(address, username, password)
		self.preload = False
		self.__init_cache()
		
	def __init_cache(self):
		self.local_cache_dir = os.path.expanduser("~") + "/.simsoexpcache"
		self.local_conf_dir = self.local_cache_dir + "/configurations"
		if not os.path.exists(self.local_cache_dir):
			os.makedirs(self.local_cache_dir)
			os.makedirs(self.local_conf_dir)
		
	def testset(self, identifier):
		"""Gets a testset given its id in the database."""
		return DBTestSet(self, identifier)
	
	def testset_by_name(self, name):
		"""Gets a testset given its name in the database"""
		identifier = self.api.get_testset_by_name(name)
		return DBTestSet(self, identifier)
	
	def results(self, testset, scheduler):
		"""
		Gets the results associated to the given testset and scheduler_.
		These results have been obtained by running simso with the corresponding
		scheduler and testsets.
		
		:param testset: A DBTestSet instance.
		:param scheduler: A DBScheduler instance.
		"""
		assert(isinstance(testset, DBTestSet))
		assert(isinstance(scheduler, DBScheduler))
		
		m = self.api.get_results(testset.identifier, scheduler.identifier)
		return [DBResults(self, identifier) for identifier in m]
	
	def result(self, identifier):
		"""
		Gets a result set given its identifier in the database.
		"""
		return DBResults(self, identifier)
		
	def categories(self):
		"""
		Gets a list of all the test categories
		"""
		return [cat[0] for cat in self.api.get_categories()]
	
	def categories_and_description(self):
		"""
		Gets a list of tuples (category_name, description) for each test category.
		"""
		return self.api.get_categories()
		
	def scheduler(self, identifier):
		"""Gets a scheduler given its id in the database."""
		return DBScheduler(self, identifier)
		
	def schedulers(self, name=""):
		"""
		Gets a list of DBScheduler objects matching the given name
		Usually there is only one matching result.
		
		:param name: The exact name of the schedulers to find.
		"""
		scheds = self.api.get_schedulers_by_name(name)
		scheds = [DBScheduler(self, sched_id) for sched_id in scheds]
		return scheds
	
	def testsets(self, category=""):
		"""
		Gets a list of testsets given a category
		If no category is specified, all the testsets are displayed.
		
		:param category: the category of testsets to display.
		"""
		sets = self.api.get_testsets_by_category(category)
		tests = [DBTestSet(self, identifier) for identifier, name in sets]
		return tests
		
	def upload_testset(self, name, description, categories, conf_files):
		"""
		Uploads a test set with the given name, categories
		and configuration files (list of Configuration objects).
		"""
		for conf_file in conf_files:
			assert(isinstance(conf_file, Configuration))
		assert(isinstance(categories, list))
		
		self.api.upload_testset(name, description, categories, [generate(f) for f in conf_files])
		