"""Provide kiskadee monitoring capabilities.

kiskadee monitors repositories checking for new package versions to be
analyzed. This module provides such capabilities.
"""
import threading
from multiprocessing import Process
import time
import os
import json
import importlib

import kiskadee.database
from kiskadee.report import CppcheckReport, FlawfinderReport
from kiskadee.runner import Runner
import kiskadee.queue
from kiskadee.model import Package, Fetcher, Version, Report

RUNNING = True

REPORTERS = {
    'cppcheck': CppcheckReport,
    'flawfinder': FlawfinderReport
}

class Monitor:
    """Provide kiskadee monitoring objects."""

    def __init__(self, _session):
        """Return a non initialized Monitor."""
        self.session = _session
        self.kiskadee_queue = None

    def monitor(self, queues):
        """Dequeue packages and check if they need to be analyzed.

        The packages are dequeued from the `package_queue`. When a package
        needs to be analyzed, this package is enqueued in the `analyses_queue`
        so the runner component can trigger an analysis.  Each fetcher must
        enqueue its packages in the `packages_queue`.
        """
        kiskadee.logger.debug('kiskadee PID: {}'.format(os.getppid()))
        kiskadee.logger.debug('Starting monitor subprocess')
        kiskadee.logger.debug('monitor PID: {}'.format(os.getpid()))

        for fetcher in kiskadee.load_fetchers():
            _start_fetcher(fetcher.Fetcher().watch)

        while RUNNING:
            self.kiskadee_queue = queues
            pkg = self.kiskadee_queue.dequeue_project()

            if pkg:
                self._send_to_runner(pkg)
            time.sleep(2)
            analyzed_project = self.queues.dequeue_result()
            self._save_analyzed_project(analyzed_project)

    def dequeue_package(self):
        """Dequeue packages from packages_queue."""
        if not kiskadee.queue.packages_queue.empty():
            pkg = kiskadee.queue.packages_queue.get()
            kiskadee.logger.debug(
                    "MONITOR: Dequed Package: {}_{}"
                    .format(pkg["name"], pkg["version"])
                )
            return pkg
        return {}

    # Use directly dequeue_result from kiskadee.queue
    #def dequeue_result(self):
    #    """Dequeue analyzed packages from result_queue."""
    #    if not self.kiskadee_queue.results_empty():
    #        pkg = self.kiskadee_queue.dequeue_result()
    #        kiskadee.logger.debug(
    #                "MONITOR: Dequed result for package : {}-{}"
    #                .format(pkg["name"], pkg["version"])
    #            )
    #        return pkg
    #    return {}

    def _send_to_runner(self, pkg):
        _name = pkg['fetcher'].split('.')[-1]
        _fetcher = self._query(Fetcher).filter_by(name = _name).first()
        _package = (
                self._query(Package)
                .filter(Package.name == pkg['name']).first()
            )

        if _fetcher:
            pkg["fetcher_id"] = _fetcher.id
            if not _package:
                kiskadee.logger.debug(
                        "MONITOR: Sending package {}_{} "
                        " for analysis".format(pkg['name'], pkg['version'])
                )
                self.kiskadee_queue.enqueue_analysis(pkg)
            else:
                new_version = pkg['version']
                analysed_version = _package.versions[-1].number
                fetcher = importlib.import_module(pkg['fetcher']).Fetcher()
                if (fetcher.compare_versions(new_version, analysed_version)):
                    self.kiskadee_queue.enqueue_analysis(pkg)

    # Move this to model.py
    def _save_analyzed_project(self, project):
        if not pkg:
            return {}
        project = self._query(Package).filter_by(name = data['name']).first()
        if not project:
            project = self._save_project(data)
        if project:
            project = self._update_project(project, data)

        for analyzer, result in data['results'].items():
            self._save_analysis(data, analyzer, result, project.versions[-1])

    # Move this to model.py
    def _update_pkg(self, package, pkg):

        if(package.versions[-1].number == pkg['version']):
            return package
        try:
            _new_version = Version(
                    number=pkg['version'],
                    package_id=package.id
                    )
            package.versions.append(_new_version)
            self.session.add(package)
            self.session.commit()
            kiskadee.logger.debug(
                    "MONITOR: Sending package {}_{}"
                    "for analysis".format(pkg['name'], pkg['version'])
                    )
            return package
        except ValueError:
            kiskadee.logger.debug("MONITOR: Could not compare versions")
            return None

    # Move this to model.py
    def _save_pkg(self, pkg):
        homepage = None
        if ('meta' in pkg) and ('homepage' in pkg['meta']):
            homepage = pkg['meta']['homepage']

        _package = Package(
                name=pkg['name'],
                homepage=homepage,
                fetcher_id=pkg['fetcher_id']
                )
        self.session.add(_package)
        self.session.commit()
        _version = Version(number=pkg['version'],
                           package_id=_package.id)
        self.session.add(_version)
        self.session.commit()
        return _package

    # Move this to model.py
    def _save_reports(self, analysis, pkg, analyzer_name):
        try:
            results = analysis['results']
            analyzer_report = REPORTERS[analyzer_name](results)
            _reports = Report()
            _reports.results = json.dumps(
                    analyzer_report
                    ._compute_reports(analyzer_name)
                )
            _reports.analysis_id = analysis['id']
            self.session.add(_reports)
            self.session.commit()
            kiskadee.logger.debug(
                    "MONITOR: Saved analysis reports for {} package"
                    .format(pkg["name"])
                )
        except KeyError as key:
            kiskadee.logger.debug(
                    "ERROR: There's no reporter " +
                    "to get reports from {} analyzer. ".format(key) +
                    "Make shure to import or implement them."
                )
        except Exception as err:
            kiskadee.logger.debug(
                    "MONITOR: Failed to get analysis reports to {} package"
                    .format(pkg["name"])
                )
            kiskadee.logger.debug(err)
        return

    # Move this to model.py
    def _save_analysis(self, pkg, analyzer, result, version):
        _analysis = kiskadee.model.Analysis()
        try:
            _analyzer = self._query(kiskadee.model.Analyzer).\
                    filter_by(name = analyzer).first()
            _analysis.analyzer_id = _analyzer.id
            _analysis.version_id = version.id
            _analysis.raw = json.loads(result)
            self.session.add(_analysis)
            self.session.commit()
            dict_analysis = {
                    'results': _analysis.raw['results'],
                    'id': _analysis.id
                }
            self._save_reports(dict_analysis, pkg, _analyzer.name)
            kiskadee.logger.debug(
                    "MONITOR: Saved analysis done by {} for package: {}-{}"
                    .format(analyzer, pkg["name"], pkg["version"])
                )
            return
        except Exception as err:
            kiskadee.logger.debug(
                    "MONITOR: The required analyzer was " +
                    "not registered in kiskadee"
                )
            kiskadee.logger.debug(err)
            return None

    # Move this to model.py
    def _save_fetcher(self, fetcher):
        name = fetcher.name
        kiskadee.logger.debug(
                "MONITOR: Saving {} fetcher in database".format(name)
            )
        if not self.session.query(Fetcher)\
                .filter(Fetcher.name == name).first():
            _fetcher = Fetcher(
                    name=name,
                    target=fetcher.config['target'],
                    description=fetcher.config['description']
                )
            self.session.add(_fetcher)
            self.session.commit()

    def _query(self, arg):
        return self.session.query(arg)


def _start_fetcher(module, joinable=False, timeout=None):
    module_as_a_thread = threading.Thread(target=module)
    module_as_a_thread.daemon = True
    module_as_a_thread.start()
    if joinable or timeout:
        module_as_a_thread.join(timeout)


def daemon():
    """Entry point to the monitor module."""
    # TODO: improve with start/stop system
    queues = kiskadee.queue.Queues()
    session = kiskadee.database.Database().session
    monitor = Monitor(session)
    runner = Runner()
    monitor_process = Process(
            target=monitor.monitor,
            args=(queues)
        )
    runner_process = Process(
            target=runner.runner,
            args=(queues)
        )
    monitor_process.start()
    runner_process.start()
    runner_process.join()
