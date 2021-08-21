import configparser
import os

config = None
conf_file_dir = None


def parse_config():
    ''' Parses the configuration file
    '''
    global config
    config = configparser.ConfigParser()
    config.read(get_config_dir() + '/binaryaudit.conf')


def get_config(section, key):
    global config
    if config is None:
        parse_config()
    return config[section][key]


def get_config_dir():
    global conf_file_dir
    if conf_file_dir is None:
        _t = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "conf"))
        if os.path.isdir(_t):
            conf_file_dir = _t
    # TODO handle conf data installed through pip
    if conf_file_dir is None:
        raise Exception("Unable to determine the conf dir")
    return conf_file_dir
