from tabulate import tabulate

from utils import hosts

# method to list all maintained nodes
def list_nodes(args):
    # retrieve all host details
    all_hosts = hosts.get_all()

    # tabulate host details
    table = [
        [
            host.name,
            host.nebula_ip,
            host.public_ip,
            "yes" if host.is_lighthouse else "no",
            ", ".join([group.name for group in hosts.get_groups(host.id)]),
        ]
        for host in all_hosts
    ]
    headers = ["Host", "Nebula IP", "Public IP", "Lighthouse", "Groups"]

    print(tabulate(table, headers, tablefmt="psql"))
