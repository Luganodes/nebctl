import os
import yaml

NEBULA_CONTROL_DIR = os.environ.get("NEBULA_CONTROL_DIR")
SETTINGS_YML_PATH = f"{NEBULA_CONTROL_DIR}/store/settings.yml"


# load settings yml
def load(path):
    with open(path, "r") as yf:
        settings_yml = list(yaml.safe_load_all(yf))

    # assert successful load
    if not settings_yml:
        raise Exception(f"Failed to load {path}")

    return settings_yml[0]


# dump settings yml
def dump(settings, path):
    with open(path, "w") as yf:
        yaml.dump(settings, yf, default_flow_style=False, sort_keys=False)


# get value from settings
def get(key):
    settings = load(SETTINGS_YML_PATH)
    return settings[key]


# set/update settings value
def set(key, value):
    settings = load(SETTINGS_YML_PATH)
    settings[key] = value
    dump(settings, SETTINGS_YML_PATH)
