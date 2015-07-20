import urllib.request as url
import hashlib
import base64

def b64(string):
	return str(base64.b64encode(string.encode()), 'utf8')
	
class Api:
	def __init__(self, address):
		"""
		Initializes a connection to the Simso Experiment server
		at the given address (includes port number)
		"""
		self.base_addr = address;
	
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
					 str(base64.b64decode(values[i*2+1]), encoding='utf8')
				))
			return tuples
			
		else:
			return [];
		
		
	def get_conf_files(self, testset_id):
		"""
		Gets a list of XML configuration files for the given test id
		They are given as tuples (name, content)
		"""
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
					 str(base64.b64decode(values[i]), encoding='utf8'),
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
					 str(base64.b64decode(values[i]), encoding='utf8'),
				)
			return tuples
		else:
			return [];
	
	def get_scheduler_code(self, sched_id):
		"""Gets the scheduler code given the scheduler id"""
		r = url.urlopen(self.base_addr + "/app/api/schedulers/code/" + sched_id)
		if(r.code == 200):
			val = str(r.read(), encoding='utf8')
			return val;
		else:
			return ""
	
	def get_metrics(self, testset_id, scheduler_id):
		"""Returns a list of metrics corresponding to the given test set and scheduler id"""
		r = url.urlopen(self.base_addr + "/app/api/metrics/" + str(testset_id) + "/" + str(scheduler_id))
		if(r.code == 200):
			val = str(r.read(), encoding='utf8')
			values = val.rsplit(',')
			tuples = []
			for i in range(0, len(values)):
				tuples.append(str(base64.b64decode(values[i]), encoding='utf-8'))
			return tuples
		else:
			return []