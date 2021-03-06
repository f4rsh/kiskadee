"""Run each static analyzer in each package marked for analysis."""

import shutil
import tempfile
import os
import importlib

import kiskadee.analyzers
import kiskadee.model
import kiskadee.database
import kiskadee.converter

RUNNING = True


class Runner:
    """Provide kiskadee runner objects."""

    def __init__(self, queues):
        """Return a non initialized Runner."""
        self.queues = queues
        self.fetcher = None
        self.package = None

    def run(self):
        """Run static analyzers.

        Continuously dequeue packages from `analyses_queue` and call the
        :func:`analyze` method, passing the dequeued package as argument.
        After the analysis, send the result back to Monitor.
        """
        kiskadee.logger.debug('RUNNER PID: {}'.format(os.getpid()))
        while RUNNING:
            kiskadee.logger.debug('RUNNER STATE: Idle.')
            self.package = self.queues.dequeue_analysis()
            self.call_analyzers()

    def import_package_fetcher(self):
        try:
            return importlib.import_module(
                    self.package['fetcher']
                    ).Fetcher()
        except ModuleNotFoundError:
            kiskadee.logger.debug("RUNNER STATE: Fetcher {}\
                    could not be loaded".format(self.package['fetcher'])
                )
            return {}

    def run_analysis(self, analyzers, source_path):
        self.package['results'] = {}
        for analyzer in analyzers:
            firehose_report = self.analyze(analyzer, source_path)
            if firehose_report:
                self.package['results'][analyzer] = firehose_report
        return self.package


    def rmdtemp(self, temp_dir):
        # not delete the source code used on tests.
        if not temp_dir.find("kiskadee/tests") > -1:
            shutil.rmtree(temp_dir)

    def call_analyzers(self):
        """Iterate over the package analyzers.

        For each analyzer defined to analysis the source, call
        the function :func:`analyze`, passing the source dict, the analyzer
        to run the analysis, and the path to a compressed source.
        """
        self.fetcher = self.import_package_fetcher()
        source_path = self.get_package_code_path()
        if not source_path:
            return None

        analyzers = self.fetcher.analyzers()
        analysis_result = self.run_analysis(
                analyzers, source_path
                )
        self.enqueue_analysis_to_monitor(analysis_result)
        self.rmdtemp(source_path)

    def enqueue_analysis_to_monitor(self, analysis_result):
        if analysis_result['results']:
            self.queues.enqueue_result(analysis_result)

    def analyze(self, analyzer, source_path):
        """Run each analyzer on some sorce code.

        The `analyzer` is the name of a static analyzer already created on the
        database.
        The `source_path` is the directory to a uncompressed source, returned
        by the :func:`get_package_code_path`.
        """
        if source_path is None:
            return None

        kiskadee.logger.debug('RUNNER STATE: analysing with {} ...'\
                .format(analyzer))
        try:
            analysis = kiskadee.analyzers.run(analyzer, source_path)
            firehose_report = kiskadee.converter.to_firehose(
                    analysis, analyzer
                )
            kiskadee.logger.debug(
                    'RUNNER STATE: DONE {} analysis'
                    .format(analyzer)
                )
            return firehose_report
        except Exception as err:
            kiskadee.logger.debug('RUNNER STATE: could not generate analysis')
            kiskadee.logger.debug(err)
            return None

    def get_package_code_path(self):
        """ Returns a string, representing the path of the uncompressed
        package source."""
        if not (self.fetcher and self.package):
            return None

        compressed_source_path = self.fetcher.get_sources(self.package)
        if compressed_source_path :
            uncompressed_source_path = self.uncompress_package_code(
                    compressed_source_path
                    )
            self.rmdtemp(os.path.dirname(compressed_source_path))
            return uncompressed_source_path
        else:
            kiskadee.logger.debug('RUNNER: invalid compressed source')
            return None

    def uncompress_package_code(self, compressed_source):
        dir_to_unpack_source = tempfile.mkdtemp()
        try:
            shutil.unpack_archive(compressed_source,
                    dir_to_unpack_source)
            return dir_to_unpack_source
        except Exception as err:
            kiskadee.logger.debug('RUNNER STATE: Could not unpack'\
                    'package source')
            kiskadee.logger.debug(err)
            return {}

