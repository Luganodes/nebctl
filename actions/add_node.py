import os
import time

from ansible.vars.manager import VariableManager
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.executor.playbook_executor import PlaybookExecutor

from utils import settings, hosts, ip, configs, callbacks

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
        RESOLVED_STATE="stopped"
        RESOLVED_ENABLED="no"
        dnsmasq_config="/tmp/dnsmasq.config"
        configs.generate_dnsmasq_config(settings.get("domain"), nebula_ip, settings.get("nebula_dns_port"), dnsmasq_config)
    else:
        configs.generate_client_config(args.nebula_port, node_config)
        RESOLVED_STATE="restarted"
        RESOLVED_ENABLED="yes"

    # generate network config
    network_config = f"/tmp/nebula1{int(time.time())}.network"
    configs.generate_network_config(network_config, node_config, False)

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
            "resolved_state": RESOLVED_STATE,
            "resolved_enabled": RESOLVED_ENABLED,
            "dnsmasq_config": dnsmasq_config,
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
    #progress = callbacks.ProgressCallback()
    #pbex._tqm._stdout_callback = progress

    # run the playbook
    results = pbex.run()

    # print status
    if results != 0:
        #progress.warn("Error encountered. Rolling back changes...")
        rollback_pbex = PlaybookExecutor(
            playbooks=config["rollback"],
            inventory=inventory,
            variable_manager=variable_manager,
            loader=loader,
            passwords=passwords,
        )

        # set rollback progress callback
        rollback_progress = callbacks.ProgressCallback()
        rollback_pbex._tqm._stdout_callback = rollback_progress

        # # run rollback playbook
        rollback_pbex.run()

        #rollback_progress.failure("Failed to add node!")

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

        #progress.success("Successfully added node!")
        print(f"Host:               {node_name}")
        print(f"Public IP:          {args.ip}")
        print(f"Nebula IP:          {nebula_ip}")
        print(f"Lighthouse:         {args.lighthouse}")
        print(f"UFW Enabled:        {args.ufw}")
        print(f"Docker UFW Enabled: {args.docker_ufw}")
