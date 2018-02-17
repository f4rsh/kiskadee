"""Provide kiskadee monitoring capabilities.

kiskadee monitors repositories checking for new package versions to be
analyzed. This module provides such capabilities.
"""
import threading
from multiprocessing import Process
import time
import os
import importlib

import kiskadee.database
from kiskadee.runner import Runner
import kiskadee.queue
from kiskadee.model import Package, Fetcher, Version, Report, Analysis

RUNNING = True

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
                self.send_to_runner(pkg)
            time.sleep(2)
            analyzed_project = self.kiskadee_queue.dequeue_result()
            self.save_analyzed_project(analyzed_project)

    def send_to_runner(self, data):
        _name = data['fetcher'].split('.')[-1]
        _fetcher = self._query(Fetcher).filter_by(name = _name).first()
        _package = self._query(Package).filter_by(name = data['name']).first()

        if _fetcher:
            data["fetcher_id"] = _fetcher.id
            if not _package:
                kiskadee.logger.debug(
                        "MONITOR: Sending package {}_{} "
                        " for analysis".format(data['name'], data['version'])
                )
                self.kiskadee_queue.enqueue_analysis(data)
            else:
                new_version = data['version']
                analysed_version = _package.versions[-1].number
                fetcher = importlib.import_module(data['fetcher']).Fetcher()
                if (fetcher.compare_versions(new_version, analysed_version)):
                    self.kiskadee_queue.enqueue_analysis(data)

    def save_analyzed_project(self, data):
        if not data:
            return {}
        project = self._query(Package).filter_by(name = data['name']).first()
        if not project:
            project = Package.save(self.session, data)
        if project:
            project = Package.update(self.session, project, data)

        for analyzer, result in data['results'].items():
            Analysis.save(self.session, data, analyzer, result, project.versions[-1])

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
            args=(queues,)
        )
    runner_process = Process(
            target=runner.runner,
            args=(queues,)
        )
    monitor_process.start()
    runner_process.start()
    runner_process.join()
