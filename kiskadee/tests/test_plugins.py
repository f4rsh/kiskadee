from unittest import TestCase
import unittest
import kiskadee
from kiskadee.helpers import load_config
import importlib
import sys
import os
from os import path, listdir
import shutil
import socket
import tempfile
from kiskadee.queue import dequeue


def is_connected():
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    return False


class TestPlugins(TestCase):
    def test_loading(self):
        kiskadee.load_plugins()
        plugins_path = path.join('kiskadee', 'plugins')
        plugins_pkg_files = [f for f in listdir(plugins_path) if
                             path.isfile(path.join(plugins_path, f))]
        plugins_pkg_files.remove('config.json')
        plugins_pkg_files.remove('__init__.py')
        for plugin in plugins_pkg_files:
            plugin_name, file_ext = path.splitext(plugin)
            self.assertTrue('kiskadee.plugins.' + plugin_name in sys.modules)


class TestDebianPlugin(TestCase):

    def setUp(self):
        self.debian_plugin = kiskadee.plugins.debian
        self.data = self.debian_plugin.PLUGIN_DATA

    def test_generate_randomfile(self):
        path = self.debian_plugin.extracted_source_path()
        shutil.rmtree(path)
        self.assertTrue(isinstance(path, str))

    def test_copy_source_to_path(self):
        source = 'kiskadee/tests/test_source/test_source.tar.gz'
        path = self.debian_plugin.extracted_source_path()
        self.debian_plugin.copy_source(source, path)
        files = os.listdir(path)
        shutil.rmtree(path)
        self.assertTrue('test_source.tar.gz' in files)

    def test_uncompress_tar_gz(self):
        source = 'kiskadee/tests/test_source/test_source.tar.gz'
        path = self.debian_plugin.extracted_source_path()
        self.debian_plugin.copy_source(source, path)
        self.debian_plugin.uncompress_tar_gz(source, path)
        files = os.listdir(path)
        shutil.rmtree(path)
        self.assertTrue('source' in files)

    def test_run_cppcheck(self):
        source = 'kiskadee/tests/test_source/test_source.tar.gz'
        path = self.debian_plugin.extracted_source_path()
        self.debian_plugin.copy_source(source, path)
        self.debian_plugin.uncompress_tar_gz(source, path)
        self.debian_plugin.analyzers().cppcheck(path)
        files = os.listdir('reports')
        shutil.rmtree(path)
        self.assertTrue('firehose_cppcheck_report.xml' in files)

    def test_mount_sources_gz_url(self):
        mirror = self.data['mirror']
        release = self.data['release']
        url = self.debian_plugin.sources_gz_url()
        expected_url = "%s/dists/%s/main/source/Sources.gz" % (mirror, release)
        self.assertEqual(url, expected_url)

    @unittest.skip("This tests depends on a good internet connection")
    def test_download_sources_gz_from_mirror(self):
        """ TODO: Think a better aproach to run this test. Maybe consider
        this test as a integration test, and no unit """

        mirror = self.data['mirror']
        release = self.data['release']
        url = self.debian_plugin.sources_gz_url()
        if is_connected():
            path = self.debian_plugin.download_sources_gz(url)
            files = os.listdir(path)
            shutil.rmtree(path)
            self.assertTrue('Sources' in files)

    def test_create_a_dict_with_sources_gz(self):
        source = 'kiskadee/tests/test_source/Sources.gz'
        temp_dir = tempfile.mkdtemp()
        self.debian_plugin.copy_source(source, temp_dir)
        sources_gz_dir = self.debian_plugin.uncompress_gz(temp_dir)
        self.debian_plugin.queue_sources_gz_pkgs(sources_gz_dir)
        some_pkg = dequeue()
        self.assertTrue(isinstance(some_pkg, dict))
        self.assertIn('name', some_pkg)
        self.assertIn('version', some_pkg)
        self.assertIn('plugin', some_pkg)
        self.assertIn('meta', some_pkg)
        self.assertIn('directory', some_pkg['meta'])
        shutil.rmtree(temp_dir)

    def test_mount_dsc_url(self):
        expected_dsc_url = "http://ftp.us.debian.org/debian/pool/main/0/0ad/0ad_0.0.21-2.dsc"
        sample_package = {'name': '0ad', 
                          'version': '0.0.21-2',
                          'directory': 'pool/main/0/0ad'}
        url = self.debian_plugin.dsc_url(sample_package)
        self.assertEqual(expected_dsc_url, url)
