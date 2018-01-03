kiskadee development
====================

This section is a guide for new developers willing to
set up a development environemnt to start contributing to
kiskadee development. If you have any doubt, please contact
us on IRC in #kiskadee at freenode.

**kiskadee development only suports python versions >= 3. Assume such versions
for all commands run along this documentation.**

Installing dependencies
-----------------------

The name of the dependencies are compatible with the Fedora distribution. If
you use another OS, you will have to find the compatible names
for the dependencies.

`dnf` is Fedora package manager. One should make proper subtitutions when using
another linux distribution.

The `redhat-rpm-config` package, is a specific Fedora dependency, if you do not
use Fedora (or a Red Hat distribution), you may not need to install it.

.. code-block:: bash

  # dnf install gcc openssl-devel python3-devel python3-pip redhat-rpm-config

Creating a python virtual environment with virtualenv
#####################################################

Using virtualenvwrapper
'''''''''''''''''''''''

.. code-block:: bash

  # dnf install python3-virtualenvwrapper python3-virtualenv

After installing the packages above, it is necessary to export some environment
variables.

.. code-block:: bash

  $ export WORKON_HOME=$HOME/.virtualenvs
  $ source /usr/bin/virtualenvwrapper.sh

Note that you may want to add the lines above in your `.bashrc` file.

Then just execute

.. code-block:: bash

  $ mkvirtualenv kiskadee -p python3
  $ workon kiskadee

Using virtualenv
''''''''''''''''

.. code-block:: bash

  # dnf install python3-virtualenvwrapper python3-virtualenv
  $ virtualenv-3 .venv
  $ source bin/activate

**You may need to change the version of the binary file for virtualenv-3.6 or
whatever minor python version you use in your system**

Python dependencies
+++++++++++++++++++

To handle python dependencies, we recommend installing a virtual environment as shown on the
previous subsections. Regardless of how you handle your python pypi dependencies, just run

.. code-block:: bash

  $ pip install -r requirements.txt

to install all kiskadee python related dependencies.
Docker Images
-----------------------

To run the static analyzers, you must have `Docker
<https://www.docker.com/community-edition>`_ installed and running.  If you
have configured the Docker engine properly, run the analyzers target in the
Makefile. It will build the images for you.

.. code-block:: bash

  $ make analyzers

Database
-----------------------

Now we will create the kiskadee database. You will need to install the
postgresql packages for your system. If you use Fedora, follow the next
steps, if not, you will have to find out how install postgresql on your
system.

.. code-block:: bash

  # dnf install postgresql-server postgresql-contrib
  # systemctl enable postgresql
  # postgresql-setup initdb
  # systemctl start postgresql

To install on distributions different from Fedora, refer to their documentation.

With postgresql installed, you will need to create the kiskadee role and
database.

.. code-block:: bash

  # su - postgres
  $ createdb kiskadee
  $ createdb kiskadee_test
  $ createuser kiskadee -P
  $ # here, we use kiskadee as password.
  $ psql -U postgres -c "grant all privileges on database kiskadee to kiskadee"
  $ psql -U postgres -c "grant all privileges on database kiskadee_test to kiskadee"
  # go back to your user (ctrl+d)
  $ echo "localhost:5432:kiskadee:kiskadee:kiskadee" > ~/.pgpass
  $ chmod 600 ~/.pgpass

Restart the postgresql service:

.. code-block:: bash

  # systemctl restart postgresql

Test the database connection:

.. code-block:: bash

  $ psql -U kiskadee -d kiskadee

If you were not able to log in on the database, you will need to edit
the *pg_hba.conf* and change some rules defined by the postgresql package.
On Linux systems this file normally stays at the
`/var/lib/pgsql/data/`. Open this file and change it to:

.. code-block:: bash

  # "local" is for Unix domain socket connections only
  local   all             all                                     md5
  # IPv4 local connections:
  host    all             all             127.0.0.1/32            md5
  # IPv6 local connections:
  host    all             all             ::1/128                 md5


After this change, restart postgresql service:

.. code-block:: bash

  # systemctl restart postgresql

Test the database connection:

.. code-block:: bash

  # psql -U kiskadee -d kiskadee

If you were able to log in the psql shell, the database is properly
configured. Leave the shell with ctrl+d.

Migrations
------------

Kiskadee uses alembic as its tool for database migration, it has a solid
documentation on: http://alembic.zzzcomputing.com/en/latest

For short, the most used commands are:

**To create a new migration**

.. code-block:: bash

  $ alembic revision -m "migration description"

**To autogenerate a new migration**

.. code-block:: bash

  $ alembic revision --autogenerate

or

.. code-block:: bash

  $ alembic revision --autogenerate -m "some migration description"

**To execute the migrations**

.. code-block:: bash

  $ alembic upgrade head
  $ alembic upgrade +2
  $ alembic upgrade -1
  $ alembic upgrade some_revision_id+2

**Downgrading**

.. code-block:: bash

  $ alembic downgrade base

Environment variables
+++++++++++++++++++++

Kiskadee database migration tool(alembic) get its database configuration
from a environment variable named DATABASE_TYPE.
If this variable is not defined, then it will assume its running on a developemnt
environment, but for others environments such as test, homologation or
production be sure to set which one are being used.

Only set DATABASE_TYPE if kiskadee is running on a non development environment.

.. code-block:: bash

  $ export DATABASE_TYPE=db_test

To see which data each one of those alembic will use, check `util/kiskadee.conf`

Running your first analysis
------------------------------

kiskadee reads environment variables from  the `util/kiskadee.conf` file.  Open
the *kiskadee.conf* file, and set the *example_fetcher* as active (`active =
yes`), the other fetchers will stay inactive (`active = no`).

Now run kiskadee by typing `kiskadee` on the terminal (kiskadee must be
installed through `python setup.py install`). If the Docker images were properly
built and the Docker client was properly configured on your machine, kiskadee
will be able to analysis an example source code. This code is in the
*kiskadee/tests/test_source/* directory.

kiskadee will decompress the example source, and run the analyzers defined on
the *kiskadee.conf* file. You can use any postgresql client to access the
database that you have created and check the analysis performed by kiskadee.

## Fetchers

### Debian Fetcher
If you intend to use the debian fetcher, you will have to install the
`devscripts` package to use the necessary Debian tools to run the
fetcher.

### Anitya Fetcher
If you intend to run the anitya fetcher, you will have to install fedmsg-hub
to enable kiskadee to consume the fedmsg events.
To install fedmsg-hub run these commands in kiskadee root path:

.. code-block:: bash

  # Run this inside the kiskadee's virtualenv
  # mkdir -p /etc/fedmsg.d/
  # cp util/base.py util/endpoints.py  /etc/fedmsg.d/
  # cp util/anityaconsumer.py /etc/fedmsg.d/
  $ PYTHONPATH=`pwd` fedmsg-hub

With this steps, fedmsg-hub will instantiate `AnityaConsumer` and publish
the monitored events using ZeroMQ. When kiskadee starts, it will consume
the messages published by the consumer, and will run the analysis.

The events that comes to the anitya fetcher are published by Anitya, on this
`page <https://apps.fedoraproject.org/datagrepper/raw?category=anitya>`_.  For
more info about the Anitya service, read the rest of kiskadee documentation.

Tests and coverage
--------------------

To check kiskadee tests and coverage just run:

.. code-block:: bash

  $ make check

To check kiskadee coverage open the file *covhtml/index.html*.

building docs
--------------------

To build the documentation you need `sphinx` and `sphinx-rtd-theme` installed.
Then, just run

.. code-block:: bash

  $ cd doc
  $ make release

Note that you must be in the `doc` directory

To access the documentation open the `index.html` file, inside doc/_build/html.

Running API
--------------------

To run the kiskadee api just execute the command:

.. code-block:: bash

  $ kiskadee_api
