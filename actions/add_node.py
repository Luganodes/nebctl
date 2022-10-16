import os
import time

from ansible.vars.manager import VariableManager
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.executor.playbook_executor import PlaybookExecutor

from utils import settings, hosts, ip, configs

# method to add a node
def add_node(args):
    NEBULA_CONTROL_DIR = os.environ.get("NEBULA_CONTROL_DIR")
    PLAYBOOK_SOURCE = [f"{NEBULA_CONTROL_DIR}/playbooks/add-node.yml"]
    ROLLBACK_SOURCE = [f"{NEBULA_CONTROL_DIR}/playbooks/remove-node.yml"]
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
        lighthouse=args.lighthouse,
    )

    # generate default node config
    node_config = f"/tmp/{node_name}{int(time.time())}.yml"
    if args.lighthouse:
        configs.generate_lighthouse_config(args.ip, nebula_ip, args.nebula_port, node_config)
    else:
        configs.generate_client_config(args.nebula_port, node_config)

    # generate network config
    network_config = f"/tmp/nebula1{int(time.time())}.network"
    configs.generate_network_config(network_config, node_config)

    config = {
        "playbook": PLAYBOOK_SOURCE,
        "rollback": ROLLBACK_SOURCE,
        "inventory": INVENTORY_SOURCE,
        "extra_vars": {
            "public_ip": args.ip,
            "nebula_ip": nebula_ip,
            "ssh_user": args.ssh_user,
            "ssh_port": args.ssh_port,
            "nebula_port": args.nebula_port,
            "lighthouse": args.lighthouse,
            "node_name": node_name,
            "node_config": node_config,
            "network_config": network_config,
            "ufw": args.ufw,
            "docker_ufw": args.docker_ufw,
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

    # run the playbook
    results = pbex.run()

    # get terminal dimensions for status display
    terminal_size = os.get_terminal_size()

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

        print("=" * terminal_size.columns)
        print("Failed to add node!")
        print("=" * terminal_size.columns)

    # add IP to list and print new node details if successful
    else:
        hosts.add_host(
            node_name,
            args.ip,
            nebula_ip,
            nebula_port=args.nebula_port,
            ssh_user=args.ssh_user,
            ssh_port=args.ssh_port,
            is_lighthouse=args.lighthouse,
            groups=args.groups,
        )

        print("=" * terminal_size.columns)
        print("Node added successfully!\n")
        print(f"Host:               {node_name}")
        print(f"Public IP:          {args.ip}")
        print(f"Nebula IP:          {nebula_ip}")
        print(f"Lighthouse:         {args.lighthouse}")
        print(f"UFW Enabled:        {args.ufw}")
        print(f"Docker UFW Enabled: {args.docker_ufw}")
        print("=" * terminal_size.columns)
