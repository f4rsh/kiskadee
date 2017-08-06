from marshmallow import Schema, fields, ValidationError, pre_load

class FetcherSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    target = fields.Str()
    description = fields.Str()

    def make_object(self, data):
        print('MAKING OBJECT FROM', data)
        return Fetcher(**data)

class PackageSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    target = fields.Str()
    fetcher_id = fields.Nested(FetcherSchema)

    def make_object(self, data):
        print('MAKING OBJECT FROM', data)
        return Package(**data)

class AnalysisSchema(Schema):
    id = fields.Int()
    version_id = fields.Int()
    analyzer_id = fields.Int()
    raw = fields.Str()

    def make_object(self, data):
        print('MAKING OBJECT FROM', data)
        return Analysis(**data)
