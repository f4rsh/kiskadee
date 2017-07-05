from unittest import TestCase
from kiskadee import model
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker


class TestModel(TestCase):

    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        model.Base.metadata.create_all(self.engine)
        self.analyzer = model.Analyzer(name="cppcheck", version="1.0.0")
        self.plugin = model.Plugin(name='kiskadee-plugin', target='university')
        self.package = model.Package(name='python-kiskadee')
        self.version = model.Version(number='1.0-rc1')
        self.plugin.packages.append(self.package)
        self.package.versions.append(self.version)
        self.session.add(self.package)
        self.session.add(self.plugin)
        self.session.add(self.version)
        self.session.add(self.analyzer)

        self.analysis = model.Analysis(
                analyzer_id=self.analyzer.id,
                version_id=self.version.id,
                raw=""
                )
        self.session.commit()

    def tearDown(self):
        model.Base.metadata.drop_all(self.engine)

    def test_query_plugin(self):
        plugins = self.session.query(model.Plugin).all()
        self.assertEqual(plugins, [self.plugin])

    def test_query_package(self):
        packages = self.session.query(model.Package).all()
        self.assertEqual(packages, [self.package])

    def test_query_version(self):
        versions = self.session.query(model.Version).all()
        self.assertEqual(versions, [self.version])

    def test_add_plugin(self):
        plugins = self.session.query(model.Plugin).all()
        self.assertEqual(len(plugins), 1)
        self.session.add(model.Plugin(name='foo', target='bar'))
        plugins = self.session.query(model.Plugin).all()
        self.assertEqual(len(plugins), 2)

    def test_add_version_without_package(self):
        version = model.Version(number='3.1')
        self.session.add(version)
        with self.assertRaises(exc.IntegrityError):
            self.session.commit()

    def test_add_package_without_plugin(self):
        package = model.Package(name='foo-bar')
        self.session.add(package)
        with self.assertRaises(exc.IntegrityError):
            self.session.commit()

    def test_unique_package_in_plugin(self):
        package_1 = model.Package(name='foo-bar')
        package_2 = model.Package(name='foo-bar')
        self.plugin.packages.append(package_1)
        self.plugin.packages.append(package_2)
        with self.assertRaises(exc.IntegrityError):
            self.session.commit()

    def test_unique_version_for_package(self):
        package_version_1 = model.Version(number='1.0')
        package_version_2 = model.Version(number='1.0')
        self.package.versions.append(package_version_1)
        self.package.versions.append(package_version_2)
        with self.assertRaises(exc.IntegrityError):
            self.session.commit()
