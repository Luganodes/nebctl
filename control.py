#! /usr/bin/env python3

import os
import sys

from argparse import ArgumentParser

from ansible import context
from ansible.vars.manager import VariableManager
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.module_utils.common.collections import ImmutableDict

from utils.ip import get_new_IP

# function to get parameters and sources for target action
def get_config(args):
    if args.command == "add-node":
        PLAYBOOK_SOURCE = ["./playbooks/add-node.yml"]
        INVENTORY_SOURCE = ["./store/inventory"]

        nebula_ip = get_new_IP()

        return {
            "playbook": PLAYBOOK_SOURCE,
            "inventory": INVENTORY_SOURCE,
            "extra_vars": {
                "public_ip": args.ip,
                "nebula_ip": nebula_ip,
                "ssh_user": args.ssh_user,
                "ssh_port": args.ssh_port,
                "node_name": args.name,
                "ufw": args.ufw,
                "docker_ufw": args.docker_ufw,
            }
        }

    else:
        sys.exit(f"Unknown command: {command}")

if __name__ == "__main__":
    # parse arguments
    parser = ArgumentParser()
    subparser = parser.add_subparsers(dest="command")

    add_node = subparser.add_parser("add-node")
    add_node.add_argument("--ip", type=str, help="Public IP address of the client node to be added", required=True)
    add_node.add_argument("--name", type=str, help="Name of the client node", required=True)
    add_node.add_argument("--ssh-user", type=str, help="User account to SSH into on the client node", default="root")
    add_node.add_argument("--ssh-port", type=int, help="Port on which sshd is listening on the client node", default=22)
    add_node.add_argument("--ufw", type=bool, help="Set up firewall rules on the client node", default=True)
    add_node.add_argument("--docker-ufw", type=bool, help="Set up firewall rules for Docker containers on the client node", default=False)

    args = parser.parse_args()

    # get config for current action
    config = get_config(args)

    # default CLI args
    context.CLIARGS = ImmutableDict(tags={}, listtags=False, listtasks=False, listhosts=False, syntax=False, connection='smart',
                    module_path=None, forks=100, ssh_common_args=None, ssh_extra_args=None, sftp_extra_args=None, scp_extra_args=None, 
                    become=None, become_method=None, become_user=None, verbosity=True, check=False, start_at_task=None)

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
    pbex = PlaybookExecutor(playbooks=config["playbook"], inventory=inventory, variable_manager=variable_manager, loader=loader, passwords=passwords)

    # run the playbook
    results = pbex.run()
