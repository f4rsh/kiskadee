"""Fetcher to monitor Debian Project Packages."""

import os
import tempfile
import urllib.request
import urllib.error
from time import sleep
import re
import shutil
from debian.deb822 import Sources
import subprocess

import kiskadee.queue

RUNNING = True


class Fetcher(kiskadee.fetchers.Fetcher):
    """Fetcher to monitor Debian Project Packages."""

    def watch(self):
        """Start the monitoring process for Debian Repositories.

        Each project monitored by the fetcher will be
        queued by calling the watch parent method,
        passing the project data as argument.
        """
        kiskadee.logger.debug("Starting Debian fetcher")
        while RUNNING:
            url = self._sources_gz_url()
            try:
                sources_gz_dir = self._download_sources_gz(url)
                self._uncompress_gz(sources_gz_dir)
                self._queue_sources_gz_pkgs(sources_gz_dir)
                sleep(float(self.config['schedule']) * 60)
                shutil.rmtree(sources_gz_dir)
            except urllib.error.URLError:
                kiskadee.logger.debug("Cannot reach debian mirror")

    def get_sources(self, source_data):
        """Download packages from some debian mirror."""
        tmp_path = tempfile.gettempdir()
        path = tempfile.mkdtemp(dir=tmp_path)
        url = self._dsc_url(source_data)
        try:
            subprocess.check_output(
                    "(cd {} && dget {} -u -q)".format(path, url), shell=True
                )
            return ''.join([path, '/', self._source_path(path)])
        except Exception as err:
            kiskadee.logger.debug(
                    'Cannot download {} source'
                    .format(source_data['name']))
            kiskadee.logger.debug(err)
            return None

    def compare_versions(self, new, old):
        """Compare Debian package versions using dpkg."""
        try:
            subprocess.check_output(['dpkg', '--compare-versions', new, 'gt',
                                     old])
            return True
        except Exception:
            return False

    def _source_path(self, path):
        """Return the path to the *.orig.tar.gz."""
        files = os.listdir(path)
        prog = re.compile(".orig.")
        return [x for x in files if prog.search(x)
                and x.find("asc") == -1][0]

    def _queue_sources_gz_pkgs(self, path):
        sources = os.path.join(path, 'Sources')
        with open(sources) as sources_file:
            for src in Sources.iter_paragraphs(sources_file):
                project = self.project_to_enqueue(src)
                super().watch(**project)

    def project_to_enqueue(self, src):
        return {'name': src["Package"],
                'version': self._parse_version(src["Version"]),
                'fetcher': __name__,
                'meta': {'directory': src['Directory']}
                }

    def _parse_version(self, version):
        if version.find(":") > -1:
            return version.split(":")[1]
        return version

    def _dsc_url(self, source_data):
        """Build dsc url to download a debian package sources.

        This url is required by dget. e.g.:
        dget http://ftp.debian.org/debian/pool/main/0/0ad/0ad_0.0.21-2.dsc

        """
        name = source_data['name']
        version = source_data['version']
        directory = source_data['meta']['directory']
        return ''.join([self.config['target'], '/',
                        directory, '/', name, '_', version, '.dsc'])

    def _sources_gz_url(self):
        """Mount the Sources.gz url."""
        return "%s/dists/%s/main/source/Sources.gz" % (self.config['target'],
                                                       self.config['release'])

    def _download_sources_gz(self, url):
        """Download and Extract the Sources.gz file, from some Debian Mirror.

        :data: The config.json file as a dict
        :returns: The path to the Sources.gz file

        """
        tmp_path = tempfile.gettempdir()
        path = tempfile.mkdtemp(dir=tmp_path)
        return os.path.dirname(self.download(path, url, 'Sources.gz'))

    def _uncompress_gz(self, path):
        """Extract Some .gz file."""
        compressed_file_path = os.path.join(path, self.config['meta'])
        subprocess.check_output(['gzip', '-d', '-k', '-f',
                                 compressed_file_path])
        return path
