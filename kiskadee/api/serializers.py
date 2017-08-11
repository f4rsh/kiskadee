"""Provide objects to serialize the kiskadee models."""

from marshmallow import Schema, fields
from kiskadee.model import Package, Fetcher, Analysis


class FetcherSchema(Schema):
    """Provide a serializer to the Fetcher model."""

    id = fields.Int()
    name = fields.Str()
    target = fields.Str()
    description = fields.Str()

    def make_object(self, data):
        """Serialize a Fetcher object."""
        print('MAKING OBJECT FROM', data)
        return Fetcher(**data)


class PackageSchema(Schema):
    """Provide a serializer to the Package model."""

    id = fields.Int()
    name = fields.Str()
    target = fields.Str()
    fetcher_id = fields.Nested(FetcherSchema)

    def make_object(self, data):
        """Serialize a Package object."""
        print('MAKING OBJECT FROM', data)
        return Package(**data)


class AnalysisSchema(Schema):
    """Provide a serializer to the Analysis model."""

    id = fields.Int()
    version_id = fields.Int()
    analyzer_id = fields.Int()
    raw = fields.Str()

    def make_object(self, data):
        """Serialize a Analysis object."""
        print('MAKING OBJECT FROM', data)
        return Analysis(**data)
