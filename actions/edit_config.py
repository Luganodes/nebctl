import re
import os
import click

from ansible.vars.manager import VariableManager
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.executor.playbook_executor import PlaybookExecutor

from utils import hosts

# method to edit updated config files to the node
def edit_config(args):
    NEBULA_CONTROL_DIR = os.environ.get("NEBULA_CONTROL_DIR")
    PLAYBOOK_SOURCE = [f"{NEBULA_CONTROL_DIR}/playbooks/push-config.yml"]
    INVENTORY_SOURCE = [f"{NEBULA_CONTROL_DIR}/store/inventory"]

    # check if host with the given name exists
    target_host = hosts.get(args.name)
    if not target_host:
        raise Exception(f"A host named '{args.name}' does not exist!")

    # set config file path
    CONFIG_SOURCE = f"{NEBULA_CONTROL_DIR}/hosts/{args.name}/config.yml"

    # calculate line number of key in file
    LINE_NUMBER = 0
    with open(CONFIG_SOURCE, "r") as f:
        contents = f.read()
        for match in re.finditer(f"^{args.key}", contents, re.M):
            start = match.span()[0]
            LINE_NUMBER = contents[:start].count("\n") + 1
            break

    # spawn editor for making changes to config
    click.edit(
        filename=CONFIG_SOURCE,
        editor=f"$EDITOR +{LINE_NUMBER}",
    )

    config = {
        "playbook": PLAYBOOK_SOURCE,
        "inventory": INVENTORY_SOURCE,
        "extra_vars": {
            "public_ip": target_host.public_ip,
            "ssh_user": target_host.ssh_user,
            "ssh_port": target_host.ssh_port,
            "node_name": args.name,
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

    print("=" * terminal_size.columns)
    print("Node config edited successfully!")
    print("=" * terminal_size.columns)
