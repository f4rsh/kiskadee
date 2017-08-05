from flask import Flask
from kiskadee.database import Database
from kiskadee.model import Package, Fetcher, Version

kiskadee = Flask(__name__)
db_session = Database().session


@kiskadee.route('/')
def index():
    return db_session.query(Package).first().name


if __name__ == '__main__':
    kiskadee.run(debug=True)

