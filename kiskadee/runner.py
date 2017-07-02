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
kiskadee.model.Base.metadata.create_all(engine)
kiskadee.model.Base.metadata.bind = engine

def runner():
    """Run static analyzers.
    Continuously dequeue packages from `analyses_queue` and call the
    :func:`analyze` method, passing the dequeued package. After the analysis,
    updates the status of this package on the database.
    """
    while running:
        if not kiskadee.queue.is_empty():
            kiskadee.logger.debug('RUNNER: dequeuing...')
            package = kiskadee.queue.dequeue_analysis()
            kiskadee.logger.debug('RUNNER: dequeued %s-%s from %s'
                                  % (package['name'],
                                     package['version'],
                                     package['plugin'].__name__))
            analyze(package)


def analyze(package):
    """Run each analyzer on a package.

    The package dict is in the queue. The keys are:
        plugin: the plugin module itself
        name: the package name
        version: the package version
        path: plugin default path for packages
        return: list with firehose reports
    """
    plugin = package['plugin'].Plugin()
    kiskadee.logger.debug(
            'ANALYSIS: Downloading {} '
            'source...'.format(package['name'])
    )
    compressed_source = plugin.get_sources(package)
    pkg = (session.query(kiskadee.model.Package).
            filter(kiskadee.model.Package.name == package['name']).
            first())
    if compressed_source:
        kiskadee.logger.debug('ANALYSIS: Downloaded!')
        kiskadee.logger.debug('ANALYSIS: Unpacking...')
        reports = []
        path = tempfile.mkdtemp()
        shutil.unpack_archive(compressed_source, path)
        with kiskadee.helpers.chdir(path):
            kiskadee.logger.debug('ANALYSIS: Unpacked!')
            analyzers = plugin.analyzers()
            for analyzer in analyzers:
                kiskadee.logger.debug('ANALYSIS: running %s ...' % analyzer)
                try:
                    analysis = kiskadee.analyzers.run(analyzer, path)
                    firehose_report = kiskadee.converter.to_firehose(analysis,
                                                                 analyzer)
                    analysed_version = pkg.versions[-1].id
                    kiskadee.logger.debug(
                        "Saving analysis of {} on {} version {}"
                        .format(analyzer, pkg.name, pkg.versions[-1].number)
                    )
                    self._save_source_analysis(
                            analysed_version, firehose_report, analyzer
                    )
                    kiskadee.logger.debug(
                            'ANALYSIS: DONE {} analysis'.format(analyzer)
                    )
                except Exception as err:
                    kiskadee.logger.debug('RUNNER: could not generate analysis')
                    kiskadee.logger.debug(err)
            # TODO: remove compressed/uncompressed files after the analysis
    else:
        kiskadee.logger.debug('RUNNER: invalid source dict')

def _save_source_analysis(self, version_id, analysis, analyzer):
    _analysis = kiskadee.model.Analysis()
    try:
        _analyzer = session.query(Analyzers).\
            filter(Analyzer.name == analyzer).first()
        _analysis.analyzer_id = _analyzer.id
        _analysis.version_id = version_id
        _analysis.raw = analysis
        session.add(_analysis)
    except Exception as err:
        kiskadee.logger.debug(
            "The required analyzer was not registered in kiskadee"
        )
        kiskadee.logger.debug(err)
