"""kiskadee API."""
from flask import Flask, jsonify
from flask import request
from flask_cors import CORS

from kiskadee.database import Database
from kiskadee.model import Project, Fetcher, Version, Analysis
from kiskadee.api.serializers import ProjectSchema, FetcherSchema,\
        AnalysisSchema
import json
from sqlalchemy.orm import eagerload

kiskadee = Flask(__name__)

CORS(kiskadee)

db = Database()

@kiskadee.route('/fetchers')
def index():
    """Get the list of available fetchers."""
    if request.method == 'GET':
        fetchers = db.session.query(Fetcher).all()
        fetcher_schema = FetcherSchema(many=True)
        result = fetcher_schema.dump(fetchers)
        return jsonify({'fetchers': result.data})


@kiskadee.route('/projects')
def projects():
    """Get the list of analyzed projects."""
    if request.method == 'GET':
        projects = db.session.query(Project).all()
        project_schema = ProjectSchema(
            many=True,
            exclude=['versions.analysis', 'versions.project_id']
        )
        data, errors = project_schema.dump(projects)
        return jsonify({'projects': data})


@kiskadee.route('/analysis/<project_name>/<version>', methods=['GET'])
def project_analysis_overview(project_name, version):
    """Get a analysis list of some project version."""

    #TODO: This can be a simple inner join between project, version and analysis
    _project_id = db.filter_by_name(Project, project_name).id
    version_id = db.session.query(Version)\
            .filter_by(number = version, project_id = _project_id ).first().id
    analysis = (
            db.session.query(Analysis)
            .options(
                eagerload(Analysis.analyzers, innerjoin=True)
            )
            .filter(Analysis.version_id == version_id)
            .all()
        )
    analysis_schema = AnalysisSchema(many=True, exclude=['raw', 'report'])
    data, errors = analysis_schema.dump(analysis)
    return jsonify(data)


@kiskadee.route(
    '/analysis/<pkg_name>/<version>/<analysis_id>/results',
    methods=['GET']
)
def analysis_results(pkg_name, version, analysis_id):
    """Get the analysis results from a specific analyzer."""
    analysis = db.get(Analysis, analysis_id)
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
    analysis = db.get(Analysis, analysis_id)
    data, errors = AnalysisSchema(only=['report']).dump(analysis)
    report = data['report']
    try:
        report['results'] = json.loads(report['results'])
        return jsonify({'analysis_report': report})
    except Exception as err:
        return jsonify({'analysis_report': {}})

def main():
    """Initialize the kiskadee API."""
    kiskadee.run('0.0.0.0')
