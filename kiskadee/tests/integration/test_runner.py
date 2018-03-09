"""
This integration tests needs docker engine be running and accessible
by the user that is executing the tests. It also needs selinux running in
a permissive mode (setenforce 0)
"""
import unittest
import re
from unittest.mock import MagicMock

import kiskadee.queue
import kiskadee.runner
import kiskadee.monitor
import kiskadee.fetchers.example
import kiskadee.analyzers

class RunnerTestCase(unittest.TestCase):

    """Docstring for AnalyzersTestCase. """

    def setUp(self):
        self.queues = kiskadee.queue.Queues()
        self.runner = kiskadee.runner.Runner(self.queues)

        self.project = {
                'name': 'test',
                'version': '1.0.0',
                'fetcher': kiskadee.fetchers.example.__name__
        }

    def tearDown(self):
        """TODO: to be defined1. """

    def test_run_analyzers(self):
        self.runner.project = self.project
        self.runner.call_analyzers()
        result = self.queues.dequeue_result()
        self.assertEqual(result['name'], 'test')
        self.assertIn('results', result)

    def test_run_a_single_analyzer(self):
        self.runner.project = self.project
        self.runner.fetcher = self.runner.import_project_fetcher()
        source_path = self.runner.get_project_code_path()
        analyzer = self.runner.fetcher.analyzers()[0]
        self.assertIsNotNone(re.search('.*cppcheck.*', analyzer))
        self.assertIsNone(re.search('.*pylint.*', analyzer))

    def test_analysis_an_incoming_monitor_project(self):
        self.session = MagicMock()
        self.session.query().filter_by().first = MagicMock(return_value={})
        self.monitor = kiskadee.monitor.Monitor(self.session, self.queues)
        self.monitor.send_project_to_runner(self.project)
        incoming_project = self.runner.queues.dequeue_analysis()
        self.assertEqual(self.project, incoming_project)

if __name__ == '__main__':
    unittest.main()
