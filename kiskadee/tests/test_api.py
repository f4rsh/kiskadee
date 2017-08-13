import json
from kiskadee.api.app import kiskadee
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import kiskadee.model as model


class ApiTestCase(unittest.TestCase):

    def setUp(self):
        kiskadee.testing = True
        self.app = kiskadee.test_client()
        self.engine = create_engine('sqlite:///:memory:')
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        model.Base.metadata.create_all(self.engine)
        model.create_analyzers(self.session)
        self.fetcher = model.Fetcher(
                name='kiskadee-fetcher', target='university'
            )

    def test_get_fetchers(self):
        response = self.app.get("/fetchers")
        self.assertIn("fetcher", json.loads(response.data.decode("utf-8")))


if __name__ == '__main__':
    unittest.main()
