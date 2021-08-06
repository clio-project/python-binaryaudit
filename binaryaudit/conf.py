import configparser
config=None
def parse_config():
    ''' Parses the configuration file
    '''
    global config
    config = configparser.ConfigParser()
    config.read('../conf/binaryaudit.conf')

def get_config (section, key):
    global config
    if config == None:
        parse_config()
    return config[section][key]
