"""Plugin package.

Each kiskadee plugin must be a module in this package that implements the
Plugin class here defined.
"""

import abc
import kiskadee
import inspect


class Plugin():
    """Abstract Plugin class."""

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        """Return a new kiskadee Plugin.

        The plugin name is the module name.
        There MUST be a [PLUGIN_NAME_plugin] section in kiskadee.conf for each
        plugin. Refer to the configuration file documentation for more
        information.
        """
        full_name = inspect.getmodule(self).__name__
        self.name = full_name.split('.')[-1]
        config_section = self.name + '_plugin'
        self.config = kiskadee.config[config_section]

    @abc.abstractmethod
    def get_sources(package):
        """Return the absolute path of compressed package source code.

        `source_data` will be a dictionary previously created by the plugin.
        `source_data` will have at least two obrigatory keys: `name` and
        `version` of the package that have to be downloaded.
        """
        raise NotImplementedError('get_sources must be defined by plugin')

    @abc.abstractmethod
    def watch(self):
        """Continuously monitor some target repository.

        This method will be called as a thread, and will run concurrently with
        the main kiskadee thread.  This method must enqueue packages using the
        `@kiskadee.queue.package_enqueuer` decorator.
        """
        raise NotImplementedError('watch must be defined by plugin')

    @abc.abstractmethod
    def compare_versions(self, new, old):
        """Return *true* if `new` is greater then `old`.

        `new` and `old` will be the versions of packages monitored by your
        plugin.
        """
        raise NotImplementedError('compare_versions must be defined by plugin')

    def analyzers(self):
        """Get active analyzers for current plugin.

        This information should live in kiskadee's configuration file as
        the name of each analyzer separated by spaces.
        """
        if not self.config['analyzers']:
            return kiskadee.config['analyzers'].split()
        else:
            return self.config['analyzers'].split()
