import kiskadee.plugins
import kiskadee.queue
import requests
import fedmsg
import fedmsg.config
from time import sleep


class Plugin(kiskadee.plugins.Plugin):
    def __init__(self):
        """Loads from /etc/fedmsg.d/endpoints.py the anitya configuration"""
        super().__init__()
        fedmsg.config.load_config()


    def watch(self):
        """Start the monitoring process for Anitya reports.

        Each package monitored by the plugin will be
        queued using the package_enqueuer decorator.
        """
        while True:
            self._get_messages()

    def get_sources(self, source_data):
        return {}

    def _get_messages(self):
        """Get messages published on fedmsg"""

        for name, endpoint, topic, msg in fedmsg.tail_messages():
            print(msg.get('msg').get('project'))
            self._create_package_dict(msg)

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
