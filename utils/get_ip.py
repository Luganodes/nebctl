#! /usr/bin/env python3

"""
script to generate the next valid IP address

depends on:
  - pyyaml
  - ipaddress
"""

import os
import yaml
import ipaddress

IP_YML_PATH = os.path.expanduser("~/nebula/hosts/ip_list.yml")

# load used IP YML
def load_IP_yml(ip_yml_path):
    ip_yml = None
    with open(ip_yml_path, "r") as yf:
        ip_yml = list(yaml.safe_load_all(yf))

    # assert successful load
    if not ip_yml:
        raise Exception("Failed to load IP YML")

    return ip_yml[0]


# sort list of IPs and return the latest one
def fetch_latest_IP(ip_list):
    sorted_ips = sorted(ip_list, key=ipaddress.IPv4Address)
    return sorted_ips[-1]


# increment given IP (+ CIDR subnet mask) by 1
def increment_IP(ip):
    return ipaddress.IPv4Address(ip) + 1


if __name__ == "__main__":
    ip_yml = load_IP_yml(IP_YML_PATH)
    
    if not ip_yml["clients"]:
        new_IP = "10.121.1.11"  # default initial IP
    else:
        latest_IP = fetch_latest_IP(list(ip_yml["clients"].keys()))
        new_IP = increment_IP(latest_IP)

    print(new_IP, end="")  # send generated IP to stdout
