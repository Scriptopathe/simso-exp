import urllib.request as url
import hashlib
import base64

def b64(string):
	return str(base64.b64encode(string.encode()), 'utf8')
def b64str(b64encoded_string):
	return str(base64.b64decode(b64encoded_string), 'utf8')
	
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
					 b64str(values[i*2+1])
				))
			return tuples
			
		else:
			return [];
		
		
	def get_conf_files(self, testset_id):
		"""
		Gets a list of XML configuration files for the given test id
		They are given as tuples (id, name, content)
		"""
		r = url.urlopen(self.base_addr + "/app/api/conffiles/" + str(testset_id))
		if(r.code == 200):
			val = str(r.read(), encoding='utf8')
			values = val.rsplit(',')
			tuples = []
			for i in range(0, int(len(values)//3)):
				tuples.append((
					 b64str(values[i*2]),
					 b64str(values[i*2+1]),
					 b64str(values[i*2+2])
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
	
	def get_scheduler_data(self, sched_id):
		"""
		Gets the scheduler data given the scheduler id.
		The scheduler data is a tuple (name, class_name, code).
		"""
		r = url.urlopen(self.base_addr + "/app/api/schedulers/data/" + str(sched_id))
		if(r.code == 200):
			val = str(r.read(), encoding='utf8')
			values = [b64str(value) for value in val.rsplit(',')]
			return (values[0], values[1], values[2]);
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
				tuples.append(b64str(values[i]))
			return tuples
		else:
			return []

