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

if False:
	db = SimsoDatabase("http://localhost:8000")
	print(HEADER + "------ Simso DB test program ------" + ENDC)
	print(HEADER + "------ All test sets" + ENDC)
	sets = db.testsets()
	blbl = db.testsets()
	print(repr(sets))
	print(HEADER + "------ One test set" + ENDC)
	test = sets[0]
	print(repr(test))
	print(HEADER + "------ Test set configuration files" + ENDC)
	conf = test.conf_files
	print(repr(blbl[0].conf_files))
	print(repr(conf))
	print(HEADER + "------ First configuration file" + ENDC)
	print(repr(conf[0]))
	print(HEADER + "------ Loaded conf file" + ENDC)
	print(repr(conf[0].configuration))
	print(HEADER + "------ EDF Scheduler" + ENDC)
	sched = db.schedulers("simso.schedulers.EDF")[0]
	print(HEADER + "------ Metrics" + ENDC)
	metrics = db.metrics(test.identifier, sched.identifier)
	print(repr(metrics))
	print(repr(metrics[0].all()))
	cf = conf[0].configuration
	cf.scheduler_info.cls = sched.cls
	model = Model(cf)
	model.run_model()
	print(HEADER + "------ SUCCESSFULLY RUN MODEL" + ENDC)

cfg = Configuration("test/test.xml")
cfg2 = Configuration("test/configuration.xml")
db = SimsoDatabase("http://localhost:8000")
for i in range(1, 1000):
	cfg = Configuration("test/test.xml")
	cfg2 = Configuration("test/configuration.xml")
	e = Experiment(db, 
		(
			"Custom test", 
			["testcat1", "testcat2"],
			[cfg, cfg2],
		),
		db.schedulers("superman.schedulers.EDF")[0])
	e.run()
	print("Uploading experiment {} / {}".format(i, 1000))	
	e.upload()