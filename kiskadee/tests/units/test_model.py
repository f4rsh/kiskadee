import unittest
from sqlalchemy import exc
from sqlalchemy.orm import sessionmaker

from kiskadee import model
from kiskadee.database import Database


class ModelTestCase(unittest.TestCase):

    def setUp(self):
        self.engine = Database('db_test').engine
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        model.Base.metadata.create_all(self.engine)
        model.create_analyzers(self.session)
        self.fetcher = model.Fetcher(
              name='kiskadee-fetcher', target='university'
            )
        self.package = model.Package(name='python-kiskadee')
        self.version = model.Version(number='1.0-rc1')
        self.fetcher.packages.append(self.package)
        self.package.versions.append(self.version)
        self.session.add(self.package)
        self.session.add(self.fetcher)
        self.session.add(self.version)

        self.analysis = model.Analysis(
                analyzer_id=1,
                version_id=1,
                raw=""
                )
        self.session.add(self.analysis)
        self.report = model.Report(
                analysis_id=1,
        )
        self.session.add(self.report)
        self.session.commit()

    def tearDown(self):
        self.session.close()
        model.Base.metadata.drop_all()

    def test_query_fetcher(self):
        fetchers = self.session.query(model.Fetcher).all()
        self.assertEqual(fetchers, [self.fetcher])

    def test_query_package(self):
        packages = self.session.query(model.Package).all()
        self.assertEqual(packages, [self.package])

    def test_query_version(self):
        versions = self.session.query(model.Version).all()
        self.assertEqual(versions, [self.version])

    def test_query_report(self):
        reports = self.session.query(model.Report).all()
        self.assertEqual(reports, [self.report])

    def test_add_fetcher(self):
        fetchers = self.session.query(model.Fetcher).all()
        self.assertEqual(len(fetchers), 1)
        self.session.add(model.Fetcher(name='foo', target='bar'))
        fetchers = self.session.query(model.Fetcher).all()
        self.assertEqual(len(fetchers), 2)

    def test_add_version_without_package(self):
        version = model.Version(number='3.1')
        self.session.add(version)
        with self.assertRaises(exc.IntegrityError):
            self.session.commit()

    def test_add_report_without_analysis(self):
        report = model.Report(
        )
        self.session.add(report)
        with self.assertRaises(exc.IntegrityError):
            self.session.commit()

    def test_add_package_without_fetcher(self):
        package = model.Package(name='foo-bar')
        self.session.add(package)
        with self.assertRaises(exc.IntegrityError):
            self.session.commit()

    def test_unique_package_in_fetcher(self):
        package_1 = model.Package(name='foo-bar')
        package_2 = model.Package(name='foo-bar')
        self.fetcher.packages.append(package_1)
        self.fetcher.packages.append(package_2)
        with self.assertRaises(exc.IntegrityError):
            self.session.commit()

    def test_unique_version_for_package(self):
        package_version_1 = model.Version(number='1.0')
        package_version_2 = model.Version(number='1.0')
        self.package.versions.append(package_version_1)
        self.package.versions.append(package_version_2)
        with self.assertRaises(exc.IntegrityError):
            self.session.commit()

    def test_compose_kiskadee_source(self):
        _analyzer = self.session.query(model.Analyzer)\
                    .filter(model.Analyzer.name == "cppcheck").first()
        package = model.Package(
                name='bla',
                fetcher_id=self.fetcher.id
                )
        package_version = model.Version(
                number='1.0.1',
                package_id=package.id
                )

        package_analysis = model.Analysis(
                raw="<>",
                analyzer_id=_analyzer.id,
                version_id=package_version.id
                )

        self.fetcher.packages.append(package)
        package.versions.append(package_version)
        package_version.analysis.append(package_analysis)

        self.assertEqual(package.versions[0].analysis[0].raw, "<>")

    def test_save_several_analysis(self):

        _analyzer1 = (
                self.session.query(model.Analyzer)
                .filter(model.Analyzer.name == "cppcheck").first()
                )
        _analyzer2 = (
                self.session.query(model.Analyzer)
                .filter(model.Analyzer.name == "flawfinder").first()
                )

        package = model.Package(
                name='bla',
                fetcher_id=self.fetcher.id
                )
        package_version = model.Version(
                number='1.0.1',
                package_id=package.id
                )

        self.fetcher.packages.append(package)
        package.versions.append(package_version)

        self.session.add(package)
        self.session.add(package_version)
        self.session.commit()

        package_analysis1 = model.Analysis(
                raw="<>",
                analyzer_id=_analyzer1.id,
                version_id=package_version.id
                )
        package_analysis2 = model.Analysis(
                raw="><",
                analyzer_id=_analyzer2.id,
                version_id=package_version.id
                )

        self.session.add(package_analysis1)
        self.session.add(package_analysis2)
        self.session.commit()

        saved_package = (
                self.session.query(model.Package)
                .filter(model.Package.name == 'bla').first()
                )
        analysis = saved_package.versions[-1].analysis
        self.assertEqual(len(analysis), 2)
        self.assertEqual(analysis[0].raw, "<>")
        self.assertEqual(analysis[1].raw, "><")


if __name__ == '__main__':
    unittest.main()
