import os

from ansible.vars.manager import VariableManager
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.executor.playbook_executor import PlaybookExecutor

from utils import hosts, settings, callbacks


# method to push updated config files to the node
def push_config(args):
    NEBULA_CONTROL_DIR = os.environ.get("NEBULA_CONTROL_DIR")
    PLAYBOOK_SOURCE = [f"{NEBULA_CONTROL_DIR}/playbooks/push-config.yml"]
    INVENTORY_SOURCE = [f"{NEBULA_CONTROL_DIR}/store/inventory"]

    # append domain to input name
    node_name = args.name + "." + settings.get("domain")

    # check if host with the given name exists
    target_host = hosts.get(node_name)
    if not target_host:
        raise Exception(f"A host named '{node_name}' does not exist!")

    config = {
        "playbook": PLAYBOOK_SOURCE,
        "inventory": INVENTORY_SOURCE,
        "extra_vars": {
            "nebula_ip": target_host.nebula_ip,
            "ssh_user": target_host.ssh_user,
            "ssh_port": target_host.ssh_port,
            "node_name": node_name,
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

    # set callback
    progress = callbacks.ProgressCallback()
    pbex._tqm._stdout_callback = progress

    # run the playbook
    results = pbex.run()

    # print status
    if results != 0:
        progress.failure("Failed to sync node config!")
    else:
        progress.success("Successfully synced node config!")
