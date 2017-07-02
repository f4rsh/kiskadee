"""Continous static analysis package.

kiskadee runs different static analyzers on a set of pre-defined software
repositories. When the kiskadee package is loaded, we load all the plugin names
in the plugins subpackages.

The following variables and functions are exported:
    - kiskadee_plugins_list - a list of all enabled plugin names
    - load_plugins() - a function to load all enabled plugins
    - config - a ConfigParser object with kiskadee configurations

Modules:
    - analyzers
    - converter
    - database
    - helpers
    - model
    - monitor
    - queue
    - runner

Subpackages:
    plugins
"""
import os
import importlib
import configparser
import logging
import sys

from kiskadee.model import Analyzer, Base
import kiskadee.model
import kiskadee.database

__version__ = '0.1.dev0'

_my_path = os.path.dirname(os.path.realpath(__file__))

# Handle plugin system
kiskadee_plugins_list = []

_plugins_path = os.path.join(_my_path, 'plugins')
_plugins_pkg_files = [f for f in os.listdir(_plugins_path) if
                      os.path.isfile(os.path.join(_plugins_path, f))]
_plugins_pkg_files.remove('__init__.py')
for plugin in _plugins_pkg_files:
    plugin_name, file_ext = os.path.splitext(plugin)
    if file_ext == '.py':  # We don't want pyc files when running with python 2
        kiskadee_plugins_list.append(plugin_name)


def load_plugins():
    """Load kiskadee plugins.

    This function loads all active plugins(see kiskadee.conf documentation) and
    returns a list with each module object imported this way.
    """
    plugins = []
    for plugin in kiskadee_plugins_list:
        if config[plugin + '_plugin'].getboolean('active'):
            plugins.append(importlib.import_module(
                'kiskadee.plugins.' + plugin))
    return plugins


# Load kiskadee configurations
_config_file_name = 'kiskadee.conf'
_sys_config_file = os.path.abspath(os.path.join('etc', _config_file_name))
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
logger.addHandler(_warning)
logger.addHandler(_info)

database = kiskadee.database.Database()
engine = database.engine
session = database.session
Base.metadata.create_all(engine)
Base.metadata.bind = engine

def create_analyzers():
    list_of_analyzers = dict(kiskadee.config._sections["analyzers"])
    for name, version in list_of_analyzers.items():
        if not (session.query(Analyzer).filter(Analyzer.name == name).
                filter(Analyzer.version == version).first()):
            new_analyzer = kiskadee.model.Analyzer()
            new_analyzer.name = name
            new_analyzer.version = version
            session.add(new_analyzer)
    session.commit()

create_analyzers()
