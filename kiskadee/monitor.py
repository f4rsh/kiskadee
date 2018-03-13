"""Provide kiskadee monitoring capabilities.

kiskadee monitors repositories checking for new project versions to be
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
        kiskadee.logger.debug('MONITOR PID: {}'.format(os.getpid()))

        for fetcher in kiskadee.load_fetchers():
            thread = Monitor._start_fetcher(fetcher.Fetcher().watch)

        while RUNNING:
            kiskadee.logger.debug('MONITOR STATE: Idle'.format(os.getpid()))
            new_project = self.dequeue_project_from_fetchers()
            self.send_project_to_runner(new_project)
            analyzed_project = self.dequeue_analysis_from_runner()
            self.save_analyzed_project(analyzed_project)

    def dequeue_project_from_fetchers(self):
        return self.queues.dequeue_project()

    def dequeue_analysis_from_runner(self):
        return self.queues.dequeue_result()

    def send_project_to_runner(self, data):
        if data:
            fetcher, project = self.get_fetcher_and_project(data)
            data["fetcher_id"] = fetcher.id if fetcher else ''
            if not self.is_a_new_project_version(project, data):
                kiskadee.logger.debug('MONITOR STATE: Project {} already'\
                        'analyzed'.format(data['name']))
                return
            self.queues.enqueue_analysis(data)


    def get_fetcher_and_project(self, data):
        fetcher_name = data['fetcher'].split('.')[-1]
        project_name = data['name']
        fetcher = self.db.filter_by_name(Fetcher, fetcher_name)
        project = self.db.filter_by_name(Package, project_name)
        return fetcher, project

    def is_a_new_project_version(self, project, data):
        if project:
            project_version = data['version']
            analysed_version = project.versions[-1].number
            fetcher = importlib.import_module(data['fetcher']).Fetcher()
            return fetcher.compare_versions(project_version, analysed_version)
        else:
            return True

    def save_analyzed_project(self, data):
        if not data:
            return {}
        project = self.db.filter_by_name(Package, data['name'])
        if not project:
            project = Package.save(self.db, data)
        if project:
            project = Package.update(self.db, project, data)

        for analyzer, result in data['results'].items():
            Analysis.save(self.db, data, analyzer, result, project.versions[-1])


    @staticmethod
    def _start_fetcher(module, joinable=False, timeout=None):
        module_as_a_thread = threading.Thread(target=module)
        module_as_a_thread.daemon = True
        module_as_a_thread.start()
        if joinable or timeout:
            module_as_a_thread.join(timeout)
