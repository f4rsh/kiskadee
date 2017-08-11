"""Kiskadee API."""
from flask import Flask, jsonify
from flask import request
from flask_cors import CORS

from kiskadee.database import Database
from kiskadee.model import Package, Fetcher, Version, Analysis
from kiskadee.api.serializers import PackageSchema, FetcherSchema,\
        AnalysisSchema

kiskadee = Flask(__name__)
db_session = Database().session
CORS(kiskadee)


@kiskadee.route('/fetchers')
def index():
    """Get the list of available fetchers."""
    if request.method == 'GET':
        fetchers = db_session.query(Fetcher).all()
        fetcher_schema = FetcherSchema(many=True)
        result = fetcher_schema.dump(fetchers)
        return jsonify({'fetcher': result.data})


@kiskadee.route('/packages')
def packages():
    """Get the list of analyzed packages."""
    if request.method == 'GET':
        packages = db_session.query(Package).all()
        package_schema = PackageSchema(many=True)
        result = package_schema.dump(packages)
        return jsonify({'packages': result.data})


@kiskadee.route('/analysis/<pkg_name>/<version>/')
def package_analysis(pkg_name, version):
    """Get the a analysis of some package version."""
    if request.method == 'GET':
        package = db_session.query(Package)\
                .filter(Package.name == pkg_name).first().id
        version = (
                db_session.query(Version)
                .filter(Version.package_id == package).first().id
            )
        analysis = (
                db_session.query(Analysis)
                .filter(Analysis.version_id == version).first()
            )

        analysis_schema = AnalysisSchema()
        result = analysis_schema.dump(analysis)
        return jsonify({'analysis': result.data})


if __name__ == '__main__':
    kiskadee.run('0.0.0.0')
