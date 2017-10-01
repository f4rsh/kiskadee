"""kiskadee API."""
from flask import Flask, jsonify
from flask import request
from flask_cors import CORS

from kiskadee.database import Database
from kiskadee.model import Package, Fetcher, Version, Analysis
from kiskadee.api.serializers import PackageSchema, FetcherSchema,\
        AnalysisSchema
import json

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
        package_schema = PackageSchema(many=True)
        result = package_schema.dump(packages)
        return jsonify({'packages': result.data})


@kiskadee.route('/analysis/<pkg_name>/<version>')
def package_analysis(pkg_name, version):
    """Get the a analysis of some package version."""
    if request.method == 'GET':
        db_session = kiskadee_db_session()
        package_id = (
                db_session.query(Package)
                .filter(Package.name == pkg_name).first().id
            )
        version_id = (
                db_session.query(Version)
                .filter(Version.number == version)
                .filter(Version.package_id == package_id).first().id
            )
        analysis = (
                db_session.query(Analysis)
                .filter(Analysis.version_id == version_id).all()
            )
        analysis_schema = AnalysisSchema(many=True)
        results = analysis_schema.dump(analysis)
        for data in results.data:
            data['raw'] = json.loads(data['raw'])
        return jsonify({'analysis': results.data})


def kiskadee_db_session():
    """Return a kiskadee database session."""
    return Database().session


def main():
    """Initialize the kiskadee API."""
    kiskadee.run('0.0.0.0')
