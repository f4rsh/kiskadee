"""Fetcher to monitor Anitya events related to packages updates."""

import tempfile
import zmq
import yaml
from packaging import version
import fedmsg.consumers
import time

import kiskadee.fetchers
import kiskadee.queue


class Fetcher(kiskadee.fetchers.Fetcher):
    """Fetcher to monitor Anitya (https://release-monitoring.org) Events."""

    def watch(self):
        """Start the monitoring process for Anitya reports.

        Each package monitored by the fetcher will be
        queued using the package_enqueuer decorator.

        The fetcher will use zmq as messaging protocol to receive
        the fedmsg-hub events. kiskadee and fedmsg-hub runs in different
        processes, so we need something to enable the
        comunication between then.  When a message come to fedmsg-hub,
        the AnityaConsumer instance, will publish this event to zmq server,
        and kiskadee will consume this message.

        """
        kiskadee.logger.debug("Starting anitya fetcher")
        socket = self._connect_to_zmq(
                self.config["zmq_port"],
                self.config["zmq_topic"])
        if socket:
            while True:
                msg = socket.recv_string()
                self._create_package_dict(msg)

    def get_sources(self, source_data):
        """Download packages from some Anitya Backend."""
        tmp_path = tempfile.gettempdir()
        path = tempfile.mkdtemp(dir=tmp_path)
        backend_name = source_data.get('meta').get('backend').lower()
        run_backend = self._load_backend(backend_name)
        if run_backend:
            return run_backend(self, source_data, path)
        else:
            return {}

    def compare_versions(self, new, old):
        """Compare anitya source versions. If new > old, returns true."""
        return version.parse(new) > version.parse(old)

    def _load_backend(self, backend_name):
        try:
            backend = Backends()
            return getattr(backend, backend_name)
        except Exception:
            kiskadee.logger.debug(
                    "Backend not suported: {}".format(str(backend_name))
            )
            return {}

    def _connect_to_zmq(self, port, topic):
        try:
            context = zmq.Context()
            socket = context.socket(zmq.SUB)
            socket.connect("tcp://localhost:{}".format(port))
            socket.setsockopt_string(
                    zmq.SUBSCRIBE, topic)
            kiskadee.logger.debug("Connecting to 0mq server")
            return socket
        except Exception as err:
            kiskadee.logger.debug("Could not connect to zmq server")
            kiskadee.logger.debug(err)
            return False

    @kiskadee.queue.package_enqueuer
    def _create_package_dict(self, fedmsg_event):
        event = self._event_to_dict(fedmsg_event)
        if event:
            project = event.get('body').get('msg').get('project')
            source_dict = {}
            if project:
                source_dict = {
                        'name': project.get('name'),
                        'version': project.get('version'),
                        'fetcher': kiskadee.fetchers.anitya.Fetcher(),
                        'meta': {
                            'backend': project.get('backend'),
                            'homepage': project.get('homepage')
                        }
                }
            return source_dict

    def _event_to_dict(self, msg):
        msg = msg[msg.find(" ")+1::]
        event = None
        try:
            event = yaml.load(msg)
            return event
        except Exception as err:
            kiskadee.logger.debug("Something went wrong on Anitya event")
            kiskadee.logger.debug(err)
            return event


class Backends():
    """Class to implement Anitya Backends.

    Each method implemented in this class, should return an absolute path
    to the downloaded source, or a empty dict if the download could
    not be made.
    """

    def github(self, fetcher, source_data, path):
        """Backend implementation to download github sources."""
        source_version = ''.join([source_data.get('version'), '.tar.gz'])
        homepage = source_data.get('meta').get('homepage')
        url = ''.join([homepage, '/archive/', source_version])
        return fetcher.download(path, url, source_version)


class AnityaConsumer(fedmsg.consumers.FedmsgConsumer):
    """Consumer used by fedmsg-hub to subscribe to fedmsg bus."""

    topic = 'org.release-monitoring.prod.anitya.project.version.update'
    config_key = 'anityaconsumer'
    validate_signatures = False

    def __init__(self, *args, **kw):
        """Anityaconsumer constructor."""
        super().__init__(*args, **kw)
        context = zmq.Context()
        self.socket = context.socket(zmq.PUB)
        self.socket.bind("tcp://*:5556")

    def consume(self, msg):
        """Consume events from fedmsg-hub."""
        self.socket.send_string("%s %s" % ("anitya", str(msg)))
        time.sleep(1)
