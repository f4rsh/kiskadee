"""Continous static analysis package.

kiskadee runs different static analyzers on a set of pre-defined software
repositories. When the kiskadee package is loaded, we load all the
fetcher names in the fetchers subpackages.

The following variables and functions are exported:
    - kiskadee_fetchers_list - a list of all enabled fetcher names
    - load_fetchers() - a function to load all enabled fetchers
    - config - a ConfigParser object with kiskadee configurations

Modules:
    - analyzers
    - converter
    - database
    - model
    - monitor
    - queue
    - runner

Subpackages:
    fetchers
"""
import os
import importlib
import configparser
import logging
import sys

__version__ = '0.4.5~dev'

_my_path = os.path.dirname(os.path.realpath(__file__))

# Handle fetcher system
kiskadee_fetchers_list = []

_fetchers_path = os.path.join(_my_path, 'fetchers')
_fetchers_pkg_files = [f for f in os.listdir(_fetchers_path) if
                       os.path.isfile(os.path.join(_fetchers_path, f))]
_fetchers_pkg_files.remove('__init__.py')
for fetcher in _fetchers_pkg_files:
    fetcher_name, file_ext = os.path.splitext(fetcher)
    if file_ext == '.py':  # We don't want pyc files when running with python 2
        kiskadee_fetchers_list.append(fetcher_name)


def load_fetchers():
    """Load kiskadee fetchers.

    This function loads all active fetchers(see kiskadee.conf documentation)
    and returns a list with each module object imported this way.
    """
    fetchers = []
    for fetcher in kiskadee_fetchers_list:
        if config[fetcher + '_fetcher'].getboolean('active'):
            fetchers.append(importlib.import_module(
                'kiskadee.fetchers.' + fetcher))
    return fetchers


# Load kiskadee configurations
_config_file_name = 'kiskadee.conf'
_sys_config_file = os.path.join('/etc', _config_file_name)
_dev_config_file = os.path.join(os.path.dirname(_my_path),  # go up a dir
                                'util', _config_file_name)
_doc_config_file = os.path.join(os.path.dirname(_my_path),
                                'util', _config_file_name)
_defaults = {}
if not os.path.exists(_sys_config_file):
    # log _sys_config_file not found
    # raise ValueError("No such file or directory: %s" % _sys_config_file)
    pass
if not os.path.exists(_dev_config_file):
    # log _dev_config_file not found
    pass

config = configparser.ConfigParser(defaults=_defaults)

_read = config.read([_dev_config_file, _sys_config_file, _doc_config_file])
if len(_read) < 1:
    raise ValueError("Invalid config files. Should be either %s or %s or %s" %
                     (_sys_config_file, _dev_config_file, _doc_config_file))
    # log no config files were loaded
    pass
elif len(_read) == 2 or _read[0] == _sys_config_file:
    # log _sys_config_file found loaded
    pass
else:
    # log _read[0] loaded
    pass

log_file = config['DEFAULT']['log_file']
logger = logging.getLogger(__name__)

formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if log_file != 'stdout':
    _debug = logging.FileHandler(log_file, mode='w+')
else:
    _debug = logging.StreamHandler(sys.stdout)

_debug.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(_debug)
