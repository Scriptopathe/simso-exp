# This file contains high-level api designed to work with simso
from .api import Api

class TestSet:
	def __init__(self, db, identifier):
		self.db = db
		self.identifier = identifier
		self.__conf_files = None
		if(db.preload):
			self.__load_conf_files()
		
	def __load_conf_files(self):
		self.__conf_files = self.db.api.get_conf_files(self.identifier)
	
	@property
	def conf_files(self):
		"""Gets a list of tuples (name, XML content) for each
		configuration file in this test set"""
		if(self.__conf_files == None):
			self.__load_conf_files()
		return self.__conf_files
	
class SimsoDatabase:
	def __init__(self, address):
		"""
		Initializes a connection to the Simso Experiment server
		at the given address (includes port number)
		Ex: http://example.com:8000/
		"""
		self.base_addr = address;
		self.api = Api(address)
		self.preload = False
		
	def get_testset_by_id(self, identifier):
		"""Gets a testset given its id"""
		return TestSet(self, identifier)
		
	def get_testsets_by_category(self, category=""):
		"""Gets a list of testset given a category"""
		sets = self.api.get_testsets_by_category(category)
		tests = []
		for identifier, name in sets:
			tests.append(TestSet(self, identifier))
		return tests