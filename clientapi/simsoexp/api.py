import urllib.request as url
import hashlib
import base64

def b64(string):
	return str(base64.b64encode(string.encode()), 'utf8')
def b64str(b64encoded_string):
	return str(base64.b64decode(b64encoded_string), 'utf8')

def cached(name):
	"""
	Decorator used to apply a cacheing mechanism to 
	an api function
	"""
	def f(func):
		def cached_func(self, identifier):
			if self.use_cache and identifier in self.cache[name]:
				return self.cache[name][identifier]
			result = func(self, identifier)
			if self.use_cache:
				self.cache[name][identifier] = result
			return result
		return cached_func
	return f
	
class Api:
	def __init__(self, address, use_cache=True):
		"""
		Initializes a connection to the Simso Experiment server
		at the given address (includes port number)
		"""
		self.base_addr = address;
		self.use_cache = use_cache;
		self.cache = {
			'testsets': {},
			'metrics' : {},
			'conf_files': {},
			'schedulers' : {}
		}
	
	def get_testsets_by_category(self, category=""):
		"""
		Gets a tuple (id, name) for each test in the database matching
		the given category. (if category = None, gives all tests)
		"""
		category = b64(category)
		r = url.urlopen(self.base_addr + "/app/api/testsets/" + category)
		if(r.code == 200):
			val = str(r.read(), encoding='utf8')
			values = val.rsplit(',');
			tuples = []
			for i in range(0, int(len(values)//2)):
				tuples.append(
					(int(base64.b64decode(values[i*2])),
					 b64str(values[i*2+1])
				))
			return tuples
			
		else:
			return [];
		
		
	def get_schedulers_by_code(self, code):
		"""
		Returns the scheduler id that corresponds to the scheduler with
		the given code. -1 if no scheduler matches.
		"""
		md5 = hashlib.md5(code).hexdigest();
		sha = hashlib.sha1(code).hexdigest();
		r = url.urlopen(self.base_addr + "/app/api/schedulers/sha/" + sha);
		if(r.code == 200):
			val = str(r.read(), encoding='utf8')
			values = val.rsplit(',')
			tuples = []
			for i in range(0, len(values)):
				tuples.append(
					 b64str(values[i])
				)
			return tuples
		else:
			return [];
	
	def get_schedulers_by_name(self, name):
		"""Returns the scheduler ids corresponding to the scheduler name"""
		name = b64(name);
		r = url.urlopen(self.base_addr + "/app/api/schedulers/name/" + name);
		if(r.code == 200):
			val = str(r.read(), encoding='utf8')
			values = val.rsplit(',')
			tuples = []
			for i in range(0, len(values)):
				tuples.append(
					 int(values[i]),
				)
			return tuples
		else:
			return [];
			
	def get_metrics(self, testset_id, scheduler_id):
		"""Returns a list of metrics ids corresponding to the given test set and scheduler id"""
		r = url.urlopen(self.base_addr + "/app/api/metrics/" + str(testset_id) + "/" + str(scheduler_id))
		if(r.code == 200):
			val = str(r.read(), encoding='utf8')
			
			if(val == ''):
				return []
				
			values = val.rsplit(',')
			tuples = []
			for i in range(0, len(values)):
				tuples.append(int(values[i]))
			return tuples
		else:
			return []
	
	@cached('schedulers')
	def get_scheduler_data(self, identifier):
		"""
		Gets the scheduler data given the scheduler id.
		The scheduler data is a tuple (name, class_name, code).
		"""
		r = url.urlopen(self.base_addr + "/app/api/schedulers/data/" + str(identifier))
		if(r.code == 200):
			val = str(r.read(), encoding='utf8')
			values = [b64str(value) for value in val.rsplit(',')]
			return (values[0], values[1], values[2]);
		else:
			return ""
	
	@cached('testsets')
	def get_testset_files(self, identifier):
		"""
		Gets a list of XML configuration files for the given test id
		Only their id is returned.
		"""
		r = url.urlopen(self.base_addr + "/app/api/testfiles/" + str(identifier))
		if(r.code == 200):
			val = str(r.read(), encoding='utf8')
			values = val.rsplit(',')
			tuples = []
			for i in range(0, len(values)):
				tuples.append(
					 int(values[i]),
				)
			return tuples
			
		else:
			return []
	
	@cached('conf_files')
	def get_conf_file(self, identifier):
		"""
		Gets the configuration file whose id is identifier.
		Given as tuple (name, content)
		"""
		r = url.urlopen(self.base_addr + "/app/api/conf_file/" + str(identifier))
		if(r.code == 200):
			val = str(r.read(), encoding='utf8')
			values = val.rsplit(',')
			return (b64str(values[0]), b64str(values[1]))
			
		else:
			return []
	
	@cached('metrics')
	def get_metric(self, identifier):
		"""
		Gets all the metrics associated to the given metric_id.
		Gives testset_id and scheduler_id first, then a 
		dictionary with a key value pair for each metric.
			Ex : [1, 2, {'metric' : 'value'}]
		"""
		r = url.urlopen(self.base_addr + "/app/api/metrics/id/" + str(identifier))
		if(r.code == 200):
			val = str(r.read(), encoding='utf8')
			print(val)
			values = val.rsplit(',')
			dic = {}
			array = [int(values[0]), int(values[1]), dic]
			for i in range(1, len(values)//2):
				key = b64str(values[i*2])
				value = b64str(values[i*2+1])
				print(key + " -" + value)
				dic[key] = value
				
			return array
			
		else:
			return [-1, -1, {}]
