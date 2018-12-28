# Proxi

Proxi is a proximity messaging service.
Your messages will be displayed to people around you, and the messages you see were posted by people nearby.
You want to know if there is an open bakery around? Just ask! 

Try it! https://prxi.net/

## Getting started

### Installing

Proxi uses GeoDjango and PostgreSQL with PostGis as backend. We show how to set-up a virtualenv and set-up the database on Debian.

#### Create a virtual env

```
sudo apt install virtualenv
virtualenv -p python3 proxi_env
cd proxi_env
source bin/activate
```

#### Clone source

```
mkdir src
cd src
git clone https://github.com/paulez/proxi.git
```

#### Set-up postgis

```
sudo apt install postgis
sudo -u postgres createuser proxydb
sudo -u postgres createdb -E UTF8 -O proxydb proxydb
sudo -u postgres psql -c "ALTER USER proxydb WITH PASSWORD 'choose_a_random_password';"
sudo -u postgres psql --dbname=proxydb -c "CREATE EXTENSION postgis;"
sudo -u postgres psql --dbname=proxydb -c "CREATE EXTENSION postgis_topology;"
```

To be able to run tests the database user needs to have super user permissions to setup the test database.

```
sudo -u postgres psql -c "ALTER ROLE proxydb SUPERUSER";
```

### Install dependencies

```
cd proxi
sudo apt install build-essential python3-dev libgeoip-dev zlib1g-dev libmemcached-dev
pip install -r doc/pip_requirements.txt
```

### Create the configuration file

Create a configuration file from the sample.

```
cp proxy/settings.ini.sample proxy/settings.ini
```

Edit the file, and set DB_PASSWORD with the database user password created above.

Run the django_secret_key script and use the output to set the SECRET_KEY parameter.

```
./utils/django_secret_key.py
```

#### Install the database and run server

```
./manage.py migrate
./manage.py runsslserver "0.0.0.0:8000"
```
#### Run tests

```
./manage.py test -v 2
```

### Front-end

The front-end uses React. We need npm to run it.

#### Install

Follow npm install instructions at https://nodejs.org/en/download/package-manager/#debian-and-ubuntu-based-linux-distributions-enterprise-linux-fedora-and-snap-packages

Install dependencies using npm.

```
cd frontend
npm install
```

#### Run

```
npm start
```

### Test

The backend and frontend development servers both use self signed SSL certificates. You need to add exceptions for your browser to use them. Connect to https://localhost:8000/ and https://localhost:3000/ and add the exception for those certifications.

Now you can test the application at https://localhost:3000/

## Authors

* **Paul Ezvan**

## License

This project is licensed under the GNU Affero General Public License version 3 - see the [LICENSE](LICENSE) file for details
