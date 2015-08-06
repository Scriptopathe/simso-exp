import urllib.request as url
import requests
import hashlib
import base64
import getpass
import os
import re

class ApiError(Exception):
	"""
	Type of errors raised by the API
	"""
	def __init__(self, value):
		self.value = value
	
	def __str__(self):
		return repr(self.value)
		
name_reg = r'^([\w|\.]*)$'
def b64(string):
	return str(base64.b64encode(string.encode()), 'utf8')
def b64str(b64encoded_string):
	return str(base64.b64decode(b64encoded_string), 'utf8')

def check_valid(name):
	"""
	Gets a value indicating if a ressource name is correct,
	e.g :
		- It contains only letters, numbers and underscores
	"""
	match = re.match(name_reg, name)
	if not match:
		raise ApiError("The name {} is not a valid ressource name ".format(name) + 
			"(should contain only letters, numbers, and underscores)")
	
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
	def __init__(self, address, username=None, password=None, use_cache=True):
		"""
		Initializes a connection to the Simso Experiment server
		at the given address (includes port number)
		"""
		self.base_addr = address;
		self.use_cache = use_cache;
		self.cache = {
			'testsets': {},
			'testsets_id': {},
			'results' : {},
			'conf_files': {},
			'schedulers' : {}
		}
		
		self.session = requests.session()
		
		# Prompts user name / password.
		nouser = username == None
		if username == None:
			print("Please enter your credentials for Simso Experiment Database website.")
			username = input("Username : ")
		
		if password == None:
			if not nouser:
				print("Enter password for user " + username)
			password = getpass.getpass()
		
		self.login(username, password)

	def login(self, username, password):
		"""
		Performs login to Simso Experiment Database.
		"""
		self.session.get(self.base_addr + "/accounts/login/")
		csrftoken = self.session.cookies['csrftoken']
		login_data = {'username':username,'password':password, 'csrfmiddlewaretoken':csrftoken, 'next': '/accounts/login'}
		p = self.session.post(self.base_addr + "/accounts/login/", data=login_data)
		self.handle_error(p)
		
	def urlopen(self, url):
		"""
		Opens the given url and returns the response.
		"""
		response = self.session.get(url, allow_redirects=False)
		if response.status_code == 302:
			raise ApiError("You cannot access the database beccause you have not logged in properly.")
		return response
	
	def post(self, url, data):
		"""
		Makes a post request to the given url with the given data.
		"""
		response = self.session.post(url, data=data)
		self.handle_error(response)
		return response
		
	def urlread(self, r):
		"""
		Reads the response's content
		"""
		return r.text
	
	def urlok(self, r):
		return r.ok
	
	def handle_error(self, r):
		if not r.ok:
			f = open("f.html", "w+")
			f.write(r.text)
			f.close()
			os.system("firefox f.html")
		
		r.raise_for_status()
		
	def get_testsets_by_category(self, category=""):
		"""
		Gets a tuple (id, name) for each test in the database matching
		the given category. (if category = None, gives all tests)
		"""
		category = b64(category)
		r = self.urlopen(self.base_addr + "/api/testsets/category/" + category)
		if self.urlok(r):
			val = self.urlread(r)
			values = val.rsplit(',');
			tuples = []
			for i in range(0, int(len(values)//2)):
				tuples.append(
					(int(base64.b64decode(values[i*2])),
					 b64str(values[i*2+1])
				))
			return tuples
			
		else: self.handle_error(r)
		
		
	def get_schedulers_by_code(self, code):
		"""
		Returns the scheduler id that corresponds to the scheduler with
		the given code. -1 if no scheduler matches.
		"""
		sha = hashlib.sha1(code).hexdigest();
		r = self.urlopen(self.base_addr + "/api/schedulers/sha/" + sha);
		if self.urlok(r):
			val = self.urlread(r)
			values = val.rsplit(',')
			tuples = []
			for i in range(0, len(values)):
				tuples.append(
					 b64str(values[i])
				)
			return tuples
		else: self.handle_error(r)
	
	def get_scheduler_by_name(self, name):
		"""Returns the scheduler ids corresponding to the scheduler name"""
		
		check_valid(name)
		
		r = self.urlopen(self.base_addr + "/api/schedulers/name/" + name);
		if self.urlok(r):
			val = self.urlread(r)
			if val == '':
				raise ApiError("Scheduler {} not found.".format(name))
			return int(val)
		else: self.handle_error(r)
			
	def get_results(self, testset_id, scheduler_id):
		"""Returns a list of result ids corresponding to the given test set and scheduler id"""
		r = self.urlopen(self.base_addr + "/api/results/" + str(testset_id) + "/" + str(scheduler_id))
		if self.urlok(r):
			val = self.urlread(r)
			
			if(val == ''):
				return []
				
			values = val.rsplit(',')
			tuples = []
			for i in range(0, len(values)):
				tuples.append(int(values[i]))
			return tuples
		else: self.handle_error(r)
	
	@cached('schedulers')
	def get_scheduler_data(self, identifier):
		"""
		Gets the scheduler data given the scheduler id.
		The scheduler data is a tuple (name, class_name, code).
		"""
		r = self.urlopen(self.base_addr + "/api/schedulers/data/" + str(identifier))
		if self.urlok(r):
			val = self.urlread(r)
			values = [b64str(value) for value in val.rsplit(',')]
			return (values[0], values[1], values[2]);
		else: self.handle_error(r)
	
	@cached('testsets')
	def get_testset_files(self, identifier):
		"""
		Gets a list of XML configuration files for the given test id
		Only their id is returned.
		"""
		r = self.urlopen(self.base_addr + "/api/testfiles/" + str(identifier))
		if self.urlok(r):
			val = self.urlread(r)
			
			if val == '':
				raise ApiError("Testset " + str(identifier) + " doesn't exist.")
			
			values = val.rsplit(',')
			tuples = []
			for i in range(0, len(values)):
				tuples.append(
					 int(values[i]),
				)
			return tuples
			
		else: self.handle_error(r)
		
	def get_testset_by_name(self, name):
		"""
		Gets the id of the test set whose name is given as argument
		"""
		
		check_valid(name)
		
		r = self.urlopen(self.base_addr + "/api/testsets/name/" + str(name))
		if self.urlok(r):
			val = self.urlread(r)
			if val == '':
				raise ApiError("Testset {} not found".format(name))
			return int(val)
		else: self.handle_error(r)
		
	@cached('testsets_id')
	def get_testset(self, identifier):
		"""
		Gets a tuple (name, description, categories[], files[]) for the testset with the given id.
		"""
		r = self.urlopen(self.base_addr + "/api/testsets/id/" + str(identifier))
		if self.urlok(r):
			val = self.urlread(r)
			
			if val == '':
				raise ApiError("Testset {} not found.".format(identifier))
				
			values = val.rsplit(',')
			tuples = (b64str(values[0]), b64str(values[1]), [], [])
			
			# Categories
			n = int(values[2])+2
			for i in range(3, n+1):
				tuples[2].append(b64str(values[i]))
			
			# Files
			n2 = int(values[n+1])
			for i in range(n+1, n+n2+2):
				tuples[3].append(values[i])
			
			return tuples
		else: self.handle_error(r)
	
	@cached('conf_files')
	def get_conf_file(self, identifier):
		"""
		Gets the configuration file whose id is identifier.
		Given as tuple (name, content)
		"""
		r = self.urlopen(self.base_addr + "/api/conf_file/" + str(identifier))
		if self.urlok(r):
			return self.urlread(r)
			
		else: self.handle_error(r)
	
	@cached('results')
	def get_result(self, identifier):
		"""
		Gets all the results associated to the given identifier.
		Gives testset_id and scheduler_id first, then a 
		dictionary with a key value pair for each metric.
			Ex : [1, 2, [{'name':name, 'count':count, 'avg':avg, 'std':std, 'median':median,
						  'minimum':min, 'maximum':max]
		"""
		r = self.urlopen(self.base_addr + "/api/results/id/" + str(identifier))
		if self.urlok(r):
			val = self.urlread(r)
			
			if val == '':
				raise ApiError("Results {} not found.".format(identifier))
				
				
			values = val.rsplit(',')
			attrs = ['name', 'sum', 'avg', 'std', 'median', 'minimum', 'maximum']
			metrics = []
			array = [int(values[0]), int(values[1]), metrics]
			for i in range(0, len(values)//len(attrs)):
				baseIndex = 2 + i * len(attrs)
				m = {}
				for j, attr in enumerate(attrs):
					m[attr] = b64str(values[baseIndex+j])
				metrics.append(m)
				
			return array
			
		else: self.handle_error(r)
	
	def get_categories(self):
		"""
		Gets all the test categories in the database and their descriptions as tuples
			(name, description)
		"""
		r = self.urlopen(self.base_addr + "/api/categories/")
		if self.urlok(r):
			val = self.urlread(r)
			values = val.rsplit(',')
			tuples = []
			for i in range(0, int(len(values)//2)):
				tuples.append(
					(b64str(values[i*2]),
					 b64str(values[i*2+1]))
				)
			return tuples
			
		else: self.handle_error(r)
	
	def upload_scheduler(self, name, class_name, code):
		"""
		Uploads a scheduler given its name, class_name and source code.
		"""
		response = self.post(self.base_addr + "/api/schedulers/upload/", {
			'sched_name' : name, 'sched_class_name' : class_name, 'sched_content' : code	
		})
		
		if self.urlok(response):
			value = self.urlread(response)
			if "error" in value:
				raise ApiError('upload_scheduler: The server returned the following status : ' + value)
			
		else: self.handle_error(r)
		
		
	def upload_experiment(self, postdata):
		"""
		Uploads an experiment (with the given post data)
		"""
		response = self.post(self.base_addr + "/api/experiment/upload", postdata)
		
		if self.urlok(response):
			value = self.urlread(response)
			if "error" in value:
				raise ApiError("upload_experiment: The server returned the following status : " + value)
		
		else: self.handle_error(r)
	
	def upload_testset(self, name, description, categories, conf_files):
		"""
		Uploads a test set with the given name, categories and list of
		configuration file (string containing XML configuration)
		"""
		data = {
			'conf_files' : conf_files,
			'test_name' : name,
			'test_description' : description,
			'categories' : categories
		}
		response = self.post(self.base_addr + "/api/testsets/upload", data)
		
		if self.urlok(response):
			value = self.urlread(response)
			if "error" in value:
				raise ApiError("upload_testset: The server returned the following status : " + value)
				
		else: self.handle_error(r)
		