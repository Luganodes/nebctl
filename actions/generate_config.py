import os
import time
import secrets

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
    nebula_ip = ""

    # append domain to input name
    node_name = args.name + "." + settings.get("domain")

    if not args.update_config:
        # check if host with the given name already exists
        if hosts.get(node_name):
            raise Exception(f"A host named '{node_name}' already exists!")

        # get IP address for new node
        nebula_ip = ip.generate_nebula_IP(
            settings.get("nebula_network_ip"),
            settings.get("nebula_network_mask"),
        )

    # generate default node config assuming default nebula listener port (4242)
    if not args.update_config:
        node_config = f"/tmp/{node_name}{int(time.time())}.yml"
        configs.generate_client_config(4242, node_config, args.no_admin)
        # generate random password
        password_length = 13
        archive_password = secrets.token_urlsafe(password_length)

    # choose updated config file
    if args.update_config:
        node_config = f"{NEBULA_CONTROL_DIR}/hosts/{node_name}/config.yml"
        # get password
        passwd_path = f"{NEBULA_CONTROL_DIR}/hosts/{node_name}/pwd"
        passwd_file = open(passwd_path, 'r')
        archive_password = passwd_file.read()

    # generate network config
    if args.mac_os:
        network_config = f"/tmp/nebula{int(time.time())}"
    else:
        network_config = f"/tmp/nebula1{int(time.time())}.network"

    configs.generate_network_config(network_config, node_config, args.mac_os)

    # generate pull_url
    pull_url = settings.get("pull_url")
    mod_url = pull_url.split("/")
    mod_url[-1] = node_name + ".zip"
    pull_url = "/".join(mod_url)

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
            "mac_os":args.mac_os,
            "archive_password":archive_password,
            "update_config":args.update_config,
            "pull_url":pull_url,
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
    elif not args.update_config:
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
        print(f"client password:    {archive_password}\n")
        print(
            f"Distributable config zip stored at: {NEBULA_CONTROL_DIR}/hosts/{node_name}/config.zip"
        )
