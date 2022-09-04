#! /usr/bin/env python3

import yaml

SETTINGS_YML_PATH = "store/settings.yml"


# load settings yml
def load():
    with open(SETTINGS_YML_PATH, "r") as yf:
        settings_yml = list(yaml.safe_load_all(yf))

    # assert successful load
    if not settings_yml:
        raise Exception(f"Failed to load {SETTINGS_YML_PATH}")

    return settings_yml[0]


# dump settings yml
def dump(settings):
    with open(SETTINGS_YML_PATH, "r") as yf:
        yaml.dump(settings, yf, default_flow_style=False)


# get value from settings
def get(key):
    settings = load()
    return settings[key]


# set/update settings value
def set(key, value):
    settings = load()
    settings[key] = value
    dump(settings)
