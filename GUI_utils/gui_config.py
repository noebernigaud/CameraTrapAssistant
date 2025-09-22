import os
import configparser
import logging

def get_config_file_path():
    """
    Returns the path to the GUI config file.
    """
    return os.path.join(os.path.dirname(__file__), '..', 'commands', 'deepfaune_gui.ini')

def load_checkbox_state():
    """
    Loads the checkbox state from the config file. Returns (do_data, do_move, do_gps) as booleans.
    """
    config = configparser.ConfigParser()
    config_file = get_config_file_path()
    if os.path.exists(config_file):
        config.read(config_file)
        do_data = config.getboolean('options', 'generate_data', fallback=True)
        do_move_empty = config.getboolean('options', 'move_empty', fallback=True)
        do_move_undefined = config.getboolean('options', 'move_undefined', fallback=True)
        do_rename = config.getboolean('options', 'rename_files', fallback=True)
        do_gps = config.getboolean('options', 'add_gps', fallback=False)
    else:
        do_data = True
        do_move_empty = True
        do_move_undefined = True
        do_rename = True
        do_gps = False
    return do_data, do_move_empty, do_move_undefined, do_rename, do_gps

def save_checkbox_state(do_data, do_move_empty, do_move_undefined, do_rename, do_gps):
    """
    Saves the checkbox state to the config file, preserving other sections. Now also saves GPS add checkbox.
    """
    config = configparser.ConfigParser()
    config_file = get_config_file_path()
    if os.path.exists(config_file):
        config.read(config_file)
    if 'options' not in config:
        config['options'] = {}
    config['options']['generate_data'] = str(do_data)
    config['options']['move_empty'] = str(do_move_empty)
    config['options']['move_undefined'] = str(do_move_undefined)  # Save undefined move state
    config['options']['rename_files'] = str(do_rename)
    config['options']['add_gps'] = str(do_gps)
    with open(config_file, 'w') as configfile:
        config.write(configfile)

def load_map_state():
    """
    Loads the last map coordinates and zoom from the config file. Returns (lat, lon, zoom).
    Defaults to Paris and zoom 5 if not set.
    Handles float zoom values.
    """
    config = configparser.ConfigParser()
    config_file = get_config_file_path()
    if os.path.exists(config_file):
        config.read(config_file)
        lat = config.getfloat('map', 'lat', fallback=48.85884)
        lon = config.getfloat('map', 'lon', fallback=2.29435)
        zoom = config.getfloat('map', 'zoom', fallback=5)
        logging.info(f"Loaded map state: lat={lat}, lon={lon}, zoom={zoom}")
    else:
        lat, lon, zoom = 48.85884, 2.29435, 5
    return lat, lon, zoom

def save_map_state(lat, lon, zoom):
    """
    Saves the last map coordinates and zoom to the config file.
    """
    config = configparser.ConfigParser()
    config_file = get_config_file_path()
    if os.path.exists(config_file):
        config.read(config_file)
    if 'map' not in config:
        config['map'] = {}
    config['map']['lat'] = str(lat)
    config['map']['lon'] = str(lon)
    config['map']['zoom'] = str(zoom)
    logging.info(f"Save map state: lat={lat}, lon={lon}, zoom={zoom}")
    with open(config_file, 'w') as configfile:
        config.write(configfile)
