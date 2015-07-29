from simsoexp.simsodb import SimsoDatabase, Experiment
from simsoexp.api import Api
from simso.configuration import Configuration
from simso.core import Model
from simso.configuration.GenerateConfiguration import generate
from simsoexp.api import ApiError

OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
HEADER = OKBLUE + BOLD

_registered_funcs = {}
logs = []
errors = 0
success = 0

def menu(options):
	if 'all' in RUN:
		return options[0]
	
	for i, opt in enumerate(options):
		print("{} : {}".format(i, opt))
	choice = int(input("Select an option : "))
	return options[choice]

def register(funcname):
	def r(func):
		_registered_funcs[funcname] = func
		return func
	return r

def execute(func, funcname):
	global success
	global errors
	global logs
	print("-- RUNNING TEST '" + funcname + "' -- ")
	try:
		func()
		logs.append(OKGREEN + "Test " + funcname + " executed." + ENDC)
		success += 1
	except ApiError as e:
		print(OKBLUE + "API Error executing test " + funcname + ENDC)
		logs.append(OKBLUE + "Error executing test " + funcname + " :\n\t " + str(e) + ENDC)
		success += 1
	except Exception as e:
		print(FAIL + "Error executing test " + funcname + ENDC)
		logs.append(FAIL + "Error executing test " + funcname + " :\n\t " + str(e) + ENDC)

		errors += 1
	finally:
		pass
		
	print("-- END OF '" + funcname + "' --")

# Users auto log in
table = {"test" : "test", "superman": "$uper$trongp@$$w0rd", "simso" : "simso"}
user = input("Username: ")


# Database initialisation
db = SimsoDatabase("http://localhost:8000", user, table[user])

# ----
# Running an experiment with local configuration files
# ----
@register('local_run')
def local_run():
	# Configure the experiment.
	scheduler_name = "simso.schedulers.EDF"
	files = ["test/test.xml", "test/configuration.xml"]
	
	# Create the experiment.
	config = [Configuration(f) for f in files]
	scheduler = db.scheduler_by_name(scheduler_name)
	e = Experiment(db, config, scheduler)
	
	# Run the experiment
	e.run()
	
	# You cannot upload the experiment with local configuration files
	if '-upload' in RUN:
		e.upload() # => ERROR
	
	# Get the metrics 
	print(repr(e.metrics))
	
	# Get the simulation results
	print(repr(e.results))
	
# ----
# Running an experiment with a remote test set
# ----
@register('remote_run')
def remote_run():
	scheduler_name = "simso.schedulers.EDF"
	
	# Selects a testset
	testset = db.testset_by_name("simso.testsets.sample")
	
	# Create the experiment
	e = Experiment(db, testset, db.scheduler_by_name(scheduler_name))
	e.run()
	
	if '-upload' in RUN:
		e.upload()
	
# ----
# Getting the results of an experiment.
# ----
@register('get_results')
def get_results():
	scheduler_name = "simso.schedulers.EDF"
	
	testset = db.testset_by_name("simso.testsets.sample")
	
	# Gets the results
	res = db.results(testset, db.scheduler_by_name(scheduler_name))
	
	print(repr(res))
	
# ----
# Running an experiment with a remote test set (1)
# ----
@register('remote_run')
def remote_run_menu():
	scheduler_name = "simso.schedulers.EDF"
	
	# Gets all the categories
	categories = db.categories()
	
	# Gets all the testset for the choosen category
	testsets = db.testsets(menu(categories)) # categories[0]
	
	# Selects a testset
	testset = menu(testsets) # testsets[0]
	
	# Create the experiment
	e = Experiment(db, testset, db.scheduler_by_name(scheduler_name))
	e.run()
	
	if '-upload' in RUN:
		e.upload()
	
# ----
# Uploading a test set
# ----
@register('upload_testset')
def upload_testset():
	test_name = "sample"
	categories = ["sample_category"]
	description = "description"
	files = ["test/test.xml", "test/configuration.xml"]
	db.upload_testset(test_name, description, categories, [Configuration(f) for f in files])


# ----
# Many tests
# ----
@register("testset_by_name")
def testset_by_name():
	db.testset_by_name("simso.testsets.sample")

@register("testset_by_name_nonexistant")
def testset_by_name_nonexistant():
	db.testset_by_name("nonono")

@register("testset_by_name_invalid")
def testset_by_name_invalid():
	db.testset_by_name("simso.testsets.é@é[}^^")
	
@register("scheduler_by_name")
def scheduler_by_name():
	db.scheduler_by_name("simso.schedulers.EDF")

@register("scheduler_by_name_nonexistant")
def scheduler_by_name_nonexistant():
	db.scheduler_by_name("nonono")

@register("scheduler_by_name_invalid")
def scheduler_by_name_invalid():
	db.scheduler_by_name("simso.schedulers.é@é[}^^")

@register("categories")
def categories():
	print(db.categories())

@register("DBTestSet")
def dbtestset():
	t = db.testset(1)
	t.name
	t.description
	t.categories
	t.conf_files

@register("DBResults")
def dbresults():
	t = db.result(1)
	t.testset_id
	t.scheduler_id
	t.metrics
	
# Choose the samples to run
print("Available tests: ")
[print(str(i) + ": " + f) for i, f in enumerate(_registered_funcs)]
RUN = [s for s in input("Tests to run: ").split(' ')]

if 'all' in RUN:
	[execute(_registered_funcs[f], f) for f in _registered_funcs]
else:
	[execute(_registered_funcs[f], f) for f in RUN]

total = errors + success	
print("Execution of {} tests terminated.".format(total))
print("{} successful, {} errors".format(success, errors))

print("Logs : ")
[print(log) for log in logs]