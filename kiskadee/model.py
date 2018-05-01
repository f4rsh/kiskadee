"""This module provides kiskadee database model."""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, UnicodeText, UniqueConstraint,\
                       Sequence, Unicode, ForeignKey, orm, JSON
import json

import kiskadee
from kiskadee.report import CppcheckReport, FlawfinderReport

Base = declarative_base()


class Package(Base):
    """Software packages abstraction.

    A software package is the source code for a software package. It may be
    upstream's distribution or the sources provided by some other source, like
    a linux distribution.
    """

    __tablename__ = 'packages'
    id = Column(Integer,
                Sequence('packages_id_seq', optional=True), primary_key=True)
    name = Column(Unicode(255), nullable=False)
    homepage = Column(Unicode(255), nullable=True)
    fetcher_id = Column(Integer, ForeignKey('fetchers.id'), nullable=False)
    versions = orm.relationship('Version', backref='packages')
    __table_args__ = (
            UniqueConstraint('name', 'fetcher_id'),
            )

    @staticmethod
    def save(db, data):
        homepage = None
        if ('meta' in data) and ('homepage' in data['meta']):
            homepage = data['meta']['homepage']

        _package = Package(
                name=data['name'],
                homepage=homepage,
                fetcher_id=data['fetcher_id']
                )
        db.session.add(_package)
        db.session.commit()
        _version = Version(number=data['version'],
                           package_id=_package.id)
        db.session.add(_version)
        db.session.commit()
        return _package

    @staticmethod
    def update(db, package, data):

        if(package.versions[-1].number == data['version']):
            return package
        try:
            _new_version = Version(
                    number=data['version'],
                    package_id=package.id
                    )
            package.versions.append(_new_version)
            db.session.add(package)
            db.session.commit()
            kiskadee.logger.debug(
                    "MONITOR: Sending package {}_{}"
                    "for analysis".format(data['name'], data['version'])
                    )
            return package
        except ValueError:
            kiskadee.logger.debug("MONITOR: Could not compare versions")
            return None


class Fetcher(Base):
    """kiskadee fetcher abstraction."""

    __tablename__ = 'fetchers'
    id = Column(Integer,
                Sequence('fetchers_id_seq', optional=True), primary_key=True)
    name = Column(Unicode(255), nullable=False, unique=True)
    target = Column(Unicode(255), nullable=True)
    description = Column(UnicodeText)
    packages = orm.relationship('Package', backref='fetchers')


class Version(Base):
    """Abstraction of a package version."""

    __tablename__ = 'versions'
    id = Column(Integer,
                Sequence('versions_id_seq', optional=True), primary_key=True)
    number = Column(Unicode(100), nullable=False)
    package_id = Column(Integer, ForeignKey('packages.id'), nullable=False)
    analysis = orm.relationship('Analysis', backref='versions')
    __table_args__ = (
            UniqueConstraint('number', 'package_id'),
            )


class Analyzer(Base):
    """Abstraction of a static analyzer."""

    __tablename__ = 'analyzers'
    id = Column(Integer,
                Sequence('analyzers_id_seq', optional=True), primary_key=True)
    name = Column(Unicode(255), nullable=False, unique=True)
    version = Column(Unicode(255), nullable=True)
    analysis = orm.relationship('Analysis', backref='analyzers')

    @staticmethod
    def create_analyzers(db):
        """Create the analyzers on database.

        The kiskadee analyzers are defined on the section `analyzers` of the
        kiskadee.conf file. The `_session` argument represents a sqlalchemy
        session.
        """
        list_of_analyzers = dict(kiskadee.config._sections["analyzers"])
        for _name, _version in list_of_analyzers.items():
            if not db.session.query(Analyzer)\
                            .filter_by(name = _name, version = _version )\
                            .first():
                new_analyzer = kiskadee.model.Analyzer(name = _name,
                                                       version = _version)
                db.session.add(new_analyzer)
        db.session.commit()

class Analysis(Base):
    """Abstraction of a package analysis."""

    __tablename__ = 'analysis'
    id = Column(Integer,
                Sequence('analysis_id_seq', optional=True), primary_key=True)
    version_id = Column(Integer, ForeignKey('versions.id'), nullable=False)
    analyzer_id = Column(Integer, ForeignKey('analyzers.id'), nullable=False)
    raw = Column(JSON)
    report = orm.relationship('Report',
                              uselist=False, back_populates='analysis')

    @staticmethod
    def save(db, analyzer, result, package):
        version = package.versions[-1]
        name = package.name
        _analysis = kiskadee.model.Analysis()
        try:
            _analyzer = db.session.query(kiskadee.model.Analyzer).\
                    filter_by(name = analyzer).first()
            _analysis.analyzer_id = _analyzer.id
            _analysis.version_id = version.id
            _analysis.raw = json.loads(result)
            db.session.add(_analysis)
            db.session.commit()
            dict_analysis = {
                    'results': _analysis.raw['results'],
                    'id': _analysis.id
                }
            Report.save(db, dict_analysis, _analyzer.name, name)
            kiskadee.logger.debug(
                    "MONITOR: Saved analysis done by {} for package: {}-{}"
                    .format(analyzer, package.name, version)
                )
            return
        except Exception as err:
            kiskadee.logger.debug(
                    "MONITOR: The required analyzer was " +
                    "not registered in kiskadee"
                )
            kiskadee.logger.debug(err)
            return None


class Report(Base):
    """Abstraction of a analysis report."""

    REPORTERS = {
        'cppcheck': CppcheckReport,
        'flawfinder': FlawfinderReport
    }

    __tablename__ = 'reports'
    id = Column(Integer,
                Sequence('reports_id_seq', optional=True), primary_key=True)
    analysis_id = Column(Integer, ForeignKey('analysis.id'), nullable=False)
    results = Column(JSON)
    analysis = orm.relationship('Analysis', back_populates='report')

    @staticmethod
    def save(db, analysis, analyzer_name, package_name):
        try:
            results = analysis['results']
            analyzer_report = Report.REPORTERS[analyzer_name](results)
            _reports = Report()
            _reports.results = json.dumps(
                    analyzer_report
                    ._compute_reports(analyzer_name)
                )
            _reports.analysis_id = analysis['id']
            db.session.add(_reports)
            db.session.commit()
            kiskadee.logger.debug(
                    "MONITOR: Saved analysis reports for {} package"
                    .format(package_name)
                )
        except KeyError as key:
            kiskadee.logger.debug(
                    "ERROR: There's no reporter " +
                    "to get reports from {} analyzer. ".format(key) +
                    "Make shure to import or implement them."
                )
        except Exception as err:
            kiskadee.logger.debug(
                    "MONITOR: Failed to get analysis reports to {} package"
                    .format(package_name)
                )
            kiskadee.logger.debug(err)
        return

