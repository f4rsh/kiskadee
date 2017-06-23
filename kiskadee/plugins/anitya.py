import tempfile
import zmq
import yaml
from time import sleep
from packaging import version
import fedmsg.consumers
import time
import urllib.request
import kiskadee.helpers

import kiskadee.plugins
import kiskadee.queue

class Plugin(kiskadee.plugins.Plugin):

    def watch(self):
        """Start the monitoring process for Anitya reports.

        Each package monitored by the plugin will be
        queued using the package_enqueuer decorator.

        The plugin will use zmq as messaging protocol to receive
        the fedmsg-hub events. Kiskadee and fedmsg-hub runs in different
        processes, so we need something to enable the comunication between then.
        When a message come to fedmsg-hub, the AnityaConsumer instance, will
        publish this event to zmq server, and kiskadee will consume this message.
        """

        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        kiskadee.logger.debug("Starting anitya plugin")
        socket.connect("tcp://localhost:5556")
        socket.setsockopt(zmq.SUBSCRIBE, b"anitya")
        kiskadee.logger.debug("Connecting to 0mq server")

        while True:
            msg = socket.recv_string()
            msg = msg[msg.find(" ")+1::]
            msg_dict = yaml.load(msg)
            self._create_package_dict(msg_dict)

        return {}

    def get_sources(self, source_data):
        path = tempfile.mkdtemp()
        backend_name = source_data.get('meta').get('backend').lower()
        run_backend = self._load_backend(backend_name)
        if run_backend:
            return run_backend(source_data, path)
        else:
            return {}

    def compare_versions(self, new, old):
        return version.parse(new) > version.parse(old)

    def _load_backend(self, backend_name):
        try:
            backend = Backends()
            return getattr(backend, backend_name)
        except:
            kiskadee.logger.debug("Backend not "\
                    "suported: {}".format(str(backend_name)))
            return {}

    @kiskadee.queue.package_enqueuer
    def _create_package_dict(self, msg):
        return {
                'name': msg.get('body').get('msg').get('project').get('name'),
                'version': msg.get('body').get('msg').get('project').get('version'),
                'plugin': kiskadee.plugins.anitya,
                'meta': {
                    'backend': msg.get('body').get('msg').get('project').get('backend'),
                    'homepage': msg.get('body').get('msg').get('project').get('homepage')
                    }
                }


class Backends():

    @staticmethod
    def github(source_data, path):
        source_version = ''.join([source_data.get('version'), '.tar.gz'])
        homepage = source_data.get('meta').get('homepage')

        if homepage.find("github") != -1:
            with kiskadee.helpers.chdir(path):
                url = ''.join([homepage, '/archive/', source_version])
                in_file = urllib.request.urlopen(url)
                data = in_file.read()
                with open(source_version, 'wb') as info:
                    info.write(data)
            return ''.join([path, '/', source_version])
        else:
            return {}


class AnityaConsumer(fedmsg.consumers.FedmsgConsumer):

    topic = 'org.release-monitoring.prod.anitya.project.version.update'
    config_key = 'anityaconsumer'
    validate_signatures = False

    def __init__(self, *args, **kw):
        super().__init__(*args, *kw)
        context = zmq.Context()
        self.socket = context.socket(zmq.PUB)
        self.socket.bind("tcp://*:5556")

    def consume(self, msg):
        self.socket.send_string("%s %s" % ("anitya", str(msg)))
        time.sleep(1)
