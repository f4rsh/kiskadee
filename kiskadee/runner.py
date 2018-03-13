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
        self.project = None

    def run(self):
        """Run static analyzers.

        Continuously dequeue packages from `analyses_queue` and call the
        :func:`analyze` method, passing the dequeued package.
        After the analysis, updates the status of this package on the database.
        """
        kiskadee.logger.debug('Runner PID: {}'.format(os.getpid()))
        while RUNNING:
            kiskadee.logger.debug('RUNNER: Waiting to dequeue'\
                                  ' project to analysis...')
            self.project = self.queues.dequeue_analysis()
            self.call_analyzers()

    def import_project_fetcher(self):
        try:
            return importlib.import_module(
                    self.project['fetcher']
                    ).Fetcher()
        except ModuleNotFoundError:
            kiskadee.logger.debug("Fetcher {} could not be loaded"\
                    .format(self.project['fetcher'])
                )
            return {}

    def run_analysis(self, analyzers, source_path):
        self.project['results'] = {}
        for analyzer in analyzers:
            firehose_report = self.analyze(analyzer, source_path)
            if firehose_report:
                self.project['results'][analyzer] = firehose_report
        return self.project


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
        self.fetcher = self.import_project_fetcher()
        source_path = self.get_project_code_path()
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
        by the :func:`_path_to_uncompressed_source`.
        """
        if source_path is None:
            return None

        kiskadee.logger.debug('ANALYSIS: running {} ...'.format(analyzer))
        try:
            analysis = kiskadee.analyzers.run(analyzer, source_path)
            firehose_report = kiskadee.converter.to_firehose(
                    analysis, analyzer
                )
            kiskadee.logger.debug(
                    'ANALYSIS: DONE {} analysis'
                    .format(analyzer)
                )
            return firehose_report
        except Exception as err:
            kiskadee.logger.debug('RUNNER: could not generate analysis')
            kiskadee.logger.debug(err)
            return None

    def get_project_code_path(self):

        if not (self.fetcher and self.project):
            return None

        compressed_source_path = self.fetcher.get_sources(self.project)
        if compressed_source_path :
            uncompressed_source_path = self.uncompress_project_code(
                    compressed_source_path
                    )
            self.rmdtemp(os.path.dirname(compressed_source_path))
            return uncompressed_source_path
        else:
            kiskadee.logger.debug('RUNNER: invalid compressed source')
            return None

    def uncompress_project_code(self, compressed_source):
        dir_to_unpack_source = tempfile.mkdtemp()
        try:
            shutil.unpack_archive(compressed_source,
                    dir_to_unpack_source)
            return dir_to_unpack_source
        except Exception as err:
            kiskadee.logger.debug('Could not unpack project source')
            kiskadee.logger.debug(err)
            return {}

