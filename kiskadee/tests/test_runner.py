import unittest

from kiskadee.runner import Runner
import kiskadee.fetchers.example
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from kiskadee import model
from kiskadee.model import create_analyzers
from kiskadee.queue import KiskadeeQueue


class TestAnalyzers(unittest.TestCase):

    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        model.Base.metadata.create_all(self.engine)
        create_analyzers(self.session)
        self.fetcher = kiskadee.fetchers.debian.Fetcher()
        self.deb_pkg = {'name': 'test',
                        'version': '1.0.0',
                        'fetcher': kiskadee.fetchers.debian.Fetcher()
                        }
        self.fetcher = model.Fetcher(
                name='kiskadee-fetcher', target='university'
            )
        self.session.add(self.fetcher)
        self.session.commit()
        kiskadee_queue = KiskadeeQueue()
        self.runner = Runner()
        self.runner.kiskadee_queue = kiskadee_queue

    def test_run_analyzer(self):

        source_to_analysis = {
                'name': 'test',
                'version': '1.0.0',
                'fetcher': kiskadee.fetchers.example.Fetcher()
        }

        source_path = self.runner._path_to_uncompressed_source(
                source_to_analysis, kiskadee.fetchers.example.Fetcher()
            )
        firehose_report = self.runner.analyze(
                self.deb_pkg, "cppcheck", source_path)
        self.assertIsNotNone(firehose_report)

    def test_generate_a_firehose_report(self):
        source_to_analysis = {
                'name': 'test',
                'version': '1.0.0',
                'fetcher': kiskadee.fetchers.example.Fetcher()
        }

        self.runner.call_analyzers(source_to_analysis)
        analyzed_pkg = self.runner.kiskadee_queue.dequeue_result()

        self.assertEqual(analyzed_pkg['name'], source_to_analysis['name'])
        self.assertIn('cppcheck', analyzed_pkg['results'])
        # TODO: fix issue #44
        # self.assertIn('flawfinder', analyzed_pkg['results'])

    def test_path_to_uncompressed_source(self):

        source_to_analysis = {
                'name': 'test',
                'version': '1.0.0',
                'fetcher': kiskadee.fetchers.example
        }

        source_path = self.runner._path_to_uncompressed_source(
                source_to_analysis, kiskadee.fetchers.example.Fetcher()
        )

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
