"""Provide kiskadee monitoring capabilities.

kiskadee monitors repositories checking for new project versions to be
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

    def __init__(self, _session, queues):
        """Return a non initialized Monitor."""
        self.session = _session
        self.queues = queues
        kiskadee.model.Analyzer.create_analyzers(self.session)

    def start(self):
        kiskadee.logger.debug('Monitor PID: {}'.format(os.getpid()))

        for fetcher in kiskadee.load_fetchers():
            thread = Monitor._start_fetcher(fetcher.Fetcher().watch)

        while RUNNING:
            new_project = self.dequeue_project_from_fetchers()
            self.send_project_to_runner(new_project)
            analyzed_project = self.dequeue_analysis_from_runner()
            self.save_analyzed_project(analyzed_project)

    def dequeue_project_from_fetchers(self):
        new_project = self.queues.dequeue_project()
        return new_project if new_project else {}

    def dequeue_analysis_from_runner(self):
        return self.queues.dequeue_result()

    def send_project_to_runner(self, data):
        if data:
            fetcher, project = self.get_fetcher_and_project(data)
            data["fetcher_id"] = fetcher.id if fetcher else ''
            if not project:
                self.queues.enqueue_analysis(data)
            elif self.is_a_new_project_version(project, data):
                self.queues.enqueue_analysis(data)

    def get_fetcher_and_project(self, data):
        fetcher_name = data['fetcher'].split('.')[-1]
        project_name = data['name']
        fetcher = self._query(Fetcher).filter_by(name = fetcher_name).first()
        project = self._query(Package).filter_by(name = project_name).first()
        return fetcher, project

    def is_a_new_project_version(self, project, data):
        project_version = data['version']
        analysed_version = project.versions[-1].number
        fetcher = importlib.import_module(data['fetcher']).Fetcher()
        fetcher.compare_versions(project_version, analysed_version)

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


    @staticmethod
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
    monitor = Monitor(session, queues)
    runner = Runner(queues)
    monitor_process = Process(
            target=monitor.start,
        )
    runner_process = Process(
            target=runner.runner,
        )
    monitor_process.start()
    runner_process.start()
    runner_process.join()
