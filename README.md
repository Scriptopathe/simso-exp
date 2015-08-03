# simso-exp
Simso Experiment Platform is a web server written in Python / Django hosting a website and an API designed to help researchers to share and run experiments made with SimSo.

There is a central Simso Experiment Platform instance running at : (TODO : put production website here).
It has been open sourced so researchers can also run the platform locally and export their work later to the central instance.

Components
===========

Simso exp
---------
Simso exp is the server running both the website and server-side API.

Client API
----------
The client API is a python package ([here](https://github.com/Scriptopathe/simso-exp/tree/master/clientapi/simsoexp)) 
containing components that can interact with the Simso Experiment Platform's web API.

See section Client API Documentation for further details.

The client API requires SimSo to be installed on your computer.
```pip install simso```

Client API Documentation
========================
The documentation for the client API can be found [here in HTML format](https://github.com/Scriptopathe/simso-exp/tree/master/clientapi/doc/build/html)

Examples and code snippets can be found in the index page of any instance running Simso Experiment Platform. (TODO : put production website here)

Server set up
=============
0. First you need to get the tools needed to install everything :
```sudo apt-get install git python-pip python-dev mysql-server libmysqlclient-dev; sudo pip install mysqlclient django```

0. Install the database :
```sudo mysql_install_db
sudo mysql_secure_installation```

0. Create the database :
```mysql -u root -p
mysql> CREATE DATABASE simsoexp CHARACTER SET UTF8;```

0. Create a database user for simsoexp. Replace 'password' by the password you want to use for this user 
(should not be the same as the mysql root account).
```mysql> CREATE USER simsoexpuser@localhost IDENTIFIED BY 'password';
mysql> GRANT ALL PRIVILEGES ON simsoexp.* TO simsoexpuser@localhost;
mysql> FLUSH PRIVILEGES;```

0. Clone this github project
```git clone https://github.com/Scriptopathe/simso-exp```

0. Open the file simsodata_server/dbsettings.py and put the username and password you chose for the simsoexp database user.
0. Open the file simsodata_server/secretkey.py and generate a secret key using any tool you like (you can use [this one](http://www.miniwebtool.com/django-secret-key-generator/))
0. Create django's super user (be sure to set your working directory to the project's root) : ```python manage.py migrate
python manage.py createsuperuser```

Local use
---------
Use this command to run the server on http://localhost:8000: 
```python manage.py runserver```

Production environment
----------------------
Setting up a production environment is beyond the scope of this document. 
However you can check out [this documentation](https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/modwsgi/) if you're interested.

