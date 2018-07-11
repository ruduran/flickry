Service to download and browse Flickr images given some tag lists.

## Setup

### Database

A MySQL/MariaDB database is required in order to run the service.
```sql
CREATE DATABASE flickry CHARACTER SET utf8;
CREATE USER 'flickryuser'@'localhost' IDENTIFIED BY 'flickrypassword';
GRANT ALL PRIVILEGES ON flickry.* TO flickryuser@localhost;
FLUSH PRIVILEGES;
```

### System

We'll probably need to install the Python and MySQL development headers.

For instance, on Debian/Ubuntu:
```
sudo apt-get install python-dev default-libmysqlclient-dev
```

For other platforms, please check [this link](https://pypi.org/project/mysqlclient/).

### Python

The easiest way is to work with a virtualenv.
```
virtualenv -p python3.6 venv
. venv/bin/activate
pip install -U -r requirements.txt -r test-requirements.txt
```

### Service

Before starting the service, we need to setup the DB:
```
# Inside the flickry/ dir
python manage.py migrate
```

The API key/secret for Flickr need to be added to the settings. If the DB configuration has changes, we also need to update it.
The settings file is located in `flickry/flickry/settings.py`, inside it we'll find the *DATABASES* and *FLICKR* sections.

## Start the service

Once everything is ready, we can run the service:
```
python manage.py runserver
```

## Run the tests

We'll need to give our user access to the test DB:
```sql
GRANT ALL PRIVILEGES ON test_flickry.* TO flickryuser@localhost;
FLUSH PRIVILEGES;
```

Once that is done we can run the tests:
```
python manage.py test
```

We can also run flake8 to check the code style and PEP8 compliance.
```
flake8
```
