import json
import unittest
from unittest.mock import MagicMock

import kiskadee
import kiskadee.api.app
import kiskadee.fetchers.example
import kiskadee.database


class ApiTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        kiskadee.api.app.kiskadee.testing = True
        cls.app = kiskadee.api.app.kiskadee.test_client()
        cls.db = kiskadee.api.app.db = MagicMock()

    def setUp(self):
        self.fetcher = kiskadee.model.Fetcher(name='kiskadee-fetcher')
        self.queues = kiskadee.queue.Queues()

    def test_get_fetchers(self):
        self.db.session.query().all = MagicMock(return_value=[self.fetcher])
        response = self.app.get("/fetchers")
        response_data = json.loads(response.data.decode("utf-8"))
        self.assertIn("fetchers", response_data)
        self.assertEqual(
                'kiskadee-fetcher',
                response_data['fetchers'][0]['name']
            )

    def test_get_analysis_as_json(self):
        analysis = kiskadee.model.Analysis(
                id=1, analyzer_id=1, version_id=1,
                raw='analysis result: foo'
                )

        self.db.filter_by_name = MagicMock()
        self.db.session.query(kiskadee.model.Project)\
            .filter_by().id = MagicMock()
        self.db.session.query(kiskadee.model.Version)\
            .filter_by().id = MagicMock()
        self.db.session.query().options()\
            .filter().all = MagicMock(return_value=[analysis])

        response = self.app.get("/analysis/mocked-package/1.0.0")
        response_data = json.loads(response.data.decode("utf-8"))
        self.assertTrue(len(response_data) >= 1)

    def test_get_analysis_results(self):

        analysis = kiskadee.model.Analysis(
                id=1, analyzer_id=1, version_id=1,
                raw={'results': 'first analysis results'}
                )
        self.db.get = MagicMock(return_value=analysis)
        response = self.app.get("/analysis/kiskadee-package/7.23/1/results")
        response_data = json.loads(response.data.decode("utf-8"))
        self.assertIn("analysis_results", response_data)
        self.assertTrue(len(response_data["analysis_results"]) > 0)

    @unittest.skip("I will review the code that this test should check")
    def test_get_analysis_reports(self):
        response = self.app.get("/analysis/kiskadee-package/7.23/1/reports")
        response_data = json.loads(response.data.decode("utf-8"))
        self.assertIn("analysis_report", response_data)


if __name__ == '__main__':
    unittest.main()
