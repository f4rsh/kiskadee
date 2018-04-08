"""Provide kiskadee queues and operations on them."""
import time
from multiprocessing import Queue

import kiskadee

analysis = Queue()
results = Queue()
packages = Queue()

class Queues():
    """Provide kiskadee queues objects."""

    @staticmethod
    def enqueue_analysis(package_to_analysis):
        """Put a analysis on the analysis queue."""
        log_msg = "MONITOR STATE: Sending package {}-{} for analysis"\
                .format(package_to_analysis['name'],
                        package_to_analysis['version'])
        kiskadee.logger.debug(log_msg)
        analysis.put(package_to_analysis)

    @staticmethod
    def dequeue_analysis():
        """Get a analysis from the analysis queue."""
        package_to_analysis = analysis.get()
        fetcher = package_to_analysis ['fetcher'].split('.')[-1]
        kiskadee.logger.debug(
                'RUNNER STATE: dequeued {}-{} from {}'
                .format(package_to_analysis['name'],
                        package_to_analysis['version'],
                        fetcher)
            )
        return package_to_analysis

    @staticmethod
    def enqueue_result(package):
        """Put a result on the results queue."""
        kiskadee.logger.debug(
                "RUNNER STATE: Sending {}-{} to Monitor"
                .format(package["name"],
                        package["version"])
            )
        results.put(package)

    @staticmethod
    def dequeue_result():
        """Get a result from the results queue."""
        result = results.get()
        kiskadee.logger.debug(
                "MONITOR STATE: Pick Up analyzed package"
                .format(result["name"],
                        result["version"])
            )
        return result

    @staticmethod
    def enqueue_package(package, fetcher=None):
        """Put a result on the results queue."""
        if fetcher:
            kiskadee.logger.debug(
                    "FETCHER {}: sending package {}-{} for monitor"
                    .format(fetcher, package['name'], package['version'])
                )
        packages.put(package)

    @staticmethod
    def dequeue_package():
        """Get a result from the results queue."""
        package = packages.get()
        kiskadee.logger.debug(
                "MONITOR STATE: Pick Up monitored package."
                .format(package["name"],
                        package["version"])
            )
        return package
