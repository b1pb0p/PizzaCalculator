# config.py

import json
from pathlib import Path
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Default paths will be relative to the project root directory
DEFAULT_PATHS = {
    "json_recipes_path": "data/saved_pizza_recipes.json",  # Relative path to save pizza recipes
    "xlsx_yeast_table_path": "data/yeast.xlsx",  # Relative path to yeast table
    "save_icon": "icons/diskette.png",  # Relative path to save icon
    "load_icon": "icons/folder.png"  # Relative path to load icon
}

JSON_CONFIG_FILE_NAME_DEFAULT = "config.json"

DEFAULT_RECIPE = {
    "salt_percentage": 3,
    "oil_percentage": 1,
    "yeast_types": ["ADY", "IDY", "CY"],
    "hydration": 75,
    "ball_weight": 300,
    "num_balls": 3
}

DEFAULT_XLSX = {
    "temp_row_range_l": 5,
    "temp_row_range_r": 66,
    "temp_row_range_offset": 0,
    "room_temperature_row": 35,
    "fridge_temperature_row": 4,
    "room_time_default": 23,
    "fridge_time_default": 8,
    "start_hour_index": 3,
    "end_hour_index": 29
}


class Configuration:
    _data = None
    _json_config_full_path = Path(__file__).parent / JSON_CONFIG_FILE_NAME_DEFAULT

    @classmethod
    def initialize(cls):
        if cls._data is None:
            cls._data = cls.load_config()

    @classmethod
    def load_config(cls):
        if cls._json_config_full_path.exists() and cls._json_config_full_path.stat().st_size > 0:
            try:
                with open(cls._json_config_full_path, 'r') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                print("Error reading the JSON configuration file. Creating a new one with default values.")

        cls.create_default_config()
        return {**DEFAULT_PATHS, **DEFAULT_RECIPE, **DEFAULT_XLSX}

    @classmethod
    def create_default_config(cls):
        default_data = {**DEFAULT_PATHS, **DEFAULT_RECIPE, **DEFAULT_XLSX}
        try:
            with open(cls._json_config_full_path, 'w') as file:
                json.dump(default_data, file, indent=4)
            logging.info(f"Default configuration created at {cls._json_config_full_path}.")
        except IOError as e:
            logging.error(f"Failed to write configuration file: {e}")

    @staticmethod
    def get_recipe_defaults():
        if Configuration._data is None:
            Configuration.initialize()

        return {
            "salt_percentage": Configuration._data.get('salt_percentage', DEFAULT_RECIPE['salt_percentage']),
            "oil_percentage": Configuration._data.get('oil_percentage', DEFAULT_RECIPE['oil_percentage']),
            "yeast_types": Configuration._data.get('yeast_types', DEFAULT_RECIPE['yeast_types']),
            "hydration": Configuration._data.get('hydration', DEFAULT_RECIPE['hydration']),
            "ball_weight": Configuration._data.get('ball_weight', DEFAULT_RECIPE['ball_weight']),
            "num_balls": Configuration._data.get('num_balls', DEFAULT_RECIPE['num_balls'])
        }

    @staticmethod
    def get_yeast_table_params():
        if Configuration._data is None:
            Configuration.initialize()

        return {
            "temp_row_range_l": Configuration._data.get('temp_row_range_l', DEFAULT_XLSX['temp_row_range_l']),
            "temp_row_range_r": Configuration._data.get('temp_row_range_r', DEFAULT_XLSX['temp_row_range_r']),
            "temp_row_range_offset": Configuration._data.get('temp_row_range_offset',
                                                             DEFAULT_XLSX['temp_row_range_offset']),
            "room_temperature_row": Configuration._data.get('room_temperature_row',
                                                            DEFAULT_XLSX['room_temperature_row']),
            "fridge_temperature_row": Configuration._data.get('fridge_temperature_row',
                                                              DEFAULT_XLSX['fridge_temperature_row']),
            "room_time_default": Configuration._data.get('room_time_default',
                                                         DEFAULT_XLSX['room_time_default']),
            "fridge_time_default": Configuration._data.get('fridge_time_default',
                                                           DEFAULT_XLSX['fridge_time_default']),
            "start_hour_index": Configuration._data.get('start_hour_index',
                                                        DEFAULT_XLSX['start_hour_index']),
            "end_hour_index": Configuration._data.get('end_hour_index',
                                                      DEFAULT_XLSX['end_hour_index'])
        }

    @staticmethod
    def json_recipes_path():
        if Configuration._data is None:
            Configuration.initialize()
        return Path(Configuration._data['json_recipes_path']).resolve()

    @staticmethod
    def get_recipe_folder_path():
        if Configuration._data is None:
            Configuration.initialize()
        return Path(Configuration._data['json_recipes_path']).parent.resolve()

    @staticmethod
    def get_save_icon_path():
        if Configuration._data is None:
            Configuration.initialize()
        return Path(Configuration._data['save_icon']).resolve()

    @staticmethod
    def get_load_icon_path():
        if Configuration._data is None:
            Configuration.initialize()
        return Path(Configuration._data['load_icon']).resolve()

    @staticmethod
    def get_yeast_table_data():
        if Configuration._data is None:
            Configuration.initialize()
        try:
            yeast_data = pd.read_excel(Path(Configuration._data['xlsx_yeast_table_path']).resolve(), header=None)
            return yeast_data
        except Exception as e:
            print("Error loading yeast data:", e)
