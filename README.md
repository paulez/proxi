# Proxi

Proxi is a proximity messaging service.
Your messages will be displayed to people around you, and the messages you see were posted by people around.
You want to know if there is an open bakery around? Just ask! 

## Getting started

### Installing

Proxi uses GeoDjango and PostgreSQL with PostGis as backend. We show how to set-up a virtualenv and set-up the database on Debian.

#### Create a virtual env

```virtualenv -p /usr/bin/python3 proxi_env/
cd proxi_env
source bin/activate
```

#### Clone source

```
mkdir src
cd src
git https://github.com/paulez/proxi.git
```

#### Set-up postgis

```
sudo apt-get install postgis
sudo -u postgres createuser proxydb
sudo -u postgres createdb -E UTF8 -O proxydb proxydb
sudo -u postgres psql
ALTER USER proxydb WITH PASSWORD 'password';
sudo -u postgres psql --dbname=proxydb -c "CREATE EXTENSION postgis;"
sudo -u postgres psql --dbname=proxydb -c "CREATE EXTENSION postgis_topology;"
```

#### Install the database and run server

```
cd proxi
./manage.py migrate
./manage.py runsslserver "0.0.0.0:8000"
```

## Authors

* **Paul Ezvan**

## License

This project is licensed under the GNU Affero General Public License version 3 - see the [LICENSE](LICENSE) file for details
