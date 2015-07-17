import urllib.request as url
import hashlib
import base64

class Api:
	def __init__(self, address):
		"""Initializes a connection to the Simso Experiment server
		at the given address (includes port number)"""
		self.base_addr = address;
		pass
	
	def get_testsets(self, category="all"):
		"""Gets a tuple (id, name) for each test in the database matching
		the given category. (if category = None, gives all tests)"""
		category = str(base64.b64encode(category.encode()), 'utf8');
		r = url.urlopen(self.base_addr + "/app/api/testsets/" + category)
		if(r.code == 200):
			val = str(r.read(), encoding='utf8')
			values = val.rsplit(',');
			tuples = []
			for i in range(0, int(len(values)//2)):
				tuples.append(
					(int(base64.b64decode(values[i*2])),
					 str(base64.b64decode(values[i*2+1]), encoding='utf8')
				))
			return tuples
			
		else:
			return [];
		
		
	def get_conf_files(self, testset_id):
		"""Gets a list of XML configuration files for the given test id"""
		r = url.urlopen(self.base_addr + "/app/api/conffiles/" + str(testset_id))
		if(r.code == 200):
			val = str(r.read(), encoding='utf8')
			values = val.rsplit(',')
			tuples = []
			for i in range(0, int(len(values)//2)):
				tuples.append((
					 str(base64.b64decode(values[i*2]), encoding='utf8'),
					 str(base64.b64decode(values[i*2+1]), encoding='utf8')
				))
			return tuples
			
		else:
			return []
		
	
	def get_scheduler_by_code(self, code):
		"""Returns the scheduler id that corresponds to the scheduler with
		the given code"""
		md5 = hashlib.md5(code).hexdigest();
		sha = hashlib.sha1(code).hexdigest();
		
		pass
	
	def get_schedulers_by_name(self, name):
		"""Returns the scheduler ids corresponding to the scheduler name"""
		pass
	
	def get_schedulers_code(self, schedid):
		"""Gets the scheduler code given the scheduler id"""
		pass
	
	def get_metrics(self, testset_id, scheduler_id):
		"""Returns a list of metrics corresponding to the given test set and scheduler id"""
		pass