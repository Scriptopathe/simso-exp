# Raw and dirty script to create the database
rootpassword = raw_input("Database root password  : ")
print("A new database user is going to be created.")
print("Please enter its username and password")

user = raw_input("username : ")
password = raw_input("password : ")

filecontent = """sudo apt-get install python-pip python-dev mysql-server libmysqlclient-dev
sudo pip install mysqlclient
sudo mysql_install_db
sudo mysql_secure_installation
mysql -u root --passwword={0} -e "source setup_db.sql"
""".format(rootpassword)


dbcontent = """CREATE DATABASE simsoexp CHARACTER SET UTF8;
CREATE USER {0}@localhost IDENTIFIED BY '{1}';
GRANT ALL PRIVILEGES ON simsoexp.* TO {0}@localhost;
FLUSH PRIVILEGES;""".format(user, password)


f = open("setup_db.sh", "w+")
f.write(filecontent)
f.close()

f = open("setup_db.sql", "w+")
f.write(dbcontent)
f.close()

import os
os.system("chmod u+x setup_db.sh")
os.system("./setup_db.sh")

os.system("rm setup_db.sh")
os.system("rm setup_db.sql")

print("Database created ! ")