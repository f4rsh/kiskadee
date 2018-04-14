# Change Log

## [Unreleased]

## [0.4.4] - 2018-04-08
### Added
- New test suites (unit, integration, functionals, api, plugins)
- initializer module, responsible for execute as processes runner and monitor.
### Changed
- Refactoring models, Runner and Monitor.
- All code that interacts with database was moved to the model.py module.
### Removed
- Useless tests.

## [0.4.3] - 2018-03-07
### Fixed
- Configuration file system path.
- Anitya github download call.

## [0.4.2] - 2017-11-18
### Added
- systemd units for kiskadee and kiskadee_api.
- kiskadee rpm package.
### Changed
- Major changes on playbook and Vagrantfile.

## [0.4.1] - 2017-11-18
### Changed
- Use white lists for Frama-C analyses.

## [0.4.0] - 2017-11-05
### Added
- Several API improvements.
- Include ansible playbooks for easy deploy.
- Use alembic to manage migrations.
- Add package homepage on package model.
### Changed
- Convert files to firehose in memory.
- Use PostgreSQL JSON type to save analyses.
### Removed
- Python2 support.

## [0.3.1] - 2017-09-07
### Fixed
- Set package version.

## [0.3.0] - 2017-08-27
### Added
- Add endpoint to get a list of analyzed packages.
- Add endpoint to get a analyzed package by it name and version.
- Create page to show the list of analyzed packages.
### Changed
- Save analysis as JSON.

## [0.2.3] - 2017-08-05
### Changed
- Run monitor and runner as separate processes.
- Rename plugin package to fetcher.
### Fixed
- Fix docker issues.
- Fix anitya and debian plugin issues.
- Remove temporary directories used on analysis.

## [0.2.1] - 2017-07-24
### Changed
- Improve kiskadee log messages.
- Save a package only when it is analyzed.
### Fixed
- Fix debian plugin missing packages.

## [0.2] - 2017-07-12
### Added
- flawfinder analyzer.
- scan-build (clang) analyzer.
- frama-c analyzer.
- New anitya plugin.

## [0.1] - 2017-06-12
### Added
- Sphinx documentation.
- Support for configuration file.
- Juliet plugin.
- Debian plugin.
- Convert analyses to firehose.
- cppcheck analyzer.
- Extensible plugin system.
- First kiskadee release.
