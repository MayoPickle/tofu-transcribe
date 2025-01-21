import os
import json

class ConfigLoader:
    """Class to handle configuration loading."""
    @staticmethod
    def load_config(config_file="config.json"):
        config_path = os.path.abspath(config_file)
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
