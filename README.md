# kiskadee

kiskadee is a continuous static analysis tool which writes the analysis results
into a Firehose database.

## Setup

### Dependencies

The name of the dependencies are compatible
with the Fedora distribution. If you use another operational system,
you will have to find the compatible names for the dependencies.
The `redhat-rpm-config`
package, is a specific Fedora dependency, if you not use Fedora (or a
Red Hat distribution), maybe you will not have to install it.

`dnf` is a package manager for the Fedora distribution
(On Debian and Ubuntu is apt),
if you not use Fedora, use the package manager available for your system,
to install the dependencies below.

     - openssl-devel
     - python3-devel
     - gcc
     - redhat-rpm-config python-pip
     - python-pip

### Virtual Environment

Create a [virtualenv](https://virtualenv.pypa.io/en/stable/) to kiskadee.
The virtualenv package will create a isolated environment
for our python dependencies.

    sudo pip install virtualenv
    virtualenv -p /usr/bin/python3 .
    source bin/activate

Install the python dependencies using pip

    pip install -e .
    pip install "fedmsg[consumers]"

### Docker Images

To run the static analyzers, you must have
[Docker](https://www.docker.com/community-edition) installed and running.
If you have configured the Docker engineer properly,
run the *docker_build.sh* script. It will build the images for you.

	chmod u+x docker_build.sh
	./docker_build.sh

### Database
Now we will create the kiskadee database. You will need to install the
postgresql packages for your system. If you use Fedora, follow the next
steps, if not, you will have to find out how install postgresql on your
system.

	sudo dnf install postgresql-server postgresql-contrib
	sudo systemctl enable postgresql
	sudo postgresql-setup initdb
	sudo systemctl start postgresql

To install on Ubuntu use this [link](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-16-04).

With postgresql installed, you will need to create the kiskadee role and
database.

    sudo su - postgres
    createdb kiskadee
    createuser kiskadee -P
    # use kiskadee as password.
    psql -U postgres -c "grant all privileges on database kiskadee to kiskadee"
    # go back to your user (ctrl+d)
    echo "localhost:5432:kiskadee:kiskadee:kiskadee" > ~/.pgpass
    chmod 600 ~/.pgpass

Restart the postgresql service:

	sudo systemctl restart postgresql

Test the database connection:

	psql -U kiskadee -d kiskadee

If you was not able to log in on the database, you will need to edit
the *pg_hba.conf* and change some rules defined by the postgresql package.
On Linux systems this file normally stays at the
`/var/lib/pgsql/data/`. Open this file and change:

	# "local" is for Unix domain socket connections only
	local   all             all                                     peer
	# IPv4 local connections:
	host    all             all             127.0.0.1/32            ident
	# IPv6 local connections:
	host    all             all             ::1/128                 ident

to:

	# "local" is for Unix domain socket connections only
	local   all             all                                     md5
	# IPv4 local connections:
	host    all             all             127.0.0.1/32            md5
	# IPv6 local connections:
	host    all             all             ::1/128                 md5


After this change, restarts the postgresql service:

	sudo systemctl restart postgresql

Test the database connection:

	psql -U kiskadee -d kiskadee

If you was able to get into the psql shell, the database is properly
configured. Leave the shell with ctrl+d.

### Running our first analysis

Kiskadee reads environment variables from  the `util/kiskadee.conf` file.
If everything goes well till now, open the *kiskadee.conf* file, and set as
active (`active = yes`) only the *example_fetcher*, the other fetchers will
stay as `active = no`.

Now run kiskadee by typing `kiskadee` on
the terminal. If the Docker images was properly build, and the Docker client
was properly configured on your machine, kiskadee will be able to analysis a
example source code. This code is in the *kiskadee/tests/test_source/* directory.

Kiskadee will decompress the example source, and run the analyzers defined on
the *kiskadee.conf* file. You can use any postgresql client to access the
database that you have created,  and check the analysis maded by kiskadee.

### Running API

To run the kiskadee api just execute the command:

	kiskadee_api

## Tests and coverage

To check kiskadee tests and coverage just run:

	chmod u+x run_tests_and_coverage.sh
	./run_tests_and_coverage.sh

To check kiskadee coverage open the file *covhtml/index.html*.

## Repositories

Kiskadee daemon and API development are hosted at [pagure](https://pagure.io/kiskadee).

Kiskadee frontend is hosted at [pagure](https://pagure.io/kiskadee/kiskadee_ui).
Feel free to open issues and pull requests there.

We also have mirrors on [gitlab](https://gitlab.com/kiskadee/kiskadee) and
[github](https://github.com/LSS-USP/kiskadee).

Kiskadee have a CI environment hosted at this [url](http://143.107.45.126:30130/blue/organizations/jenkins/LSS-USP%2Fkiskadee/activity).

## Documentation

[kiskadee documentation is hosted at pagure.](docs.pagure.org/kiskadee)

To build the documentation just entry in the doc directory, and run

    make html

To access the documentation open the `index.html` file, inside the
doc/\_build/html.

## Fetchers

### Debian Fetcher
If you intend to use the debian fetcher, you will have to install the
`devscripts` package, in order use the necessary Debian tools to run the
fetcher.

### Anitya Fetcher
If you intend to run the anitya fetcher, you will have to install fedmsg-hub,
in order to kiskadee be able to consume the fedmsg events.
To install fedmsg-hub follow this steps inside the kiskadee root path:

    # Run this inside the kiskadee's virtualenv
    sudo mkdir -p /etc/fedmsg.d/
    sudo cp util/base.py util/endpoints.py  /etc/fedmsg.d/
    sudo cp util/anityaconsumer.py /etc/fedmsg.d/
    PYTHONPATH=`pwd` fedmsg-hub

With this steps, fedmsg-hub will instantiate `AnityaConsumer` and publish
the monitored events using ZeroMQ. When kiskadee starts it will consume
the messages published by the consumer, and will run the analysis.

The events that comes to the anitya fetcher are published by Anitya, on this
[page](https://apps.fedoraproject.org/datagrepper/raw?category=anitya.)
For more info about the Anitya service, read kiskadee documentation.


## License
Copyright (C) 2017 the AUTHORS (see the AUTHORS file)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
