from simsoexp.simsodb import SimsoDatabase, Experiment
from simsoexp.api import Api
from simso.configuration import Configuration
from simso.core import Model
from simso.configuration.GenerateConfiguration import generate
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
HEADER = OKBLUE + BOLD

def menu(options):
	for i, opt in enumerate(options):
		print("{} : {}".format(i, opt))
	choice = int(input("Select an option : "))
	return options[choice]

# Choose the samples to run
RUN = [s for s in input("Test to run: ").split(' ')]

table = {"test" : "test", "superman": "$uper$trongp@$$w0rd", "simso" : "simso"}
user = input("Username: ")


# Database initialisation
db = SimsoDatabase("http://localhost:8000", user, table[user])

# ----
# Running an experiment with local configuration files
# ----
if 'local_run' in RUN:
	# Configure the experiment.
	scheduler_name = "superman.schedulers.EDF"
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
if 'remote_run' in RUN:
	scheduler_name = "superman.schedulers.EDF"
	
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
if 'get_results' in RUN:
	scheduler_name = "superman.schedulers.EDF"
	
	testset = db.testset_by_name("simso.testsets.sample")
	
	# Gets the results
	res = db.results(testset, db.scheduler_by_name(scheduler_name))
	
	print(repr(res))
	
# ----
# Running an experiment with a remote test set (1)
# ----
if 'remote_run_menu' in RUN:
	scheduler_name = "superman.schedulers.EDF"
	
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
if 'testset_upload' in RUN:
	test_name = "sample"
	categories = ["sample_category"]
	description = "description"
	files = ["test/test.xml", "test/configuration.xml"]
	db.upload_testset(test_name, description, categories, [Configuration(f) for f in files])
