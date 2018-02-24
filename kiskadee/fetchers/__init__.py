"""Fetcher package.

Each kiskadee fetcher must be a module in this package that implements the
Fetcher class here defined.
"""

import os
import abc
import inspect
import kiskadee
import urllib.request

import kiskadee.queue

class Fetcher(abc.ABC):
    """Abstract Fetcher class."""

    def __init__(self):
        """Return a new kiskadee Fetcher.

        The fetcher name is the module name.
        There MUST be a [FETCHER_NAME_fetcher] section in kiskadee.conf
        for each fetcher. Refer to the configuration file documentation
        for more information.
        """
        full_name = inspect.getmodule(self).__name__
        self.name = full_name.split('.')[-1]
        config_section = self.name + '_fetcher'
        self.config = kiskadee.config[config_section]

    @abc.abstractmethod
    def get_sources(package):
        """Return the absolute path of compressed package source code.

        `source_data` will be a dictionary previously created by the fetcher.
        `source_data` will have at least two obrigatory keys: `name` and
        `version` of the package that have to be downloaded.
        """
        raise NotImplementedError('get_sources must be defined by fetcher')

    def watch(self, **kwargs):
        """Continuously monitor some target repository.
        This method will be called as a thread, and will run concurrently with
        the main kiskadee thread. The monitoring process must be done by
        classes that heritage from this one. This method is only responsible
        to enqueue new monitored projects, so must be called by it childrens.
        """
        project = kwargs
        if not project:
            raise NotImplementedError('fetcher must call parent watch method ')

        kiskadee.queue.Queues().enqueue_project(project)
        fetcher = project['fetcher']
        kiskadee.logger.debug(
                "{} fetcher: sending package {}_{} for monitor"
                .format(fetcher, project['name'], project['version'])
            )

    @abc.abstractmethod
    def compare_versions(self, new, old):
        """Return *true* if `new` is greater then `old`.

        `new` and `old` will be the versions of packages monitored by your
        fetcher.
        """
        raise NotImplementedError(
                'compare_versions must be defined by fetcher'
            )

    def analyzers(self):
        """Get active analyzers for current fetcher.

        This information should live in kiskadee's configuration file as
        the name of each analyzer separated by spaces.
        """
        if not self.config.get('analyzers'):
            fetcher_name = self.name + '_fetcher'
            return kiskadee.config[fetcher_name].get('analyzers').split()
        else:
            return self.config.get('analyzers').split()

    def download(self, path, url, file_name):
        """Download something from the internet.

        :path: The path where the file will be placed when downloaded.
        :url: Url of the file.
        :file_name: The name of the file that will be saved on the disc.
        :return: The absolute path to the downloaded file.
        """
        try:
            in_file = urllib.request.urlopen(url)
            data = in_file.read()
            download_path = os.path.join(path, file_name)
            with open(download_path, 'wb') as info:
                info.write(data)
            kiskadee.logger.debug(
                    "Downloaded {} source in {} path".format(file_name, path)
                    )
            return download_path
        except Exception as err:
            kiskadee.logger.debug(
                    "Cannot download {} "
                    "file".format(file_name)
            )
            kiskadee.logger.debug(err)
            return None
