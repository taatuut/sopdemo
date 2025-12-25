import os
import json
import yaml
import configparser
from pathlib import Path

class ConfigLoader:
    _instance = None  # Singleton instance
    
    def __new__(cls, config_file: str = None):
        """Implements Singleton pattern to ensure a single instance."""
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            cls._instance._config = {}
            if config_file:
                cls._instance.load(config_file)
        return cls._instance

    def load(self, config_file: str):
        """Loads configuration based on file extension."""
        config_path = Path(config_file)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config file '{config_file}' not found.")

        ext = config_path.suffix.lower()
        if ext == ".ini":
            self._load_ini(config_path)
        elif ext == ".json":
            self._load_json(config_path)
        elif ext in [".yaml", ".yml"]:
            self._load_yaml(config_path)
        else:
            raise ValueError("Unsupported config file format. Use .ini, .json, or .yaml")

    def _load_ini(self, path: Path):
        """Loads an INI configuration file."""
        config = configparser.ConfigParser()
        config.read(path)
        self._config = {section: dict(config.items(section)) for section in config.sections()}

    def _load_json(self, path: Path):
        """Loads a JSON configuration file."""
        with open(path, "r", encoding="utf-8") as file:
            self._config = json.load(file)

    def _load_yaml(self, path: Path):
        """Loads a YAML configuration file."""
        with open(path, "r", encoding="utf-8") as file:
            self._config = yaml.safe_load(file)

    def get(self, key: str, default=None):
        """Gets a configuration value by key, supporting nested keys using dot notation."""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def as_dict(self):
        """Returns the entire config as a dictionary."""
        return self._config

# Example usage:
# config = ConfigLoader("config.yaml")
# print(config.get("database.host"))

'''
1. Load a Configuration File

from ez_config_loader import ConfigLoader

config = ConfigLoader("config.yaml")  # Supports .ini, .json, .yaml
print(config.get("database.host"))

2. Access Nested Keys

db_host = config.get("database.host", "localhost")
print(db_host)

3. Retrieve Full Config as Dictionary

full_config = config.as_dict()
print(full_config)

Example 1: Using an .ini Configuration File
Step 1: Create an INI file (config.ini)

[database]
host = localhost
port = 5432
user = admin
password = secret

[app]
debug = true
log_level = info

Step 2: Use ConfigLoader to Read the INI File

from config_loader import ConfigLoader

# Load the configuration
config = ConfigLoader("config.ini")

# Access values
db_host = config.get("database.host")
db_port = config.get("database.port")
app_debug = config.get("app.debug")

print(f"Database Host: {db_host}")
print(f"Database Port: {db_port}")
print(f"App Debug Mode: {app_debug}")

Example 2: Using a .json Configuration File
Step 1: Create a JSON file (config.json)

{
    "database": {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "mypassword"
    },
    "app": {
        "debug": false,
        "log_level": "warning"
    }
}

Step 2: Use ConfigLoader to Read the JSON File

from config_loader import ConfigLoader

# Load the configuration
config = ConfigLoader("config.json")

# Access values
db_host = config.get("database.host")
db_port = config.get("database.port")
log_level = config.get("app.log_level")

print(f"Database Host: {db_host}")
print(f"Database Port: {db_port}")
print(f"Log Level: {log_level}")

'''