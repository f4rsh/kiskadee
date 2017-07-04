"""Run each static analyzer in each package marked for analysis."""

import shutil
import tempfile
import kiskadee.queue
import kiskadee.analyzers
import kiskadee.model
import kiskadee.database
import kiskadee.helpers
import kiskadee.converter

running = True
database = kiskadee.database
engine = database.engine
session = database.session


def runner():
    """Run static analyzers.
    Continuously dequeue packages from `analyses_queue` and call the
    :func:`analyze` method, passing the dequeued package. After the analysis,
    updates the status of this package on the database.
    """
    kiskadee.logger.debug('Starting runner component')
    while running:
        if not kiskadee.queue.is_empty():
            kiskadee.logger.debug('RUNNER: dequeuing...')
            source_to_analysis = kiskadee.queue.dequeue_analysis()
            kiskadee.logger.debug('RUNNER: dequeued %s-%s from %s'
                                  % (source_to_analysis['name'],
                                     source_to_analysis['version'],
                                     source_to_analysis['plugin'].__name__))

            _call_analyzers(source_to_analysis)


def _call_analyzers(source_to_analysis):
            plugin = source_to_analysis['plugin'].Plugin()
            source_path = _path_to_uncompressed_source(
                    source_to_analysis, plugin
            )
            analyzers = plugin.analyzers()
            for analyzer in analyzers:
                firehose_report = _analyze(
                        source_to_analysis, analyzer, source_path
                )
                _save_source_analysis(
                        source_to_analysis, firehose_report, analyzer
                )

            session.commit()


def _analyze(source_to_analysis, analyzer, source_path):
    """Run each analyzer on a source_to_analysis.

    The source_to_analysis dict is in the queue. The keys are:
        plugin: the plugin module itself
        name: the package name
        version: the package version
        path: plugin default path for packages
        return: list with firehose reports
    """

    if source_path is None:
        return None

    with kiskadee.helpers.chdir(source_path):
            kiskadee.logger.debug('ANALYSIS: running {} ...'.format(analyzer))
            try:
                analysis = kiskadee.analyzers.run(analyzer, source_path)
                firehose_report = kiskadee.converter.to_firehose(analysis,
                                                                 analyzer)
                kiskadee.logger.debug(
                        'ANALYSIS: DONE {} analysis'.format(analyzer)
                )
                return firehose_report
            except Exception as err:
                kiskadee.logger.debug('RUNNER: could not generate analysis')
                kiskadee.logger.debug(err)
        # TODO: remove compressed/uncompressed files after the analysis


def _save_source_analysis(source_to_analysis, analysis, analyzer):

    if analysis is None:
        return None

    source_name = source_to_analysis['name']
    source_version = source_to_analysis['version']

    kiskadee.logger.debug(
        "Saving analysis of {} on package {}-{}"
        .format(analyzer, source_name, source_version)
    )
    package = (
            session.query(kiskadee.model.Package)
            .filter(kiskadee.model.Package.name == source_name).first()
    )
    version_id = package.versions[-1].id
    _analysis = kiskadee.model.Analysis()
    try:
        _analyzer = session.query(kiskadee.model.Analyzer).\
            filter(kiskadee.model.Analyzer.name == analyzer).first()
        _analysis.analyzer_id = _analyzer.id
        _analysis.version_id = version_id
        _analysis.raw = analysis
        session.add(_analysis)
    except Exception as err:
        kiskadee.logger.debug(
            "The required analyzer was not registered in kiskadee"
        )
        kiskadee.logger.debug(err)


def _path_to_uncompressed_source(package, plugin):
    kiskadee.logger.debug(
            'ANALYSIS: Downloading {} '
            'source...'.format(package['name'])
    )
    compressed_source = plugin.get_sources(package)
    if compressed_source:
        kiskadee.logger.debug('ANALYSIS: Downloaded!')
        kiskadee.logger.debug('ANALYSIS: Unpacking...')
        path = tempfile.mkdtemp()
        shutil.unpack_archive(compressed_source, path)
        kiskadee.logger.debug('ANALYSIS: Unpacked!')
        return path
    else:
        kiskadee.logger.debug('RUNNER: invalid compressed source')
        return None
