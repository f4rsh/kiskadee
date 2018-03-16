"""Provide objects to serialize the kiskadee models."""

from marshmallow import Schema, fields
from kiskadee.model import Project, Fetcher, Analysis, Version,\
        Report, Analyzer


class ReportsSchema(Schema):
    """Provide a serializer to the Reports model."""

    id = fields.Int()
    analysis_id = fields.Int()
    results = fields.Dict()

    def make_object(self, data):
        """Serialize a Reports object."""
        print('MAKING OBJECT FROM', data)
        return Report(**data)


class AnalyzerSchema(Schema):
    """Provide a serializer to the Analyzer model."""

    id = fields.Int()
    name = fields.Str()
    version = fields.Str()
    analysis = fields.Nested('AnalysisSchema', many=True)

    def make_object(self, data):
        """Serialize a Analyzer object."""
        print('MAKING OBJECT FRON', data)
        return Analyzer(**data)


class AnalysisSchema(Schema):
    """Provide a serializer to the Analysis model."""

    id = fields.Int()
    version_id = fields.Int()
    analyzer_id = fields.Int()
    raw = fields.Dict()
    report = fields.Nested(ReportsSchema)
    analyzers = fields.Nested(AnalyzerSchema, exclude=['analysis', 'id'])

    def make_object(self, data):
        """Serialize a Analysis object."""
        print('MAKING OBJECT FROM', data)
        return Analysis(**data)


class VersionSchema(Schema):
    """Provide a serializer to the Project model."""

    id = fields.Int()
    number = fields.Str()
    package_id = fields.Int()
    analysis = fields.Nested(AnalysisSchema, many=True)

    def make_object(self, data):
        """Serialize a Project object."""
        print('MAKING OBJECT FROM', data)
        return Version(**data)


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


class ProjectSchema(Schema):
    """Provide a serializer to the Project model."""

    id = fields.Int()
    name = fields.Str()
    fetcher_id = fields.Int()
    versions = fields.Nested(VersionSchema, many=True)

    def make_object(self, data):
        """Serialize a Project object."""
        print('MAKING OBJECT FROM', data)
        return Project(**data)
