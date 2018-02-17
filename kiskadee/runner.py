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

    def __init__(self):
        """Return a non initialized Runner."""
        self.queues = None

    def runner(self, queues):
        """Run static analyzers.

        Continuously dequeue packages from `analyses_queue` and call the
        :func:`analyze` method, passing the dequeued package.
        After the analysis, updates the status of this package on the database.
        """
        kiskadee.logger.debug('Starting runner subprocess')
        kiskadee.logger.debug('runner PID: {}'.format(os.getpid()))
        session = kiskadee.database.Database().session
        kiskadee.model.Analyzer.create_analyzers(session)
        self.queues = queues
        while RUNNING:
            kiskadee.logger.debug('RUNNER: Waiting to dequeue'\
                                  ' project to analysis...')
            source_to_analysis = self.queues.dequeue_analysis()
            kiskadee.logger.debug(
                    'RUNNER: deqeued {}-{} from {}'
                    .format(source_to_analysis['name'],
                            source_to_analysis['version'],
                            source_to_analysis['fetcher'])
                )
            self.call_analyzers(source_to_analysis)

    def call_analyzers(self, source_to_analysis):
        """Iterate over the package analyzers.

        For each analyzer defined to analysis the source, call
        the function :func:`analyze`, passing the source dict, the analyzer
        to run the analysis, and the path to a compressed source.
        """
        fetcher = importlib.import_module(source_to_analysis['fetcher']).Fetcher()
        source_path = self._path_to_uncompressed_source(
                source_to_analysis, fetcher
        )
        if not source_path:
            return None

        analyzers = fetcher.analyzers()
        source_to_analysis['results'] = {}
        for analyzer in analyzers:
            firehose_report = self.analyze(analyzer, source_path)
            if firehose_report:
                source_to_analysis['results'][analyzer] = firehose_report

        if source_to_analysis['results']:
            kiskadee.logger.debug(
                    "RUNNER: Sending {}-{} to Monitor"
                    .format(source_to_analysis["name"],
                            source_to_analysis["version"])
                )
            self.queues.enqueue_result(source_to_analysis)
        shutil.rmtree(source_path)

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

    def _path_to_uncompressed_source(self, package, fetcher):

        if not (fetcher and package):
            return None

        kiskadee.logger.debug(
                'ANALYSIS: Downloading {} '
                'source...'.format(package['name'])
        )

        compressed_source = fetcher.get_sources(package)

        if compressed_source:
            kiskadee.logger.debug(
                    'ANALYSIS: Downloaded {} source in {} path'
                    .format(
                        package['name'],
                        os.path.dirname(compressed_source)
                    )
                )
            tmp_path = tempfile.gettempdir()
            uncompressed_source_path = tempfile.mkdtemp(dir=tmp_path)
            try:
                shutil.unpack_archive(
                        compressed_source,
                        uncompressed_source_path
                    )
                kiskadee.logger.debug(
                        'ANALYSIS: Unpacking {} source in {} path'
                        .format(package['name'], uncompressed_source_path)
                        )
                # not delete the source code used on tests.
                if not compressed_source.find("kiskadee/tests") > -1:
                    shutil.rmtree(os.path.dirname(compressed_source))
                    kiskadee.logger.debug(
                            'ANALYSIS: Remove {} temp directory'
                            .format(os.path.dirname(compressed_source))
                        )
                kiskadee.logger.debug(
                        'ANALYSIS: Unpacked {} source'.format(package['name'])
                        )
                return uncompressed_source_path
            except Exception as err:
                kiskadee.logger.debug('Something went wrong')
                kiskadee.logger.debug(err)
                return None
        else:
            kiskadee.logger.debug('RUNNER: invalid compressed source')
            return None
