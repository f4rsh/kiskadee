import json
from flask import Flask, jsonify
from flask import request

from kiskadee.database import Database
from kiskadee.model import Package, Fetcher, Version
from kiskadee.api.serializers import PackageSchema, FetcherSchema

kiskadee = Flask(__name__)
db_session = Database().session


@kiskadee.route('/fetchers')
def index():
    if request.method == 'GET':
        fetchers = db_session.query(Fetcher).all()
        fetcher_schema = FetcherSchema(many=True)
        result = fetcher_schema.dump(fetchers)
        return jsonify({'fetcher': result.data})

@kiskadee.route('/packages')
def packages():
    if request.method == 'GET':
        packages = db_session.query(Package).all()
        package_schema = PackageSchema(many=True)
        result = package_schema.dump(packages)
        return jsonify({'packages': result.data})

if __name__ == '__main__':
    kiskadee.run(debug=True)
