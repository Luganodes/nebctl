<div align="center">
  <a href="">
    <img src="docs/nebctl.png" alt="nebctl" >
  </a>

  <p align="center">
	  A slick command-line utility to set up and manage your Nebula network
  </p>
</div>


<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#what-is-nebula">What is Nebula?</a></li>
    <li><a href="#why-nebctl">Why nebctl?</a></li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#dependencies">Dependencies</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>


## What is Nebula?

[Nebula](https://github.com/slackhq/nebula) is a scalable overlay networking tool with a focus on performance, simplicity and security. It lets you seamlessly connect computers anywhere in the world.

Nebula incorporates a number of existing concepts like encryption, security groups, certificates, and tunneling, and each of those individual pieces existed before Nebula in various forms. What makes Nebula different to existing offerings is that it brings all of these ideas together, resulting in a sum that is greater than its individual parts. 
 
Unlike other VPN solutions like Tailscale and ZeroTier, Nebula is **agentless**. It requires no daemon or background agent to listen for updates or configuration changes and propagate them.  

A Nebula network is decentralized and **fault-tolerant**. Due to the existence of multiple lighthouse nodes, it does not possess a single point of failure.  

Nebula also comes with a built-in firewall, making it easy to **secure** the network without needing to use other third-party software.


## Why nebctl?

![demo](docs/demo.gif)

`nebctl` was built to simplify the process of setting up and maintaining a Nebula network by automating most of the steps required. It aims to serve as a seamless, one-click solution for managing a Nebula network.

## Quick Start

To get nebctl up and running, follow these steps:

1. Fetch and run the install script<br>
```sh
$ sh -c "$(curl -sSfl https://raw.githubusercontent.com/Luganodes/nebctl/master/install.sh)"
```
> For macOS and Ubuntu/Debian based systems dependencies will be installed, for other systems, please ensure you have the following dependencies:
> git, python3, pip, wget, zip, unzip, ufw, git

2. Copy existing CA certificates, if any, to `~/.nebctl/ca`. Otherwise, create one.
```sh
$ cd ~/.nebctl/ca; nebula-cert ca -name "myOrganization" -duration 43834h
```

3. Create a lighthouse node
```sh
nebctl add myLighthouse0 --ip <public_ip> --lighthouse yes
```
> Ensure you have ssh access to the machine you are deploying to

4. Generate nebctl config for user client
```sh
nebctl generate myClient0 --groups users --no-admin yes
```
> Note down the password and send the user the config file along with the password <br>
> for nebctl 
to work, host an http server in the ~/.nebctl/archive folder

5. Import nebctl config on user client machine
```sh
nebctl import <hostname.zip> --password <password>
```
> make sure the file name is not changed before import

6. Add a server node to the Nebula network
```sh
nebctl add myServer0 --ip <public_ip> --groups servers
```
> Ensure you have ssh access to the machine you are deploying to

7. Access the server node over the Nebula network
```sh
ping myServer0.nebula
```

8. Edit the nebula config
```sh
nebctl edit myServer0 --key KEY 
```
> Edit nebula configs and then push them to a machine

## Usage

```sh
$ nebctl COMMAND [-h] [--options]
```
### Available commands

| Command               | Description                                                            |
|:---------------------:| ---------------------------------------------------------------------- |
| **`add`**               | Set up a new remotely managed node on the network.                     |        
| **`remove`**            | Remove a node from network.                                            |
| **`status`**            | Show all nodes managed by the application.                             |
| **`edit`**              | Edit configuration of a remotely managed node.                         |
| **`sync`**              | Sync local configuration changes with a remotely managed node.         |
| **`groups`**            | Manage groups that the target node belongs to.                         |
| **`generate`**          | Generate distributable configuration files for a new node.             |
| **`import`**            | Import configuration files and set up the current host as a node.      |
| **`pull`**              | Pull updated configs from a remote server.      			   |
| **`restart`**           | Restart nebula along with all services that it depends on.             |

### Command options and arguments
####  `add`
```sh
$ nebctl add [-h] --ip IP [--ssh-user SSH_USER] [--ssh-port SSH_PORT] 
             [--nebula-port NEBULA_PORT] [--lighthouse LIGHTHOUSE]
             [--ufw UFW] [--docker-ufw DOCKER_UFW] 
             [--groups GROUPS [GROUPS ...]] [--no-admin NO_ADMIN]
             name
```
- `name`: Name of the client node on this network
- `--ip`: Public IP address of the client node
- `--lighthouse`: Whether or not the target client is a lighthouse (default: no)
- `--ssh-user`: SSH user on the client node (default: root)
- `--ssh-port`: Port on which the client node's SSH server is listening (default: 22)
- `--nebula-port`: Port on which the client node's Nebula service listens (default: 4242)
- `--ufw`: Whether or not to add firewall rules on the client (default: yes)
- `--docker-ufw`: Whether or not the apply Docker + UFW [fix](https://github.com/chaifeng/ufw-docker) (default: no)
- `--groups`: Nebula groups to which this node belongs to (default: [])
- `--no-admin`: Deny admin access to system. (default: no)

**NOTE**: The host's SSH key needs to be added to the target client node's authorized_keys list before attempting to add it to the network remotely via the `add` command. In case this is not possible, use the `generate` command to obtain configs for the node and distribute it manually.

To set up the host machine as a Nebula node, make sure its SSH key also exists in authorized_keys and pass in "localhost" as the argument for `--ip`,

####  `remove`
```sh
$ nebctl remove [-h] name
```
- `name`: Name of the client node on this network

#### `edit`
```sh
$ nebctl edit [-h] [--key KEY] name
```
- `name`: Name of the client node on this network
- `--key`: Configuration option key at which the editor opens (default: none)

**NOTE**: Edit commands are executed on the client via its Nebula IP. This requires the host to also be connected to the Nebula network.

#### `sync`
```sh
$ nebctl sync [-h] name
```
- `name`: Name of the client node on this network

#### `groups`
```sh
$ nebctl groups [-h] [--add ADD [ADD ...]] [--remove REMOVE [REMOVE ...]] name
```
- `name`: Name of the client node on this network
- `--add`: Groups to add this node to (default: [])
- `--remove`: Groups to remove this node from (default: [])

#### `generate`
```sh
$ nebctl generate name [-h] [--groups GROUPS [GROUPS ...]] [--mac-os yes/no]
```
- `name`: Name of the client node on this network
- `--groups`: Nebula groups to which this node belongs to (default: [])
- `--no-admin`: Deny admin access to machine (Default: no)
- `--update_config`: generate .zip with changes made in existing config files instead of generating new configs (default: no)
- `--mac-os`: specify if the target machine is macOS or not
#### `import`
```sh
nebctl import [-h] config [--no-admin yes/no] [--update-config yes/no] [--mac-os yes/no]
```
- `config`: Path to the config.zip distributed by the admin
- `--password`: set/change password of your config
- `--mac-os`: specify if the target machine is macOS or not

#### `restart`
```sh
nebctl restart [-h] [--mac-os yes/no]
```
- `--mac-os`: specify if the target machine is macOS or not

#### `pull`
```sh
nebctl pull [-h] [--password PASSWORD] [--mac-os yes/no]
```
- `--password`: set/change password for archive

## Configuration
For editing the default domain name and IP segment, check `~/.nebctl/store/settings.yml`.  
For editing default firewall rules and node configuration options, check `~/.nebctl/defaults/client.yml` and `~/.nebctl/defaults/lighthouse.yml`.


## Roadmap
- [x] Remote node management
- [x] Implement generation of distributable configurations
- [ ] Update configurations of all existing nodes upon new lighthouse addition
- [ ] Interface to edit nebctl settings
- [ ] Better error handling and display

See [open issues](#) for a full list of proposed features (and known issues).


## License

Distributed under the MIT License. See `LICENSE.txt` for more information.
