import configparser
import os

config = None
conf_file_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../conf")


def parse_config():
    ''' Parses the configuration file
    '''
    global config
    config = configparser.ConfigParser()
    config.read(conf_file_dir + '/binaryaudit.conf')


def get_config(section, key):
    global config
    if config is None:
        parse_config()
    return config[section][key]
