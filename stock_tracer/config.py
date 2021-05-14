"""
Simple module that reads a json file (and can be extended to merge json files)
and allow for easy dot-referencing from the `config` object
"""
from dotmap import DotMap
import json
import os

# Fetch environment variable detailing the path to the folder containing the config files
CONFIG_LOCATION = os.getenv("CONFIG_LOCATION")

if CONFIG_LOCATION is None:
    raise Exception("Please set environment variable `CONFIG_LOCATION`")

f = open(str(CONFIG_LOCATION) + "/config.json", "r")
data = json.load(f)
config = DotMap(**data)

if __name__ == "__main__":
    print(json.dumps(data, indent=2))
