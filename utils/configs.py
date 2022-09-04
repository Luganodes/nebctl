import yaml

from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import engine
from .db.models import Host

CLIENT_CONFIG_PATH = "defaults/client.yml"
LIGHTHOUSE_CONFIG_PATH = "defaults/lighthouse.yml"

# load config yml
def load(path):
    with open(path, "r") as yf:
        config_yml = list(yaml.safe_load_all(yf))

    # assert successful load
    if not config_yml:
        raise Exception(f"Failed to load {path}")

    return config_yml[0]


# dump config yml
def dump(config, path):
    with open(path, "w") as yf:
        yaml.dump(config, yf, default_flow_style=False, sort_keys=False)


# generate client config by populating it with existing lighthouses
def generate_client_config(destination):
    with Session(engine) as session:
        config = load(CLIENT_CONFIG_PATH)
        lighthouses_query = select(Host).where(Host.is_lighthouse == True)
        lighthouses = session.scalars(lighthouses_query)

        if not config["static_host_map"]:
            config["static_host_map"] = dict()

        for lighthouse in lighthouses:
            config["static_host_map"][lighthouse.nebula_ip] = [
                f"{lighthouse.public_ip}:{lighthouse.nebula_port}"
            ]

        dump(config, destination)
