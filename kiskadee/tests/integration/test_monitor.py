import unittest
from unittest.mock import MagicMock

from kiskadee.monitor import Monitor
from kiskadee.queue import Queues
from kiskadee.model import Package, Fetcher
import kiskadee.queue
import kiskadee.fetchers.debian
import kiskadee.fetchers.anitya
import kiskadee.fetchers.example


class MonitorTestCase(unittest.TestCase):

    def setUp(self):
        def mocked_models(klass):
            class Package:
                def all(self):
                    [self.pkg1, self.pkg2, self.pkg3, self.pkg4]
            klass()

        self.example_fetcher = kiskadee.fetchers.example.Fetcher()
        self.db = MagicMock()

        queues = Queues()
        self.monitor = Monitor(self.db, queues)

        self.data1 = {
                'name': 'curl',
                'version': '7.52.1-5',
                'fetcher': kiskadee.fetchers.debian.__name__,
                'meta': {'directory': 'pool/main/c/curl'},
                'results': {
                    'cppcheck': '<>',
                    'flawfinder': '><'},
                'fetcher_id': 1}

    def test_dequeue_package_from_fetcher(self):
        self.example_fetcher.watch()
        monitored_package = self.monitor.dequeue_package_from_fetchers()
        self.assertIn("version", monitored_package)
        self.assertIn("name", monitored_package)
        self.assertIn("fetcher", monitored_package)
        self.assertEqual(monitored_package['version'], '0.1')

    def test_run_fetchers_as_threads(self):
        Monitor.start_fetcher(self.example_fetcher.watch)
        Monitor.start_fetcher(self.example_fetcher.watch)
        first_monitored_package = self.monitor.dequeue_package_from_fetchers()
        second_monitored_package = self.monitor.dequeue_package_from_fetchers()
        self.assertIn("version", first_monitored_package)
        self.assertIn("version", second_monitored_package)
        self.assertIn("name", first_monitored_package)
        self.assertIn("name", second_monitored_package)
        self.assertIn("fetcher", first_monitored_package)
        self.assertIn("fetcher", second_monitored_package)

    def test_send_package_to_runner(self):
        fetcher = Fetcher(name='example')
        Package(name='package1', fetcher_id=fetcher.id)
        self.monitor.get_fetcher_and_package = MagicMock(
                return_value=[fetcher, {}]
                )
        self.monitor.is_a_new_package_version = MagicMock(
                return_value=True
                )
        self.monitor.send_package_to_runner(self.data1)
        self.assertEqual(self.monitor.queues.dequeue_analysis(), self.data1)

        if __name__ == '__main__':
            unittest.main()
