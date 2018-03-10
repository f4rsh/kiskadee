"""Provide kiskadee Database operations."""

from sqlalchemy import create_engine, orm

import kiskadee
from kiskadee.model import Base
from kiskadee.model import Package, Fetcher, Version, Report, Analysis

class Database:
    """kiskadee Database class."""

    def __init__(self, db='db_development'):
        """Return a Database object with SQLAlchemy session and engine."""
        self.engine = self._create_engine(db)
        self.session = self._create_session(self.engine)
        Base.metadata.bind = self.engine

    def _create_engine(self, db):
        uri = get_database_uri(db)
        return create_engine(uri)

    def _create_session(self, engine):
        DBSession = orm.sessionmaker(bind=engine)
        return DBSession()

    def filter_by_name(self, model, _name):
        return self.session.query(model).filter_by(name = _name).first()

    def get(self, model, id):
        return self.session.query(model).get(id)

def get_database_uri(db):
    """Return the Database URI of the current session."""
    config = kiskadee.config[db]

    driver = config['driver']
    username = config['username']
    password = config['password']
    hostname = config['hostname']
    port = config['port']
    dbname = config['dbname']

    return '%s://%s:%s@%s:%s/%s' % (driver, username, password,
                                    hostname, port, dbname)
