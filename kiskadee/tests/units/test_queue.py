import unittest
import kiskadee.queue
import kiskadee.fetchers.example


class QueueTestCase(unittest.TestCase):

    def setUp(self):
        self.queues = kiskadee.queue.Queues()
        self.package = {
                'name': 'bar',
                'fetcher': kiskadee.fetchers.example.Fetcher(),
                'version': '1.0.0'
                }

    def test_enqueue_dequeue_package(self):
        self.queues.enqueue_package(self.package)
        _package = self.queues.dequeue_package()
        self.assertTrue(isinstance(_package, dict))
        self.assertEqual(_package['name'], 'bar')


if __name__ == '__main__':
    unittest.main()
