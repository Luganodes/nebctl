import os

from ansible.vars.manager import VariableManager
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.executor.playbook_executor import PlaybookExecutor

from utils import callbacks

# method to import node configs
def import_config(args):
    NEBULA_CONTROL_DIR = os.environ.get("NEBULA_CONTROL_DIR")
    PLAYBOOK_SOURCE = [f"{NEBULA_CONTROL_DIR}/playbooks/import-config.yml"]
    INVENTORY_SOURCE = [f"{NEBULA_CONTROL_DIR}/store/inventory"]

    config = {
        "playbook": PLAYBOOK_SOURCE,
        "inventory": INVENTORY_SOURCE,
        "extra_vars": {
            "node_config": os.path.abspath(args.config),
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
        # progress.failure("Failed to import node config!")
        print("Failed to import node config!")
    else:
        # progress.success("Successfully imported node config!")
        print("Successfully imported node config!")
