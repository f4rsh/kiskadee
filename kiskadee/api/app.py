"""kiskadee API."""
from flask import Flask, jsonify
from flask import request
from flask_cors import CORS

from kiskadee.database import Database
from kiskadee.model import Package, Fetcher, Version, Analysis
from kiskadee.api.serializers import PackageSchema, FetcherSchema,\
        AnalysisSchema
import json
from sqlalchemy.orm import eagerload

kiskadee = Flask(__name__)

CORS(kiskadee)


@kiskadee.route('/fetchers')
def index():
    """Get the list of available fetchers."""
    if request.method == 'GET':
        db_session = kiskadee_db_session()
        fetchers = db_session.query(Fetcher).all()
        fetcher_schema = FetcherSchema(many=True)
        result = fetcher_schema.dump(fetchers)
        return jsonify({'fetchers': result.data})


@kiskadee.route('/packages')
def packages():
    """Get the list of analyzed packages."""
    if request.method == 'GET':
        db_session = kiskadee_db_session()
        packages = db_session.query(Package).all()
        package_schema = PackageSchema(
            many=True,
            exclude=['versions.analysis', 'versions.package_id']
        )
        data, errors = package_schema.dump(packages)
        return jsonify({'packages': data})


@kiskadee.route('/analysis/<pkg_name>/<version>', methods=['GET'])
def package_analysis_overview(pkg_name, version):
    """Get the a analysis list of some package version."""
    db_session = kiskadee_db_session()

    #TODO: This can be a simple inner join between package, version and analysis
    package_id = (
            db_session.query(Package).filter_by(name = pkg_name).id
        )
    version_id = (
            db_session.query(Version)
            .filter(Version.number == version)
            .filter(Version.package_id == package_id).first().id
        )
    analysis = (
            db_session.query(Analysis)
            .options(
                eagerload(Analysis.analyzers, innerjoin=True)
            )
            .filter(Analysis.version_id == version_id)
            .all()
        )
    kiskadee.logger.debug("haaaaaaa")
    kiskadee.logger.debug(analysis)
    analysis_schema = AnalysisSchema(many=True, exclude=['raw', 'report'])
    data, errors = analysis_schema.dump(analysis)
    return jsonify(data)


@kiskadee.route(
    '/analysis/<pkg_name>/<version>/<analysis_id>/results',
    methods=['GET']
)
def analysis_results(pkg_name, version, analysis_id):
    """Get the analysis results from a specific analyzer."""
    db_session = kiskadee_db_session()
    analysis = (
            db_session.query(Analysis)
            .get(analysis_id)
        )
    analysis_schema = AnalysisSchema(only=['raw'])
    data, errors = analysis_schema.dump(analysis)
    response = data['raw']['results']
    return jsonify({'analysis_results': response})


@kiskadee.route(
    '/analysis/<pkg_name>/<version>/<analysis_id>/reports',
    methods=['GET']
)
def analysis_reports(pkg_name, version, analysis_id):
    """Get the analysis reports from a specific analyzer."""
    db_session = kiskadee_db_session()
    analysis = (
            db_session.query(Analysis)
            .get(analysis_id)
        )
    analysis_schema = AnalysisSchema(only=['report'])
    data, errors = analysis_schema.dump(analysis)
    report = data['report']
    if (report is not None) and\
        ('results' in report.keys()) and\
            report['results'] is not None:
        report['results'] = json\
            .loads(report['results'])
    return jsonify({'analysis_report': report})


def kiskadee_db_session():
    """Return a kiskadee database session."""
    return Database().session


def main():
    """Initialize the kiskadee API."""
    kiskadee.run('0.0.0.0')
