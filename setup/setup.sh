apt-get install python-pip
pip install django

sudo ./setup_mysql.sh
python setup_db.py

python manage.py createsuperuser