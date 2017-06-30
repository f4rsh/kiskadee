# kiskadee

kiskadee is a continuous static analysis tool which writes the analyses results
into a Firehose database.

## Running

To run kiskadee, you must have docker installed and running. Use the
dockerfiles in the util directory to build the containers for each static
analyzer.

If you are using distribution with selinux, be aware that you must set
permissions so the container can access external files.

kiskadee looks for its configuration file under `/etc/kiskadee.conf`.

### Anitya Plugin
If you intend to run the anitya plugin, you will have to install fedmsg-hub,
in order to kiskadee be able to consume the fedmsg events.
To install fedmsg-hub follow this steps inside the kiskadee root path:

    sudo mkdir -p /etc/fedmsg.d/
    sudo cp util/base.py util/endpoints.py  /etc/fedmsg.d/
    sudo cp util/anityaconsumer.py /etc/fedmsg.d/
    pip install -e .
    PYTHONPATH=`pwd` fedmsg-hub

With this steps, fedmsg-hub will instanciate `AnityaConsumer` and publish
the monitored events using ZeroMQ. When kiskadee starts it will consume
the messages published by the consumer, and will run the analysis.

### Debian Plugin
If you intend to use the debian plugin, you will have to install the
`devscripts` package, in order use the necessary debian tools to run the
plugin.

## Development

kiskadee development is hosted at [pagure](https://pagure.io/kiskadee). Feel
free to open issues and pull requests there.

kiskadee dependencies are listed in requirements.txt. To install them, just run
`pip install -e .`

## Documentation

[kiskadee documentation is hosted at pagure.](docs.pagure.org/kiskadee)

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
