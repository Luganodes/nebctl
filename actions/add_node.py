import os
import time

from ansible.vars.manager import VariableManager
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.executor.playbook_executor import PlaybookExecutor

from utils import settings, hosts, ip, configs

# routine to add a client node
def add_node(args):
    NEBULA_CONTROL_DIR = os.environ.get("NEBULA_CONTROL_DIR")
    PLAYBOOK_SOURCE = [f"{NEBULA_CONTROL_DIR}/playbooks/add-node.yml"]
    ROLLBACK_SOURCE = [f"{NEBULA_CONTROL_DIR}/playbooks/add-node-rollback.yml"]
    INVENTORY_SOURCE = [f"{NEBULA_CONTROL_DIR}/store/inventory"]

    # get IP address for new node
    nebula_ip = ip.generate_nebula_IP(
        settings.get("nebula_network_ip"), settings.get("nebula_network_mask")
    )

    # generate default node config
    node_config = f"/tmp/{args.name}{int(time.time())}.yml"
    configs.generate_client_config(node_config)

    config = {
        "playbook": PLAYBOOK_SOURCE,
        "rollback": ROLLBACK_SOURCE,
        "inventory": INVENTORY_SOURCE,
        "extra_vars": {
            "public_ip": args.ip,
            "nebula_ip": nebula_ip,
            "ssh_user": args.ssh_user,
            "ssh_port": args.ssh_port,
            "node_name": args.name,
            "node_config": node_config,
            "ufw": args.ufw,
            "docker_ufw": args.docker_ufw,
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

    # rollback changes if error
    if results != 0:
        print("Error encountered. Rolling back changes...")
        rollback_pbex = PlaybookExecutor(
            playbooks=config["rollback"],
            inventory=inventory,
            variable_manager=variable_manager,
            loader=loader,
            passwords=passwords,
        )
        rollback_pbex.run()

    # add IP to list and print new node details if successful
    else:
        hosts.add_host(args.name, args.ip, nebula_ip)

        print("=" * 50)
        print("Node added successfully!\n")
        print(f"Name:               {args.name}")
        print(f"Public IP:          {args.ip}")
        print(f"Nebula IP:          {nebula_ip}")
        print(f"UFW Enabled:        {args.ufw}")
        print(f"Docker UFW Enabled: {args.docker_ufw}")
        print("=" * 50)
