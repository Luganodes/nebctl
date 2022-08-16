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
1. Clone the repository:
```
https://gitlab.com/lgns-platform-team/nebula-control.git
```

2. Copy existing CA certificates to `nebula-control/ca`, or create one:
```
cd nebula-control/ca; nebula-cert ca -name "<name>" -duration 43834h
```

3. Add existing ligthouse and client IPs to `nebula-control/hosts/ip_list.yml`.
```
[lighthouses|clients]:
    <nebula_ip>: <public_ip>:<port>
```

## Actions
### Add non-lighthouse client to network
```
Usage: ansible-playbook playbooks/add-node.yml -e "public_ip=<public_ip> ssh_user=<ssh_user> ssh_port=<ssh_port>  node_name=<node_name> ufw=[yes|no] docker_ufw=[yes|no]" -K
```
Options:
- `public_ip`: Public IP address of the client node
- `ssh_user`: SSH user on the client node
- `ssh_port`: Port on which client node's SSH server is listening (default: 22)
- `node_name`: Name of the client node
- `ufw`: Whether or not to add firewall rules on the client (default: yes)
- `docker_ufw`: Whether or not the host is using Docker to expose services (default: no)

## Future Work
- Add client node IPs to ansible inventory; maybe group them under different `clients` keys.
- Propagate configuration changes to all/relevant nodes.
- Add lighthouse node IPs and domains to client nodes' DNS resolvers.
