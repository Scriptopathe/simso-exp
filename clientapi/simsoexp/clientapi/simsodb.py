# This file contains high-level api designed to work with simso
import sys
from .api import Api
from .api import ApiError
from .metrics_collector import MetricsCollector
from simso.core import Model
from simso.configuration import Configuration
from simso.configuration.GenerateConfiguration import generate
import re
import numpy
import os

def _check_type(var, varname, ttype):
	if(not isinstance(var, ttype)):
		raise TypeError("Expected parameter '{}' of type {}. Got {}".format(varname, ttype, var.__class__))
	
class DBResults:
	"""
	Represents a results set from a remote Simso Experiment Database.
	These results contains :
	- the scheduler and testset identifiers in the database used to build the experiment.
	- the resulting metrics
	"""
	def __init__(self, db, identifier):
		"""
		Creates a new instance of DBResults its database identifier.
		This should not be called directly, the methods from :class:'SimsoDatabase' instead.
		"""
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
		self.__metrics = dict()
		for metric in m[2]:
			self.__metrics[metric["name"]] = dict()
			for key in metric:
				if key == "name":
					continue
				self.__metrics[metric["name"]][key] = float(metric[key])
		
	
	@property	
	def testset_id(self):
		"""
		:returns: The id of the testset used to build these results.
		:rtype: int
		"""
		if self.__testset_id == None:
			self.__load_metrics()
		return self.__testset_id
	
	@property
	def scheduler_id(self):
		"""
		:returns: The id of the scheduler used to build these results.
		:rtype: int
		"""
		if self.__scheduler_id == None:
			self.__load_metrics()
		return self.__scheduler_id
	
	def __getitem__(self, name):
		"""
		This is a shortcut to *metrics[name]*.
		:param name: The name of the metric to retrieve.
		
		:returns: A dictionnary of key-values pairs containing as keys
		the measure name (avg, minimum, median, maximum, sum, std).
		:rtype: dict
		"""
		if self.__metrics == None:
			self.__load_metrics()
		
		return self.__metrics[name]
	
	@property
	def metrics(self):
		"""
		:returns: A dictionnary containing a set of metrics indexed by their name.
		:rtype: dict of dict
		"""
		if self.__metrics == None:
			self.__load_metrics()
			
		return self.__metrics
	
	def __repr__(self):
		return "<DBResults id={} testset={} scheduler={}>".format(
			self.identifier, self.testset_id, self.scheduler_id
		)
	
class DBTestSet:
	"""
	Represents a test set taken from a remote Simso Experiment Database.
	"""
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
		
	def push(self, newdb):
		"""
		Pushes this DBTestset object to another database.
		*Note : this testset might need to be validated by the maintainers of the destination database.*
		
		:param newdb: Destination database where the object will be pushed.
		:type newdb: SimsoDatabase
		"""
		_check_type(newdb, 'newdb', SimsoDatabase)
		newdb.upload_testset(self.name, self.description, self.categories, [c.configuration for c in self.conf_files])
		
	@property
	def name(self):
		"""
		:returns: The name of the test set
		:rtype: str
		"""
		if self.__name == None:
			self.__load_data()
		return self.__name
	
	@property
	def description(self):
		"""
		:returns: The description of the test set.
		:rtype: str
		"""
		if self.__description == None:
			self.__load_data()
		return self.__description
	
	@property
	def categories(self):
		"""
		:returns: This test set's categories as a list.
		:rtype: list of string
		"""
		if self.__categories == None:
			self.__load_data()
		return self.__categories
	
	@property
	def conf_files(self):
		"""
		:returns: a list of DBConfFile object for each configuration file in this test set.
		:rtype: list of DBConfFile
		"""
		if self.__conf_files == None:
			self.__load_conf_files()
		return self.__conf_files
	
	def __repr__(self):
		return "<DBTestSet id={}, name={}>".format(self.identifier, self.name)

class DBConfFile:
	"""
	Represents a configuration file taken from a remote Simso Experiment Database.
	"""
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
		:returns: this configuration file's XML content.
		:rtype: str
		"""
		if self.__content == None:
			self.__load_data()
		return self.__content
	
	@property
	def configuration(self):
		"""
		:returns: the Simso configuration object represented by this configuration file.
		:rtype: simso.configuration.Configuration
		"""
		if self.__configuration == None:
			self.__load_configuration()
		return self.__configuration
		
	def __repr__(self):
		return "<DBConfFile id={}>".format(self.identifier)

_schedprefixreg = re.compile('^([\w]*\.schedulers\.)')
class DBScheduler:
	"""
	Represents a scheduler taken from a remote Simso Experiment Database.
	"""
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
		:returns: the scheduler's class object.
		:rtype: type
		"""
		if(self.__cls == None):
			self.__load_cls()
		return self.__cls
		
	@property
	def code(self):
		"""
		:returns: this scheduler's python code
		:rtype: str
		"""
		if self.__code == None:
			self.__load_data()
		return self.__code
	
	@property
	def name(self):
		"""
		:returns: this scheduler visible name
		:rtype: str
		"""
		if self.__name == None:
			self.__load_data()
		return self.__name
	
	@property
	def class_name(self):
		"""
		:returns: the scheduler's main class in the scheduler's code
		:rtype: str
		"""
		if self.__class_name == None:
			self.__load_data()
		return self.__class_name
		
	def push(self, newdb):
		"""
		Pushes this DBScheduler object to another database.
		*Note : this scheduler might need to be validated by the maintainers of the destination database.*
		
		:param newdb: Destination database where the object will be pushed.
		:type newdb: SimsoDatabase
		"""
		_check_type(newdb, 'newdb', SimsoDatabase)
		
		# Replaces the user name from the old db by nothing
		name = re.sub(_schedprefixreg, "", self.name)
		
		newdb.upload_scheduler(name, self.class_name, self.code)
		
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
		:conf_files: Either a DBTestSet object or Custom Test Set (a list of Configuration objects).
		
		
		Take care : you won't be able to upload your results if you used a custom test set.
		"""
		self.db = db
		self.results = []
		# Checks conf_files
		if isinstance(conf_files, DBTestSet):
			if conf_files.db.base_addr != self.db.base_addr:
				raise ApiError("The database of the 'conf_files' parameter is {}, expected {}".format(
					conf_files.db.base_addr,
					self.db.base_addr
				));
				
			self.testset = conf_files
			self.testname = self.testset.name
			self.testdesc = self.testset.description
			self.conf_files = [f.configuration for f in conf_files.conf_files]
			self.categories = self.testset.categories
		elif isinstance(conf_files, list):
			for f in conf_files:
				_check_type(f, 'f', Configuration)
			self.conf_files = conf_files
			self.testset = None
			self.testname = None
			self.testdesc = None
			self.categories = None
		else:
			raise TypeError("Expected conf_file to be 'list of Configuration' or 'DBTestSet'. Got {}".format(conf_files.__class__))
		# Check scheduler
		_check_type(scheduler, 'scheduler', DBScheduler)
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
		Uploads the experiment results to Simso Experiment Database.
		
		An ApiError will be raised if the results of the experiment already exist.
		
		*Note you won't be able to upload your results if you used a custom test set.*
		
		:raise ApiError: the operation is not allowed (see exception details).
		"""
		if self.testset == None:
			raise Exception("You cannot upload an experiment with a custom testset.")
		
		data = {}
		
		# Metrics
		data["metrics"] = []
		for metric in self.metrics:
			data["metrics"].append(','.join([metric] + [str(m) for m in self.metrics[metric]]))
		
		# Configuration files / testset
		data["testset_id"] = str(self.testset.identifier)

		# Scheduler
		data["scheduler"] = self.scheduler.identifier
		
		self.db.api.upload_experiment(data)

class SimsoDatabase:
	"""
	SimsoDatabase is the main component of the **Simso Experiment Platform API**.
	"""
	def __init__(self, address, username=None, password=None):
		"""
		Initializes a connection to the Simso Experiment server
		at the given address (includes port number)
		Ex: http://example.com:8000/
		"""
		_check_type(address, 'address', str)
		
		self.base_addr = address.rstrip('/');
		self.api = Api(self.base_addr, username, password)
		self.preload = False
		self.__init_cache()
		
	def __init_cache(self):
		self.local_cache_dir = os.path.expanduser("~") + "/.simsoexpcache"
		self.local_conf_dir = self.local_cache_dir + "/configurations"
		if not os.path.exists(self.local_cache_dir):
			os.makedirs(self.local_cache_dir)
			os.makedirs(self.local_conf_dir)
		
	def testset(self, identifier):
		"""
		:param identifier: The identifier of the testset to retrieve.
		:type identifier: int
		:returns: DBTestset instance whose id is *identifier*
		:rtype: DBTestset
		"""
		_check_type(identifier, 'identifier', int)
		
		return DBTestSet(self, identifier)
	
	def testset_by_name(self, name):
		"""
		:returns: DBTestset instance whose name is *name*
		:rtype: DBTestset
		"""
		_check_type(name, 'name', str)
		
		identifier = self.api.get_testset_by_name(name)
		return DBTestSet(self, identifier)
	
	def results(self, testset, scheduler):
		"""
		Gets the results associated to the given testset and scheduler.
		These results have been obtained by running simso with the corresponding
		scheduler and testsets.
		
		:param testset: A DBTestSet instance.
		:type testset: DBTestSet
		:param scheduler: A DBScheduler instance.
		:type scheduler: DBScheduler
		:returns: The results corresponding to the given scheduler and testset.
		:rtype: list of DBResults
		:raise HttpError: there was an error in the request.
		"""
		_check_type(testset, 'testset', DBTestSet)
		_check_type(scheduler, 'scheduler', DBScheduler)
		
		m = self.api.get_results(testset.identifier, scheduler.identifier)
		return [DBResults(self, identifier) for identifier in m]
	
	def result(self, identifier):
		"""
		:returns: a result set given its identifier in the database.
		:rtype: DBResults
		"""
		_check_type(identifier, 'identifier', int)
		return DBResults(self, identifier)
		
	def categories(self):
		"""
		:returns: a list of all the test categories in the database.
		:rtype: list of str
		:raise HttpError: there was an error in the request.
		"""
		return [cat[0] for cat in self.api.get_categories()]
	
	def categories_and_description(self):
		"""
		:returns: a list of tuples (category_name, description) for each test category.
		:rtype: list of (str, str)
		:raise HttpError: there was an error in the request.
		"""
		return self.api.get_categories()
		
	def scheduler(self, identifier):
		"""
		:returns: a scheduler given its id in the database.
		:rtype: DBScheduler
		"""
		_check_type(identifier, 'identifier', int)
		return DBScheduler(self, identifier)
		
	def scheduler_by_name(self, name=""):
		"""		
		:param name: The exact name of the schedulers to find.
		:type name: str
		:returns: a scheduler given its name in the database.
		:rtype: DBScheduler
		:raise HttpError: there was an error in the request.
		:raise ApiError: the scheduler with the given name does not exist.
		"""
		_check_type(name, 'name', str)
		return DBScheduler(self, self.api.get_scheduler_by_name(name))
	
	def testsets(self, category=""):
		"""
		Gets a list of testsets given a category.
		If no category is specified, all the testsets are returned.
		
		:param category: the category of testsets to display.
		:type category: str
		:returns: list of testsets given a category.
		:rtype: list of DBTestSet
		:raise HttpError: there was an error in the request.
		"""
		_check_type(category, 'category', str)
		sets = self.api.get_testsets_by_category(category)
		tests = [DBTestSet(self, identifier) for identifier, name in sets]
		return tests
		
	def upload_testset(self, name, description, categories, conf_files):
		"""
		Uploads a test set with the given name, categories
		and configuration files (list of Configuration objects).
		
		The testset will be available in the database as soon as 
		it is validated by a maintainer.
		
		If a VALIDATED testset with the same name already exists, an 
		ApiError is raised. If a non-validated testset with the same name 
		already exists, it will be overriden if you are the author of the 
		existing test set.
		
		:param name: name of the test set to upload
		:type name: str
		:param description: description of the test set to upload.
		:type description: str
		:param categories: categories linked to the test set. They must already exist in the DB.
		:type categories: list of str
		:raise HttpError: there was an error in the request.
		:raise ApiError: the operation is not allowed (see exception details)
		"""
		for conf_file in conf_files:
			_check_type(conf_file, 'conf_file', Configuration)
		_check_type(categories, 'categories', list)
		
		self.api.upload_testset(name, description, categories, [generate(f) for f in conf_files])
		

	def upload_scheduler(self, name, class_name, code):
		"""
		Uploads a scheduler with the given name, class name and code
		to the database.
		
		The scheduler will be available in the database as soon as 
		it is validated by a maintainer.
		
		If a VALIDATED scheduler with the same name already exists, an 
		ApiError is raised. If a non-validated scheduler with the same name 
		already exists, it will be overriden if you are the author of the 
		existing scheduler.
		
		:param name: name of the scheduler to upload. Should be unique.
		:type name: str
		:param class_name: name of the main class of the scheduler in the code.
		:type class_name: str
		:param code: python code of the scheduler.
		:type code: str
		:raise HttpError: there was an error in the request.
		:raise ApiError: the operation is not allowed (see exception details)
		"""
		_check_type(name, 'name', str)
		_check_type(class_name, 'class_name', str)
		_check_type(code, 'code', str)
		
		self.api.upload_scheduler(name, class_name, code)