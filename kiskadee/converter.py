"""Firehose static analysis report format converter.

Module providing functions to convert analysis reports to the firehose format.
"""

from importlib import import_module
import shutil
import tempfile
import os
import json

from firehose.model import Analysis, to_json


def to_firehose(bytes_input, analyzer):
    """Parser the analyzer report to Firehose format.

    :bytes_input: The analyzer report, as a byte string
    :returns: A xml.etree.ElementTree object, representing the firehose report
    """
    tempdir = tempfile.mkdtemp()
    tmp_report_file = "%s_report.raw" % analyzer

    file_to_parse = os.path.join(tempdir, tmp_report_file)
    with open(file_to_parse, 'w') as f:
        f.write(bytes_input.decode('UTF-8'))

    analyzer_module = import_firehose_parser(analyzer)

    analysis_as_json = None
    firehose_result = None
    if (analyzer_module):
        with open(file_to_parse, 'r+') as f:
            analysis_instance = analyzer_module.parse_file(f)
            firehose_result = analysis_instance.to_xml_bytes().decode("utf-8")
            f.seek(0)
            f.truncate()
            f.write(firehose_result)
        with open(file_to_parse, 'r+') as f:
            analysis_as_json = to_json(Analysis.from_xml(f))

    shutil.rmtree(tempdir)
    return json.dumps(analysis_as_json)


def import_firehose_parser(parser):
    """Import a firehose parser.

    parser: The name of the parser that will be imported
    :returns: Some firehose parser
    """
    try:
        return import_module("firehose.parsers.%s" % (parser))
    except ImportError:
        print("ERROR: Firehose parser %s not found" % parser)
