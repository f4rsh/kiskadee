import unittest

import kiskadee.fetchers.example
import kiskadee.runner


class RunnerTestCase(unittest.TestCase):

    def setUp(self):
        self.queues = kiskadee.queue.Queues()
        self.runner = kiskadee.runner.Runner(self.queues)

    def test_path_to_uncompressed_source(self):

        self.runner.fetcher = kiskadee.fetchers.example.Fetcher()
        self.runner.project = {'name': 'test'}
        uncompressed_source_path = self.runner.get_project_code_path()
        self.assertIsNotNone(uncompressed_source_path)
