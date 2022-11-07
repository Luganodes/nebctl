import os
import time

from ansible.vars.manager import VariableManager
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.executor.playbook_executor import PlaybookExecutor

from utils import settings, hosts, ip, configs, callbacks

# method to generate configs for a node
def generate_config(args):
    NEBULA_CONTROL_DIR = os.environ.get("NEBULA_CONTROL_DIR")
    PLAYBOOK_SOURCE = [f"{NEBULA_CONTROL_DIR}/playbooks/generate-config.yml"]
    INVENTORY_SOURCE = [f"{NEBULA_CONTROL_DIR}/store/inventory"]

    # append domain to input name
    node_name = args.name + "." + settings.get("domain")

    # check if host with the given name already exists
    if hosts.get(node_name):
        raise Exception(f"A host named '{node_name}' already exists!")

    # get IP address for new node
    nebula_ip = ip.generate_nebula_IP(
        settings.get("nebula_network_ip"),
        settings.get("nebula_network_mask"),
    )

    # generate default node config assuming default nebula listener port (4242)
    node_config = f"/tmp/{node_name}{int(time.time())}.yml"
    configs.generate_client_config(4242, node_config)

    # generate network config
    network_config = f"/tmp/nebula1{int(time.time())}.network"
    configs.generate_network_config(network_config, node_config)

    config = {
        "playbook": PLAYBOOK_SOURCE,
        "inventory": INVENTORY_SOURCE,
        "extra_vars": {
            "nebula_ip": nebula_ip,
            "node_name": node_name,
            "node_config": node_config,
            "network_config": network_config,
            "nebula_groups": ",".join(args.groups),
            "nebula_control_dir": NEBULA_CONTROL_DIR,
        },
    }

    # initialize dataloader
    loader = DataLoader()

    # initialize inventory
    inventory = InventoryManager(loader=loader, sources=config["inventory"])

    # initialize variable manager
    variable_manager = VariableManager(loader=loader, inventory=inventory)

    # extra runtime variables
    variable_manager._extra_vars = config["extra_vars"]

    # initialize passwords
    passwords = {}

    # initialize playbook executor
    pbex = PlaybookExecutor(
        playbooks=config["playbook"],
        inventory=inventory,
        variable_manager=variable_manager,
        loader=loader,
        passwords=passwords,
    )

    # set progress callback
    # progress = callbacks.ProgressCallback()
    # pbex._tqm._stdout_callback = progress

    # run the playbook
    results = pbex.run()

    # print status
    if results != 0:
        # progress.failure("Failed to generate node config!")
        print("Failed to generate node config!")
    else:
        # add host to database
        hosts.add_host(
            node_name,
            None,
            nebula_ip,
            groups=args.groups,
        )

        # progress.success("Successfully generated node config!")
        print("Successfully generated node config!")
        print(f"Name:               {node_name}")
        print(f"Nebula IP:          {nebula_ip}\n")
        print(
            f"Distributable config zip stored at: {NEBULA_CONTROL_DIR}/hosts/{node_name}/config.zip"
        )
