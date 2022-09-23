import os
import time

from ansible.vars.manager import VariableManager
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.executor.playbook_executor import PlaybookExecutor

from utils import settings, hosts, ip, configs

# method to generate configs for a node
def generate_node(args):
    NEBULA_CONTROL_DIR = os.environ.get("NEBULA_CONTROL_DIR")
    PLAYBOOK_SOURCE = [f"{NEBULA_CONTROL_DIR}/playbooks/generate-node.yml"]
    INVENTORY_SOURCE = [f"{NEBULA_CONTROL_DIR}/store/inventory"]

    # check if host with the given name already exists
    if hosts.get(args.name):
        raise Exception(f"A host named '{args.name}' already exists!")

    # get IP address for new node
    nebula_ip = ip.generate_nebula_IP(
        settings.get("nebula_network_ip"),
        settings.get("nebula_network_mask"),
    )

    # generate default node config assuming default nebula listener port (4242)
    node_config = f"/tmp/{args.name}{int(time.time())}.yml"
    configs.generate_client_config(4242, node_config)

    config = {
        "playbook": PLAYBOOK_SOURCE,
        "inventory": INVENTORY_SOURCE,
        "extra_vars": {
            "nebula_ip": nebula_ip,
            "node_name": args.name,
            "node_config": node_config,
            "groups": ",".join(args.groups),
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

    # run the playbook
    results = pbex.run()

    # get terminal dimensions for status display
    terminal_size = os.get_terminal_size()

    # add IP to list and print new node details if successful
    if results == 0:
        hosts.add_host(
            args.name,
            None,
            nebula_ip,
            groups=args.groups,
        )

        print("=" * terminal_size.columns)
        print("Node generated successfully!\n")
        print(f"Name:               {args.name}")
        print(f"Nebula IP:          {nebula_ip}\n")
        print(
            f"Distributable config zip stored at: {NEBULA_CONTROL_DIR}/hosts/{args.name}/config.zip"
        )
        print("=" * terminal_size.columns)
