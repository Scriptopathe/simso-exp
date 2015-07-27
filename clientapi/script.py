from simsoexp.simsodb import SimsoDatabase, Experiment
from simsoexp.api import Api
from simso.configuration import Configuration
from simso.core import Model

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
RUN = [1]


# Database initialisation
db = SimsoDatabase("http://localhost:8000")

# ----
# Running an experiment with local configuration files
# ----
if 0 in RUN:
	# Configure the experiment.
	scheduler_name = "superman.schedulers.EDF"
	test_name = "sample_test"
	test_categories = ["sample_category"]
	files = ["test/test.xml", "test/configuration.xml"]
	
	# Create the experiment.
	config = (test_name, test_categories, [Configuration(f) for f in files])
	e = Experiment(db, config, db.schedulers(scheduler_name)[0])
	
	# Run the experiment
	e.run()
	
	# Optional : Upload the experiment
	# e.upload()
	
	# Get the metrics 
	e.metrics
	
	# Get the simulation results
	e.results

if 1 in RUN:
	# ----
	# Running an experiment with a remote test set
	# ----
	scheduler_name = "superman.schedulers.EDF"
	
	# Gets all the categories
	categories = db.categories()
	
	# Gets all the testset for the choosen category
	testsets = db.testsets(menu(categories))
	
	# Selects a testset
	testset = menu(testsets)
	
	# Create the experiment
	e = Experiment(db, testset, db.schedulers(scheduler_name)[0])
	e.run()
