# Nebula Controls

## Dependencies
(host)
- yq
- nebula
- ansible

(clients)
- sshd, with host key added to authorized list
- ufw
- sed
- wget
- tar

## Installation
1. Get and run and install script:
```
sh -c "$(curl -sSfl https://gitlab.com/lgns-platform-team/nebula-control/-/raw/main/install.sh)"
```

2. Copy existing CA certificates, if any, to `/opt/nebula-control/ca`. Otherwise, create one:
```
cd /opt/nebula-control/ca; nebula-cert ca -name "<name>" -duration 43834h
```

3. Add existing lighthouse and client IPs, if any, to `/opt/]nebula-control/hosts/ip_list.yml`.
```
[lighthouses|clients]:
    <nebula_ip>: <public_ip>:<port>
```

## Commands
### Add a client to network
```
Usage: nebula-control add-node --ip <public_ip> --name <node_name> 
```
Options:
- `--ip`: Public IP address of the client node (required)
- `--name`: Name of the client node (required)
- `--ssh-user`: SSH user on the client node (default: root)
- `--ssh-port`: Port on which client node's SSH server is listening (default: 22)
- `--ufw`: Whether or not to add firewall rules on the client (default: yes)
- `--docker-ufw`: Whether or not the host is using Docker to expose services (default: no)

## Future Work
- Add client node IPs to ansible inventory; maybe group them under different `clients` keys.
- Propagate configuration changes to all/relevant nodes.
- Add lighthouse node IPs and domains to client nodes' DNS resolvers.
