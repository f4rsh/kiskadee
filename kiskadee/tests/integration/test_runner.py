"""
This integration tests needs docker engine be running and accessible
by the user that is executing the tests. It also needs selinux running in
a permissive mode (setenforce 0)
"""
import unittest
import tempfile

from kiskadee.runner import Runner
import kiskadee.fetchers.example
import kiskadee.fetchers.debian
from sqlalchemy.orm import sessionmaker
from kiskadee import model
from kiskadee.queue import Queues
from kiskadee.database import Database


class AnalyzersTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = Database('db_test').engine
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        model.Base.metadata.create_all(self.engine)
        model.Analyzer.create_analyzers(self.session)
        self.fetcher = kiskadee.fetchers.debian.Fetcher()
        self.deb_pkg = {'name': 'test',
                        'version': '1.0.0',
                        'fetcher': kiskadee.fetchers.debian.__name__
                        }
        self.fetcher = model.Fetcher(
                name='kiskadee-fetcher2', target='university'
            )
        self.session.add(self.fetcher)
        self.session.commit()
        self.runner = Runner()
        self.runner.queues = Queues()

    def tearDown(self):
        self.session.close()
        model.Base.metadata.drop_all()

    def test_run_analyzer(self):

        source_to_analysis = {
                'name': 'test',
                'version': '1.0.0',
                'fetcher': kiskadee.fetchers.example.Fetcher()
        }

        source_path = self.runner._path_to_uncompressed_source(
                source_to_analysis, kiskadee.fetchers.example.Fetcher()
            )
        firehose_report = self.runner.analyze("cppcheck", source_path)
        self.assertIsNotNone(firehose_report)

    def test_generate_a_firehose_report(self):
        source_to_analysis = {
                'name': 'test',
                'version': '1.0.0',
                'fetcher': kiskadee.fetchers.example.__name__
        }

        self.runner.call_analyzers(source_to_analysis)
        analyzed_pkg = self.runner.queues.dequeue_result()
        self.assertEqual(analyzed_pkg['name'], source_to_analysis['name'])
        self.assertIn('cppcheck', analyzed_pkg['results'])
        self.assertIn('flawfinder', analyzed_pkg['results'])

    def test_path_to_uncompressed_source(self):

        source_to_analysis = {
                'name': 'test',
                'version': '1.0.0',
                'fetcher': kiskadee.fetchers.example
        }

        source_path = self.runner._path_to_uncompressed_source(
                source_to_analysis, kiskadee.fetchers.example.Fetcher()
        )
        tmp_path = tempfile.gettempdir()
        self.assertTrue(source_path.find(tmp_path) >= 0)
        self.assertIsNotNone(source_path)

    def test_invalid_path_to_uncompressed_source(self):

        source_to_analysis = {
                'name': 'test',
                'version': '1.0.0',
                'fetcher': kiskadee.fetchers.example
        }

        source_path = self.runner._path_to_uncompressed_source(
                source_to_analysis, None
        )

        self.assertIsNone(source_path)


if __name__ == '__main__':
    unittest.main()
