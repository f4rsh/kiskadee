"""Provide kiskadee monitoring capabilities.

kiskadee monitors repositories checking for new package versions to be
analyzed. This module provides such capabilities.
"""
import threading
from multiprocessing import Process
import time

import kiskadee.database
import kiskadee.runner
import kiskadee.queue
from kiskadee.model import Package, Plugin, Version, Base

RUNNING = True


class Monitor:
    """Provide kiskadee monitoring objects."""

    def __init__(self):
        """Return a non initialized Monitor."""
        self.engine = None
        self.session = None

    def initialize(self):
        """Start all threads related to the monitoring process.

        This includes all plugins that enqueue packages in the packages_queue,
        and the monitor() method, which retrieves packages from packages_queue,
        and makes the necessary database operations

        .. warning::

            If a plugin does not enqueue the packages in the packages_queue,
            the analysis will never be performed. You can use thee decorator
            `@kiskadee.queue.package_enqueuer` to easiliy enqueue a package.
        """
        database = kiskadee.database.Database()
        self.engine = database.engine
        self.session = database.session
        Base.metadata.create_all(self.engine)
        Base.metadata.bind = self.engine
        _start(self.monitor)
        plugins = kiskadee.load_plugins()
        for plugin in plugins:
            self._save_plugin(plugin)
            _start(plugin.Plugin().watch)
            time.sleep(1)
        _start(kiskadee.runner.runner, True)

    def monitor(self):
        """Dequeue packages and check if they need to be analyzed.

        The packages are dequeued from the `package_queue`. When a package
        needs to be analyzed, this package is enqueued in the `analyses_queue`
        queue so the runner component can trigger an analysis. Each plugin must
        enqueue its packages in the `packages_queue`.
        """
        while RUNNING:
            pkg = self.dequeue()
            if pkg:
                self._save_or_update_pkg(pkg)

    def dequeue(self):
        """Dequeue packages from packages_queue."""
        if not kiskadee.queue.packages_queue.empty():
            pkg = kiskadee.queue.dequeue_package()
            kiskadee.queue.package_done()
            kiskadee.logger.debug("Dequed Package: {}".format(str(pkg)))
            time.sleep(1)
            return pkg
        return {}

    def _save_or_update_pkg(self, pkg):
        _name = self._plugin_name(pkg['plugin'])
        _plugin = self._query(Plugin).filter(Plugin.name == _name).first()
        if _plugin:
            if not self._query(Package).\
                    filter(Package.name == pkg['name']).first():
                self._save_pkg(pkg, _plugin)
            else:
                self._update_pkg_version(pkg)

    def _save_pkg(self, pkg, _plugin):
        _package = Package(name=pkg['name'],
                           plugin_id=_plugin.id)
        _version = Version(number=pkg['version'],
                           package_id=_package.id,
                           has_analysis=False)
        _package.versions.append(_version)
        self.session.add(_package)
        kiskadee.logger.debug("Saving package in db: {}".format(str(pkg)))
        self.session.commit()
        kiskadee.logger.debug(
                "Enqueue package {}_{} "
                " for analysis".format(pkg['name'], pkg['version'])
        )
        kiskadee.queue.enqueue_analysis(pkg)

    def _update_pkg_version(self, pkg):
        _pkg = self._query(Package).filter(Package.name == pkg['name']).first()
        current_pkg_version = _pkg.versions[-1].number

        try:
            if(pkg['plugin'].Plugin().
               compare_versions(pkg['version'], current_pkg_version) == 1):
                _new_version = Version(number=pkg['version'],
                                       package_id=_pkg.id,
                                       has_analysis=False)
                _pkg.versions.append(_new_version)
                self.session.add(_pkg)
                self.session.commit()
                kiskadee.logger.debug(
                        "Enqueue package {}_{}"
                        "for analysis".format(pkg['name'], pkg['version'])
                )
                kiskadee.queue.enqueue_analysis(pkg)
            else:
                return {}
        except ValueError:
            kiskadee.logger.debug("Could not compare versions")

    def _plugin_name(self, plugin):
        return plugin.__name__.split('.')[len(plugin.__name__.split('.')) - 1]

    def _save_plugin(self, plugin):
        name = self._plugin_name(plugin)
        plugin = plugin.Plugin()
        kiskadee.logger.debug("Saving {} plugin in database".format(name))
        if not self.session.query(Plugin).filter(Plugin.name == name).first():
            _plugin = Plugin(name=name,
                             target=plugin.config['target'],
                             description=plugin.config['description'])
            self.session.add(_plugin)
            self.session.commit()

    def _query(self, arg):
        return self.session.query(arg)


def _start(module, joinable=False, timeout=None):
    module_as_a_thread = threading.Thread(target=module)
    module_as_a_thread.daemon = True
    module_as_a_thread.start()
    if joinable or timeout:
        module_as_a_thread.join(timeout)


def daemon():
    """Entry point to the monitor module."""
    # TODO: improve with start/stop system
    monitor = Monitor()
    p = Process(target=monitor.initialize())
    p.daemon = True
    p.start()
    p.join()
    # cleanup goes here
