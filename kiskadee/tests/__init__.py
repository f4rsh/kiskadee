"""kiskadee test suite."""
from kiskadee import model


def clean_test_db(db, metadata):
    """Clean test database to run tests independently."""
    #  The number of openend sessions is limited by the operational system.
    # If we open too much connections, the database will lock the tests
    # execution.
    db.session.close_all()
    metadata.drop_all(db.engine)
    metadata.create_all(db.engine)
    model.Analyzer.create_analyzers(db)
