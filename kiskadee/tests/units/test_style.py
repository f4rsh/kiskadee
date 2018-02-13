# Thanks bodhi
# https://github.com/fedora-infra/bodhi/blob/develop/bodhi/tests/test_style.py

import os
import subprocess
import unittest

KISKADEE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class TestStyle(unittest.TestCase):
    def test_with_flake8(self):
        """Enforce PEP-8"""
        flake8_command = ['flake8', KISKADEE_PATH]
        self.assertEqual(subprocess.call(flake8_command), 0)

    def test_with_pydocstyle(self):
        """Enforce PEP-257"""
        pydocstyle_command = ['pydocstyle', KISKADEE_PATH]
        self.assertEqual(subprocess.call(pydocstyle_command), 0)
