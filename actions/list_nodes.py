from tabulate import tabulate

from utils import hosts

# method to list all maintained nodes
def list_nodes(args):
    # retrieve all host details
    all_hosts = hosts.get_all()

    # tabulate host details
    table = [
        [host.name, host.nebula_ip, host.public_ip, "yes" if host.is_lighthouse else "no"]
        for host in all_hosts
    ]
    headers = ["Name", "Nebula IP", "Public IP", "Lighthouse"]

    print(tabulate(table, headers, tablefmt="psql"))
