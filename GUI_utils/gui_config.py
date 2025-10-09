import os
import configparser
import logging
import sys

# Import project utilities
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from objects.options_config import OptionsConfig

def get_config_file_path():
    """
    Returns the path to the GUI config file.
    """
    return os.path.join(os.path.dirname(__file__), '..', 'deepfaune_gui.ini')

def load_checkbox_state():
    """
    Loads the checkbox state from the config file. Returns an OptionsConfig containing booleans for each option.
    Also loads the time offset selector value as 'time_offset'.
    """
    config = configparser.ConfigParser()
    config_file = get_config_file_path()
    if os.path.exists(config_file):
        config.read(config_file)
        state = OptionsConfig(
            generate_data = config.getboolean('options', 'generate_data', fallback=True),
            generate_stats = config.getboolean('options', 'generate_stats', fallback=True),
            move_empty = config.getboolean('options', 'move_empty', fallback=True),
            move_undefined = config.getboolean('options', 'move_undefined', fallback=True),
            rename_files = config.getboolean('options', 'rename_files', fallback=True),
            add_gps = config.getboolean('options', 'add_gps', fallback=True),
            prediction_threshold = config.getfloat('options', 'prediction_threshold', fallback=0.9),
            get_gps_from_each_file = config.getboolean('options', 'get_gps_from_each_file', fallback=False),
            use_gps_only_for_data = config.getboolean('options', 'use_gps_only_for_data', fallback=False),
            combine_with_data= config.getboolean('options', 'combine_with_data', fallback=False),
            time_offset = config.get('options', 'time_offset', fallback='auto')
        )
    else:
        state = OptionsConfig(
            generate_data = True,
            generate_stats = True,
            move_empty = True,
            move_undefined = True,
            rename_files = True,
            add_gps = False,
            prediction_threshold = 0.9,
            get_gps_from_each_file = False,
            use_gps_only_for_data = False,
            combine_with_data= False,
            time_offset = 'auto'
        )
    return state

def save_checkbox_state(newOptionsConfig: OptionsConfig):
    """
    Saves the checkbox state to the config file, preserving other sections. Now also saves GPS add checkbox and time offset.
    """
    config = configparser.ConfigParser()
    config_file = get_config_file_path()
    if os.path.exists(config_file):
        config.read(config_file)
    if 'options' not in config:
        config['options'] = {}
    config['options']['generate_data'] = str(newOptionsConfig.generate_data)
    config['options']['generate_stats'] = str(newOptionsConfig.generate_stats)
    config['options']['move_empty'] = str(newOptionsConfig.move_empty)
    config['options']['move_undefined'] = str(newOptionsConfig.move_undefined)
    config['options']['rename_files'] = str(newOptionsConfig.rename_files)
    config['options']['add_gps'] = str(newOptionsConfig.add_gps)
    config['options']['prediction_threshold'] = str(newOptionsConfig.prediction_threshold)
    config['options']['get_gps_from_each_file'] = str(newOptionsConfig.get_gps_from_each_file)
    config['options']['use_gps_only_for_data'] = str(newOptionsConfig.use_gps_only_for_data)
    config['options']['combine_with_data'] = str(newOptionsConfig.combine_with_data)
    config['options']['time_offset'] = str(newOptionsConfig.time_offset)
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
