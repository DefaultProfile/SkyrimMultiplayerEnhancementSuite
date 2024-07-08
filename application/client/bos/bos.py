import configparser

def load_bos_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    return config
