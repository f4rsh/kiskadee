import unittest

from sqlalchemy.orm import sessionmaker
from kiskadee.report import CppcheckReport, FlawfinderReport
from kiskadee.database import Database


class ReportTestCase(unittest.TestCase):

    def setUp(self):
        self.engine = Database('db_test').engine
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def tearDown(self):
        self.session.close()

    def test_compute_cppcheck_reports(self):
        _reports = [
                {'severity': 'warning'},
                {'severity': 'error'},
                {'severity': 'style'},
                {'some-attribute': None}
            ]
        _cpp_reporter = CppcheckReport(_reports)
        result = _cpp_reporter._compute_reports('cppcheck')
        self.assertEqual(len(result.keys()), 3)
        self.assertEqual(result['warning'], 1)
        self.assertEqual(result['style'], 1)
        self.assertEqual(result['error'], 1)

    def test_compute_flawfinder_reports(self):
        _reports = [
                {'severity': '5'},
                {'severity': '4'},
                {'severity': '3'},
                {'some-attribute': None}
            ]
        _flawfinder_reporter = FlawfinderReport(_reports)
        result = _flawfinder_reporter._compute_reports('flawfinder')
        self.assertEqual(len(result.keys()), 5)
        self.assertEqual(result['severity_5'], 1)
        self.assertEqual(result['severity_4'], 1)
        self.assertEqual(result['severity_3'], 1)
        self.assertEqual(result['severity_2'], 0)
        self.assertEqual(result['severity_1'], 0)


if __name__ == '__main__':
    unittest.main()
