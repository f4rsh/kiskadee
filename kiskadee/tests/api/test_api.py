import json
import unittest
from unittest.mock import MagicMock

import kiskadee
from kiskadee.monitor import Monitor
import kiskadee.api.app
import kiskadee.fetchers.example


class ApiTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        kiskadee.api.app.kiskadee.testing = True
        cls.app = kiskadee.api.app.kiskadee.test_client()

    def setUp(self):
        self.fetcher = kiskadee.model.Fetcher(name='kiskadee-fetcher')

    def test_get_fetchers(self):
        kiskadee.api.app.kiskadee_db_session = MagicMock()
        kiskadee.api.app.kiskadee_db_session().query().all = MagicMock(
                return_value=[self.fetcher]
                )
        response = self.app.get("/fetchers")
        response_data = json.loads(response.data.decode("utf-8"))
        self.assertIn("fetchers", response_data)
        self.assertEqual(
                'kiskadee-fetcher',
                response_data['fetchers'][0]['name']
            )

    def test_get_analysis_as_json(self):
        package = kiskadee.model.Package(name='mocked-package', id=1)
        version = kiskadee.model.Version(number='1.0.0', id=1, package_id=1)
        analysis = kiskadee.model.Analysis(
                id=1, analyzer_id=1, version_id=1,
                raw='analysis result: foo'
                )

        def side_effect(klass):
            mocked_objects = {
                    'Package': package,
                    'Version': version,
                    }
            return mocked_objects[klass.__name__]

        kiskadee.api.app.kiskadee_db_session = MagicMock()
        Monitor(kiskadee.api.app.kiskadee_db_session())
        db_session = kiskadee.api.app.kiskadee_db_session()
        db_session.query(kiskadee.model.Package)\
                  .filter_by().id = MagicMock()

        db_session.query(kiskadee.model.Version)\
                  .filter_by().id = MagicMock()
        db_session.query().options()\
                  .filter().all = MagicMock(return_value=[analysis])

        response = self.app.get("/analysis/mocked-package/1.0.0")
        response_data = json.loads(response.data.decode("utf-8"))
        self.assertTrue(len(response_data) >= 1)

    def test_get_analysis_results(self):

        analysis = kiskadee.model.Analysis(
                id=1, analyzer_id=1, version_id=1,
                raw={'results': 'first analysis results'}
                )

        kiskadee.api.app.kiskadee_db_session().query().get = MagicMock(
                return_value=analysis
                )
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
