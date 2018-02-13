import unittest
from sqlalchemy.orm import sessionmaker

from kiskadee import model
from kiskadee.monitor import Monitor
from kiskadee.queue import Queues
from kiskadee.model import Package, create_analyzers, Report, Analysis
import kiskadee.queue
import kiskadee.fetchers.debian
import kiskadee.fetchers.anitya
from kiskadee.database import Database


class MonitorTestCase(unittest.TestCase):

    def setUp(self):
        self.engine = Database('db_test').engine
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.monitor = Monitor(self.session)
        self.queues = Queues()
        model.Base.metadata.create_all(self.engine)
        create_analyzers(self.session)
        self.pkg1 = {
                'name': 'curl',
                'version': '7.52.1-5',
                'fetcher': kiskadee.fetchers.debian.__name__,
                'meta': {'directory': 'pool/main/c/curl'},
                'results': {
                    'cppcheck': '<>',
                    'flawfinder': '><'},
                'fetcher_id': 1}

        self.pkg2 = {'name': 'urlscan',
                     'version': '0.8.2',
                     'fetcher': kiskadee.fetchers.debian.__name__,
                     'meta': {'directory': 'pool/main/u/urlscan'},
                     'results': {
                            'cppcheck': '<>',
                            'flawfinder': '><'},
                     'fetcher_id': 1}

        self.pkg3 = {'name': 'curl',
                     'version': '7.52.2-5',
                     'fetcher': kiskadee.fetchers.debian.__name__,
                     'meta': {'directory': 'pool/main/c/curl'},
                     'results': {
                            'cppcheck': '<>',
                            'flawfinder': '><'},
                     'fetcher_id': 1}
        self.pkg4 = {'name': 'urlanitya',
                     'version': '0.11',
                     'fetcher': kiskadee.fetchers.anitya.__name__,
                     'meta': {
                            'backend': 'gitHub',
                            'homepage': 'https://github.com/GesielFreitas/Cros'
                        },
                     'results': {
                            'cppcheck': '<>',
                            'flawfinder': '><'},
                     'fetcher_id': 1}
        self.analysis = {
                'analyzer_id': 1,
                'id': 1,
                'raw': {
                    'results': [
                        {'severity': 'warning'},
                        {'severity': 'style'},
                        {'severity': 'error'}
                    ]
                }
            }

    def tearDown(self):
        self.session.close()
        model.Base.metadata.drop_all()

    def test_return_fetcher_name(self):
        fetcher = kiskadee.fetchers.debian.Fetcher()
        self.assertEqual(fetcher.name, 'debian')

    def test_save_package(self):
        self.monitor._save_fetcher(kiskadee.fetchers.debian.Fetcher())
        self.monitor._save_analyzed_project(self.pkg1)
        self.monitor._save_analyzed_project(self.pkg2)
        _pkgs = self.monitor.session.query(Package).all()
        self.assertEqual(len(_pkgs), 2)
        self.assertEqual(_pkgs[0].name, self.pkg1['name'])
        self.assertEqual(_pkgs[1].name, self.pkg2['name'])

    def test_save_reports(self):
        _fetcher = model.Fetcher(
                name='kiskadee-fetcher3', target='university'
            )
        _pkg = model.Package(
                name='kiskadee-package', fetcher_id=1
            )
        _version = model.Version(
                number='1.0-rc1', package_id=1
                )
        _raw = {
            'results': [
                {'severity': 'warning'},
                {'severity': 'style'},
                {'severity': 'error'}
            ]
        }
        _analysis = Analysis(
                version_id=1,
                analyzer_id=1,
                id=1,
                raw=_raw
            )
        self.session.add(_fetcher)
        self.session.add(_pkg)
        self.session.add(_version)
        self.session.add(_analysis)
        self.session.commit()
        _dict_analysis = {
                'results': _raw['results'],
                'id': 1
            }
        self.monitor._save_reports(_dict_analysis, self.pkg1, 'cppcheck')
        _report = self.monitor.session.query(Report).all()
        self.assertEqual(len(_report), 1)

    def test_save_version(self):
        self.monitor._save_fetcher(kiskadee.fetchers.debian.Fetcher())
        self.monitor._save_analyzed_project(self.pkg1)
        _pkgs = self.monitor.session.query(Package).all()
        _version = _pkgs[0].versions[0].number
        self.assertEqual(_version, self.pkg1['version'])

    def test_update_version(self):
        self.monitor._save_fetcher(kiskadee.fetchers.debian.Fetcher())
        self.queues.enqueue_project(self.pkg1)
        self.queues.enqueue_project(self.pkg3)

        _pkg = self.queues.dequeue_project()
        self.monitor._save_analyzed_project(_pkg)

        _pkg = self.queues.dequeue_project()
        self.monitor._save_analyzed_project(_pkg)

        _pkgs = self.monitor.session.query(Package).all()
        self.assertEqual(len(_pkgs), 1)

        _pkg_versions = self.monitor._query(Package).\
            filter(Package.name == _pkg['name']).first().versions

        _first_version = _pkg_versions[0].number
        _current_version = _pkg_versions[-1].number
        self.assertEqual(self.pkg1['version'], _first_version)
        self.assertEqual(_pkg['version'], _current_version)

    def test_save_package_anitya(self):
        self.monitor._save_fetcher(kiskadee.fetchers.anitya.Fetcher())
        self.queues.enqueue_project(self.pkg4)
        _pkg = self.queues.dequeue_project()
        self.monitor._save_analyzed_project(_pkg)
        _pkgs = self.monitor.session.query(Package).all()
        self.assertEqual(len(_pkgs), 1)
        self.assertEqual(_pkgs[0].homepage, _pkg['meta']['homepage'])


if __name__ == '__main__':
    unittest.main()
