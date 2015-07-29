# Raw and dirty script to create the database
rootpassword = raw_input("Database root password  : ")
print("A new database user is going to be created.")
print("Please enter its username and password")

user = raw_input("username : ")
password = raw_input("password : ")

dbcontent = """CREATE DATABASE simsoexp CHARACTER SET UTF8;
CREATE USER {0}@localhost IDENTIFIED BY '{1}';
GRANT ALL PRIVILEGES ON simsoexp.* TO {0}@localhost;
FLUSH PRIVILEGES;""".format(user, password)

f = open("setup_db.sql", "w+")
f.write(dbcontent)
f.close()

import os
os.system('mysql -u root --password={0} -e "source setup_db.sql"'.format(rootpassword))
os.system("rm setup_db.sql")

print("Database created ! ")