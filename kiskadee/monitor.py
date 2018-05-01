"""Provide kiskadee monitoring capabilities.

kiskadee monitors repositories checking for new package versions to be
analyzed. This module provides such capabilities.
"""
import threading
import time
import os
import importlib

import kiskadee
from kiskadee.model import Package, Fetcher, Version, Report, Analysis, Analyzer

RUNNING = True

class Monitor:
    """Provide kiskadee monitoring objects."""

    def __init__(self, db, queues):
        """Return a non initialized Monitor."""
        self.db = db
        self.queues = queues
        Analyzer.create_analyzers(self.db)

    def run(self):
        """Run Monitor process. This method resumes Monitor behavior. It dequeue
        packages from fetchers, check if the package is valid and if so send it
        to Runner. When Runner ends a analysis, the Monitor dequeue the analysis
        and save it on database. """
        kiskadee.logger.debug('MONITOR PID: {}'.format(os.getpid()))

        for fetcher in kiskadee.load_fetchers():
            thread = Monitor.start_fetcher(fetcher.Fetcher().watch)

        while RUNNING:
            kiskadee.logger.debug('MONITOR STATE: Idle'.format(os.getpid()))
            new_package = self.dequeue_package_from_fetchers()
            self.send_package_to_runner(new_package)
            analyzed_package = self.dequeue_analysis_from_runner()
            self.save_analyzed_package(analyzed_package)

    def dequeue_package_from_fetchers(self):
        return self.queues.dequeue_package()

    def dequeue_analysis_from_runner(self):
        return self.queues.dequeue_result()

    def send_package_to_runner(self, data):
        if data:
            fetcher, package = self.get_fetcher_and_package(data)
            data["fetcher_id"] = fetcher.id if fetcher else ''
            if not self.is_a_new_package_version(package, data):
                kiskadee.logger.debug('MONITOR STATE: Package {} already'\
                        ' analyzed'.format(data['name']))
                return
            self.queues.enqueue_analysis(data)


    def get_fetcher_and_package(self, data):
        fetcher_name = data['fetcher'].split('.')[-1]
        package_name = data['name']
        fetcher = self.db.filter_by_name(Fetcher, fetcher_name)
        package = self.db.filter_by_name(Package, package_name)
        return fetcher, package

    def is_a_new_package_version(self, package, data):
        if package:
            package_version = data['version']
            analysed_version = package.versions[-1].number
            fetcher = importlib.import_module(data['fetcher']).Fetcher()
            return fetcher.compare_versions(package_version, analysed_version)
        else:
            return True

    def save_analyzed_package(self, data):
        if not data:
            return {}
        package = self.db.filter_by_name(Package, data['name'])
        if not package:
            new_package = Package.save(self.db, data)
            self.save_package_analysis(data, new_package)
        else:
            updated_package = Package.update(self.db, package, data)
            self.save_package_analysis(data, updated_package)

    def save_package_analysis(self, data, package):
        for analyzer, result in data['results'].items():
            Analysis.save(self.db, analyzer, result, package)


    @staticmethod
    def start_fetcher(module, joinable=False, timeout=None):
        """Start a fetcher as a thread of the Monitor process."""
        module_as_a_thread = threading.Thread(target=module)
        module_as_a_thread.daemon = True
        module_as_a_thread.start()
        if joinable or timeout:
            module_as_a_thread.join(timeout)
