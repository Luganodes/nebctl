import os
import wget

from ansible.vars.manager import VariableManager
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.executor.playbook_executor import PlaybookExecutor

from utils import callbacks, settings

# method to import node configs
def import_config(args, pull):
    NEBULA_CONTROL_DIR = os.environ.get("NEBULA_CONTROL_DIR")
    if args.mac_os:
        PLAYBOOK_SOURCE = [f"{NEBULA_CONTROL_DIR}/playbooks/mac-import-config.yml"]
    else:
        PLAYBOOK_SOURCE = [f"{NEBULA_CONTROL_DIR}/playbooks/import-config.yml"]
    INVENTORY_SOURCE = [f"{NEBULA_CONTROL_DIR}/store/inventory"]

    # Pull configs from online source if specified
    if pull:
        wget.download(settings.get("pull_url"), "/tmp")
        NODE_CONFIG="/tmp/config.zip"
    else:
        NODE_CONFIG=args.config
        
    # save password
    if args.password != "":
        settings.set("archive_password", args.password)

    # set domain
    hostname = args.config.split("/")[-1].rstrip(".zip")
    domain = ".".join(hostname.split(".")[1:])
    settings.set("domain", domain)
    config = {
        "playbook": PLAYBOOK_SOURCE,
        "inventory": INVENTORY_SOURCE,
        "extra_vars": {
            "node_config": os.path.abspath(NODE_CONFIG),
            "nebula_control_dir": NEBULA_CONTROL_DIR,
            "archive_password": settings.get("archive_password"),
            "domain":settings.get("domain")
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
        # set pull URL
        url_path = f"/etc/nebula/pull_url"
        url_file = open(url_path, 'r')
        settings.set("pull_url", url_file.read())
        url_file.close()
        
        # progress.success("Successfully imported node config!")
        print("Successfully imported node config!")
        
