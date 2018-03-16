"""Provide kiskadee queues and operations on them."""
import time
from multiprocessing import Queue

import kiskadee

analysis = Queue()
results = Queue()
projects = Queue()

class Queues():
    """Provide kiskadee queues objects."""

    @staticmethod
    def enqueue_analysis(project_to_analysis):
        """Put a analysis on the analysis queue."""
        log_msg = "MONITOR STATE: Sending project {}-{} for analysis"\
                .format(project_to_analysis['name'],
                        project_to_analysis['version'])
        kiskadee.logger.debug(log_msg)
        analysis.put(project_to_analysis)

    @staticmethod
    def dequeue_analysis():
        """Get a analysis from the analysis queue."""
        project_to_analysis = analysis.get()
        fetcher = project_to_analysis ['fetcher'].split('.')[-1]
        kiskadee.logger.debug(
                'RUNNER STATE: dequeued {}-{} from {}'
                .format(project_to_analysis['name'],
                        project_to_analysis['version'],
                        fetcher)
            )
        return project_to_analysis

    @staticmethod
    def enqueue_result(project):
        """Put a result on the results queue."""
        kiskadee.logger.debug(
                "RUNNER STATE: Sending {}-{} to Monitor"
                .format(project["name"],
                        project["version"])
            )
        results.put(project)

    @staticmethod
    def dequeue_result():
        """Get a result from the results queue."""
        result = results.get()
        kiskadee.logger.debug(
                "MONITOR STATE: Pick Up analyzed project"
                .format(result["name"],
                        result["version"])
            )
        return result

    @staticmethod
    def enqueue_project(project, fetcher=None):
        """Put a result on the results queue."""
        if fetcher:
            kiskadee.logger.debug(
                    "FETCHER {}: sending package {}-{} for monitor"
                    .format(fetcher, project['name'], project['version'])
                )
        projects.put(project)

    @staticmethod
    def dequeue_project():
        """Get a result from the results queue."""
        project = projects.get()
        kiskadee.logger.debug(
                "MONITOR STATE: Pick Up monitored project."
                .format(project["name"],
                        project["version"])
            )
        return project
