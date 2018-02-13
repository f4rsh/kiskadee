import unittest
import kiskadee.queue
import kiskadee.fetchers.example


class QueueTestCase(unittest.TestCase):

    def setUp(self):
        self.queues = kiskadee.queue.Queues()
        self.project = {
                'name': 'bar',
                'fetcher': kiskadee.fetchers.example.Fetcher(),
                'version': '1.0.0'
                }

    def test_enqueue_dequeue_project(self):
        self.queues.enqueue_project(self.project)
        _project = self.queues.dequeue_project()
        self.assertTrue(isinstance(_project, dict))
        self.assertEqual(_project['name'], 'bar')


if __name__ == '__main__':
    unittest.main()
