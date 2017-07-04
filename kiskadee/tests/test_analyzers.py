import os
from unittest import TestCase

from kiskadee.runner import _analyze, _path_to_uncompressed_source
import kiskadee.plugins.example


class TestAnalyzers(TestCase):

    def setUp(self):
        self.plugin = kiskadee.plugins.debian.Plugin()
        self.deb_pkg = {'name': 'test',
                        'version': '1.0.0',
                        'plugin': kiskadee.plugins.debian
                        }

    def test_run_analyzer(self):

        source_to_analysis = {
                'name': 'test',
                'version': '1.0.0',
                'plugin': kiskadee.plugins.example
        }

        source_path = _path_to_uncompressed_source(
                source_to_analysis, kiskadee.plugins.example.Plugin()
        )
        firehose_report = _analyze(self.deb_pkg, "cppcheck", source_path)
        self.assertIsNotNone(firehose_report)
