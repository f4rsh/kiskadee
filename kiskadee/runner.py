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

    def __init__(self, session, queues):
        """Return a non initialized Runner."""
        self.queues = queues
        self.session = session
        kiskadee.model.Analyzer.create_analyzers(self.session)
        self.fetcher = None

    def runner(self, queues):
        """Run static analyzers.

        Continuously dequeue packages from `analyses_queue` and call the
        :func:`analyze` method, passing the dequeued package.
        After the analysis, updates the status of this package on the database.
        """
        kiskadee.logger.debug('Runner PID: {}'.format(os.getpid()))
        while RUNNING:
            kiskadee.logger.debug('RUNNER: Waiting to dequeue'\
                                  ' project to analysis...')
            project_to_analysis = self.queues.dequeue_analysis()
            self.call_analyzers(project_to_analysis)

    def load_project_fetcher(self, project_to_analysis):
        try:
        return importlib.import_module(
                project_to_analysis['fetcher']
                ).Fetcher()
        except ModuleNotFoundError:
            kiskadee.logger.debug("Fetcher {} could not be loaded"\
                    .format(project_to_analysis['fetcher'])
                )
            return {}

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

    def run_analysis(self, analyzers, project_to_analysis):
        project_to_analysis['results'] = {}
        for analyzer in analyzers:
            firehose_report = self.analyze(analyzer, source_path)
            if firehose_report:
                project_to_analysis['results'][analyzer] = firehose_report
        return project_to_analysis


    def clean_temporary_directory(self, dir):
        # not delete the source code used on tests.
        if not compressed_source_path .find("kiskadee/tests") > -1:
            shutil.rmtree(os.path.dirname(dir))

    def call_analyzers(self, project_to_analysis):
        """Iterate over the package analyzers.

        For each analyzer defined to analysis the source, call
        the function :func:`analyze`, passing the source dict, the analyzer
        to run the analysis, and the path to a compressed source.
        """
        self.fetcher = self.load_project_fetcher(project_to_analysis)
        source_path = self.prepare_to_get_project_code(project_to_analysis)
        if not source_path:
            return None

        analyzers = fetcher.analyzers()
        analysis_result = self.run_analysis(analyzers, project_to_analysis)
        self.enqueue_analysis_to_monitor(analysis_result)
        self.clean_temporary_directory(source_path)

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

    def prepare_to_get_project_code(self, project):

        if not (self.fetcher and project):
            return None

        compressed_source_path = self.fetcher.get_sources(project)
        if compressed_source_path :
            uncompressed_source_path = uncompress_project_code(
                    compressed_source_path
                    )
            self.clean_temporary_directory(os.path.dirname(compressed_source_path))
            return uncompressed_source_path
        else:
            kiskadee.logger.debug('RUNNER: invalid compressed source')
            return None
