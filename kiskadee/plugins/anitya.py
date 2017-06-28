"""Plugin to monitor Anitya events related to packages updates."""

import tempfile
import zmq
import yaml
from packaging import version
import fedmsg.consumers
import time
import urllib.request

import kiskadee.helpers
import kiskadee.plugins
import kiskadee.queue


class Plugin(kiskadee.plugins.Plugin):
    """Plugin to monitor Anitya (https://release-monitoring.org) Events."""

    def watch(self):
        """Start the monitoring process for Anitya reports.

        Each package monitored by the plugin will be
        queued using the package_enqueuer decorator.

        The plugin will use zmq as messaging protocol to receive
        the fedmsg-hub events. Kiskadee and fedmsg-hub runs in different
        processes, so we need something to enable the
        comunication between then.  When a message come to fedmsg-hub,
        the AnityaConsumer instance, will publish this event to zmq server,
        and kiskadee will consume this message.

        """
        kiskadee.logger.debug("Starting anitya plugin")
        socket = self._connect_to_zmq(
                self.config["zmq_port"],
                self.config["zmq_topic"])
        if socket:
            while True:
                msg = socket.recv_string()
                self._create_package_dict(msg)

        return {}

    def get_sources(self, source_data):
        """Download packages from some Anitya Backend."""
        path = tempfile.mkdtemp()
        backend_name = source_data.get('meta').get('backend').lower()
        run_backend = self._load_backend(backend_name)
        if run_backend:
            return run_backend(source_data, path)
        else:
            return {}

    def compare_versions(self, new, old):
        """Compare anitya source versions. If new > old, returns true."""
        return version.parse(new) > version.parse(old)

    def _load_backend(self, backend_name):
        try:
            backend = Backends()
            return getattr(backend, backend_name)
        except:
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
    def _create_package_dict(self, msg_as_string):
        msg_as_string = msg_as_string[msg_as_string.find(" ")+1::]
        msg = yaml.load(msg_as_string)
        _msg = msg.get('body').get('msg').get('project')
        source_dict = {}
        if _msg:
            source_dict = {
                    'name': _msg.get('name'),
                    'version': _msg.get('version'),
                    'plugin': kiskadee.plugins.anitya,
                    'meta': {
                        'backend': _msg.get('backend'),
                        'homepage': _msg.get('homepage')
                    }
            }
        return source_dict


class Backends():
    """Class to implement Anitya Backends.

    Each method implemented in this class, should returns a absolute path
    to the downloaded source, or a empty dict if the download could
    not be made.
    """

    def github(self, source_data, path):
        """Backend implementation to download github sources."""
        source_version = ''.join([source_data.get('version'), '.tar.gz'])
        homepage = source_data.get('meta').get('homepage')

        if homepage.find("github") != -1:
            try:
                with kiskadee.helpers.chdir(path):
                    url = ''.join([homepage, '/archive/', source_version])
                    in_file = urllib.request.urlopen(url)
                    data = in_file.read()
                    with open(source_version, 'wb') as info:
                        info.write(data)
                return ''.join([path, '/', source_version])
            except Exception as err:
                kiskadee.logger.debug(
                        "Cannot download {} "
                        "source code".format(source_data["name"])
                )
                kiskadee.logger.debug(err)
                return {}

        return {}


class AnityaConsumer(fedmsg.consumers.FedmsgConsumer):
    """Consumer used by fedmsg-hub to subscribe to fedmsg bus."""

    topic = 'org.release-monitoring.prod.anitya.project.version.update'
    config_key = 'anityaconsumer'
    validate_signatures = False

    def __init__(self, *args, **kw):
        """Anityaconsumer constructor."""
        super().__init__(*args, *kw)
        context = zmq.Context()
        self.socket = context.socket(zmq.PUB)
        self.socket.bind("tcp://*:5556")

    def consume(self, msg):
        """Consume events from fedmsg-hub."""
        self.socket.send_string("%s %s" % ("anitya", str(msg)))
        time.sleep(1)
