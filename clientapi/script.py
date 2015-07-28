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
RUN = [int(s) for s in input("Test to run: ").split(',')]

table = {"test" : "test", "superman": "$uper$trongp@$$w0rd", "simso" : "simso"}
user = input("Username: ")


# Database initialisation
db = SimsoDatabase("http://localhost:8000", user, table[user])

# ----
# Running an experiment with local configuration files
# You can only upload that if you are one of the 
# Simso Experiment Database administrators.
# ----
if 0 in RUN:
	# Configure the experiment.
	scheduler_name = "superman.schedulers.EDF"
	test_name = "sample_test"
	test_description = "This is a sample description with <b>inner html</b>.\nAnd carriage return.\nAgain.\nAnd again."
	test_categories = ["sample_category"]
	files = ["test/test.xml", "test/configuration.xml"]
	
	# Create the experiment.
	config = (test_name, test_description, test_categories, [Configuration(f) for f in files])
	e = Experiment(db, config, db.schedulers(scheduler_name)[0])
	
	# Run the experiment
	e.run()
	
	# Optional : Upload the experiment
	# In this case, it is not allowed unless you are part
	# of the database admins.
	e.upload()
	
	# Get the metrics 
	print(repr(e.metrics))
	
	# Get the simulation results
	print(repr(e.results))
	

# ----
# Running an experiment with a remote test set
# ----
if 1 in RUN:
	scheduler_name = "superman.schedulers.EDF"
	
	# Gets all the categories
	categories = db.categories()
	
	# Gets all the testset for the choosen category
	testsets = db.testsets(menu(categories)) # categories[0]
	
	# Selects a testset
	testset = menu(testsets) # testsets[0]
	
	# Create the experiment
	e = Experiment(db, testset, db.schedulers(scheduler_name)[0])
	e.run()
	e.upload()

# ----
# Running an experiment with a remote test set
# ----
if 4 in RUN:
	scheduler_name = "superman.schedulers.EDF"
	
	# Gets all the categories
	categories = db.categories()
	
	# Gets all the testset for the choosen category
	testsets = db.testsets(categories[2])
	
	# Selects a testset
	testset = testsets[0]
	
	# Gets the results
	res = db.results(testset, db.schedulers(scheduler_name)[0])
	
	print(repr(res))
	
if 2 in RUN:
	# Configure the experiment.
	scheduler_name = "superman.schedulers.EDF"
	files = ["test/test.xml", "test/configuration.xml"]
	
	# Create the experiment.
	config = [Configuration(f) for f in files]
	e = Experiment(db, config, db.schedulers(scheduler_name)[0])
	
	# Run the experiment
	e.run()
	
	# In this case : you cannot upload the experiment.
	# e.upload()
	
	# Get the metrics 
	print(repr(e.metrics))
	
	# Get the simulation results
	print(repr(e.results))

# ----
# Running an experiment with a remote test set
# ----
if 3 in RUN:
	scheduler_name = "superman.schedulers.EDF"
	
	# Selects a testset
	testset = db.testset_by_name("test.testsets.my_test_name")
	
	# Create the experiment
	e = Experiment(db, testset, db.schedulers(scheduler_name)[0])
	e.run()
	
# ----
# Uploading a test set
# ----
if 42 in RUN:
	test_name = "my_test_name"
	categories = ["test_category1"]
	description = "description"
	files = ["test/test.xml", "test/configuration.xml"]
	db.upload_testset(test_name, description, categories, [Configuration(f) for f in files])
