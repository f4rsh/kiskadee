import tempfile
import importlib
from time import sleep
from packaging import version
import requests
import fedmsg
import fedmsg.config

import kiskadee.plugins
import kiskadee.queue

class Plugin(kiskadee.plugins.Plugin):

    def watch(self):
        """Start the monitoring process for Anitya reports.

        Each package monitored by the plugin will be
        queued using the package_enqueuer decorator.
        """

        config = fedmsg.config.load_config([], None)
        config["endpoints"] = { "anitya-public-relay": [
                        "tcp://release-monitoring.org:9940",
                        ],
                    }
        config['mute'] = True
        config['timeout'] = 0

        for name, endpoint, topic, msg in fedmsg.tail_messages(**config):
            self._create_package_dict(msg)

    def get_sources(self, source_data):
        path = tempfile.mkdtemp()
        backend_name = source_data.get('meta').get('backend').lower()
        backend = self._load_backend(backend_name)
        if backend:
            return backend.download_source(source_data, path)
        else:
            return {}

    def compare_versions(self, new, old):
        return version.parse(new) > version.parse(old)

    @kiskadee.queue.package_enqueuer
    def _create_package_dict(self, message):
        return {
                'name': message.get('msg').get('project').get('name'),
                'version': message.get('msg').get('project').get('version'),
                'plugin': kiskadee.plugins.anitya,
                'meta': {
                    'backend': message.get('msg').get('project').get('backend'),
                    'homepage': message.get('msg').get('project').get('homepage')
                    }
                }

    def _load_backend(self, backend_name):
        try:
            return importlib.import_module(''.join(['kiskadee.plugins.anitya_',
            backend_name]))
        except:
            kiskadee.logger.info("Backend not "\
                    "suported: {}".format(str(backend_name)))
            return {}
