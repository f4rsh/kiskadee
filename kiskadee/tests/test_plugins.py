from unittest import TestCase
import os
import shutil
import tempfile
import zmq
import threading
import time

import kiskadee.queue


class TestPlugins(TestCase):
    def test_loading(self):
        _config = kiskadee.config
        _config['debian_plugin'] = {'active': 'no'}
        _config['juliet_plugin'] = {'active': 'yes'}
        _config['example_plugin'] = {'active': 'yes'}
        kiskadee.config = _config
        plugins = kiskadee.load_plugins()
        for plugin in plugins:
            name_index = len(plugin.__name__.split('.')) - 1
            name = plugin.__name__.split('.')[name_index]
            self.assertTrue(name != 'debian')


class TestDebianPlugin(TestCase):

    def setUp(self):
        import kiskadee.plugins.debian
        self.debian_plugin = kiskadee.plugins.debian.Plugin()
        self.data = self.debian_plugin.config

    def mock_download_sources_gz(self):
        path = tempfile.mkdtemp()
        source = 'kiskadee/tests/test_source/Sources.gz'
        shutil.copy2(source, path)
        return path

    def test_mount_sources_gz_url(self):
        mirror = self.data['target']
        release = self.data['release']
        url = self.debian_plugin._sources_gz_url()
        expected_url = "%s/dists/%s/main/source/Sources.gz" % (mirror, release)
        self.assertEqual(url, expected_url)

    def test_uncompress_sources_gz(self):
        temp_dir = tempfile.mkdtemp()
        self.debian_plugin._download_sources_gz = self.mock_download_sources_gz
        temp_dir = self.debian_plugin._download_sources_gz()
        self.debian_plugin._uncompress_gz(temp_dir)
        files = os.listdir(temp_dir)
        shutil.rmtree(temp_dir)
        self.assertTrue('Sources' in files)

    def test_enqueue_a_valid_pkg(self):
        temp_dir = tempfile.mkdtemp()
        self.debian_plugin._download_sources_gz = self.mock_download_sources_gz
        temp_dir = self.debian_plugin._download_sources_gz()
        self.debian_plugin._uncompress_gz(temp_dir)
        self.debian_plugin._queue_sources_gz_pkgs(temp_dir)
        shutil.rmtree(temp_dir)
        some_pkg = kiskadee.queue.dequeue_package()
        self.assertTrue(isinstance(some_pkg, dict))
        self.assertIn('name', some_pkg)
        self.assertIn('version', some_pkg)
        self.assertIn('plugin', some_pkg)
        self.assertIn('meta', some_pkg)
        self.assertIn('directory', some_pkg['meta'])

    def test_mount_dsc_url(self):
        expected_dsc_url = ("http://ftp.us.debian.org" +
                            "/debian/pool/main/0/0ad/0ad_0.0.21-2.dsc")
        sample_package = {'name': '0ad',
                          'version': '0.0.21-2',
                          'meta': {'directory': 'pool/main/0/0ad'}}
        url = self.debian_plugin._dsc_url(sample_package)
        self.assertEqual(expected_dsc_url, url)

    def test_compare_gt_version(self):
        new = '1.1.1'
        old = '1.1.0'
        result = self.debian_plugin.compare_versions(new, old)
        self.assertTrue(result)

    def test_compare_smallest_version(self):
        new = '8.5-2'
        old = '8.6-0'
        result = self.debian_plugin.compare_versions(new, old)
        self.assertFalse(result)

    def test_compare_equal_version(self):
        new = '3.3.3-0'
        old = '3.3.3-0'
        result = self.debian_plugin.compare_versions(new, old)
        self.assertFalse(result)


class TestAnityaPlugin(TestCase):

    def setUp(self):
        import kiskadee.plugins.anitya
        self.anitya_plugin = kiskadee.plugins.anitya.Plugin()

        self.msg = "anitya {'body':{'msg':{'project':{name: 'urlscan',"\
                   "'version':'0.8.5','backend':'GitHub',"\
                   "'homepage':'https://github.com/firecat53/urlscan'}}}}"

        self.msg1 = "{'body':{'msg':{'project':{name: 'urlscan',"\
                    "'version':'0.8.5','backend':'GitHub',"\
                    "'homepage':'https://github.com/firecat53/urlscan'}}}}"

    def test_connect_to_zmq(self):

        def zmq_server():
            context = zmq.Context()
            socket = context.socket(zmq.PUB)
            socket.bind("tcp://*:7776")

        zmq_server()
        socket = self.anitya_plugin._connect_to_zmq("7776", "anitya")
        self.assertIsNotNone(socket)

    def test_receive_msg_from_zmq(self):
        """definitely this is not a unit test, but is important to kiskadee
        be able to interact correctly with ZeroMQ.
        We need to define other test levels to kiskadee asap.
        When we do that, we can move integration tests
        to a proper place. For now we will maintain this test here"""

        def zmq_server():
            context = zmq.Context()
            socket = context.socket(zmq.PUB)
            socket.bind("tcp://*:5556")
            time.sleep(1)
            socket.send_string("%s" % (self.msg))
            time.sleep(1)

        def receive_msg_from_server():
            client_socket = self.anitya_plugin._connect_to_zmq(
                    "5556", "anitya")
            if client_socket:
                response = client_socket.recv_string()
                results[0] = response[response.find(" ")+1::]
            else:
                results[0] = "invalid"

        results = [None]

        client_as_thread = threading.Thread(target=receive_msg_from_server)
        server_as_thread = threading.Thread(
                target=zmq_server)

        server_as_thread.start()
        client_as_thread.start()
        server_as_thread.join()
        self.assertEqual(self.msg1, results[0])

    def test_compare_versions(self):
        is_greater = self.anitya_plugin.compare_versions('0.8.5-2', '0.8.5-1')
        self.assertTrue(is_greater)

    def test_load_backend(self):
        backend = self.anitya_plugin._load_backend('github')
        self.assertIsNotNone(backend)

    def test_not_load_backend(self):
        backend = self.anitya_plugin._load_backend('foo')
        self.assertEqual(backend, {})

    def test_get_sources(self):

        def mock_github(self, source_data, path):
            return 'kiskadee/tests/test_source/Sources.gz'

        kiskadee.plugins.anitya.Backends.github = mock_github
        source_data = {'meta': {'backend': 'GitHub'}}
        source_path = self.anitya_plugin.get_sources(source_data)
        self.assertEqual(source_path, mock_github("self", "foo", "bla"))

    def test_create_package_dict(self):

        self.anitya_plugin._create_package_dict(self.msg)
        _dict = kiskadee.queue.dequeue_package()
        self.assertEqual(_dict['name'], 'urlscan')
        self.assertEqual(_dict['version'], '0.8.5')
        self.assertEqual(_dict['meta']['backend'], 'GitHub')
        self.assertEqual(
                _dict['meta']['homepage'],
                'https://github.com/firecat53/urlscan'
        )
        self.assertEqual(_dict['plugin'], kiskadee.plugins.anitya)
