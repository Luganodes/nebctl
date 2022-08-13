# Nebula Setup

## Desired config

### Mgmt

10.121.0.1 lighthouse1.lgns
10.121.0.2 lighthouse2.lgns
10.121.0.11 sns-laptop1.lgns

### Nodes

10.121.1.11 monvm1.lgns (142.93.42.62)
10.121.1.12 polygon-node1.lgns (51.91.80.190)
10.121.1.13 tron-mainnet-node2.lgns (51.210.209.208)

## Steps

1. Install nebula and create folders
```bash
sudo pacman -Sy nebula
mkdir -p nebula/hosts nebula/ca nebula/templates
```

2. Create CA certificate (Valid for 5 years)
```bash
cd nebula/ca
nebula-cert ca -name "Luganodes" -duration 43834h
```

3. Download template 
```bash
cd nebula/templates
wget https://raw.githubusercontent.com/slackhq/nebula/master/examples/config.yml
```

4. Sign certificates for lighthouse1
```bash
mkdir nebula/hosts/lighthouse1; cd nebula/hosts/lighthouse1
nebula-cert sign -out-crt host.crt -out-key host.key -ca-key ../../ca/ca.key --ca-crt ../../ca/ca.crt -name "lighthouse1.lgns" -ip "10.121.0.1/16"
```

5. Create lighthouse1 config `nano nebula/hosts/lighthouse1/config.yml`
```yaml
pki:
  ca: /etc/nebula/ca.crt
  cert: /etc/nebula/host.crt
  key: /etc/nebula/host.key

static_host_map:
  "10.121.0.1": ["178.62.120.83:4242"]
  "10.121.0.2": ["164.92.148.83:4242"]

lighthouse:
  am_lighthouse: true
  serve_dns: true
  dns:
    host: 10.121.0.1
    port: 5353
  interval: 60

listen:
  host: 0.0.0.0
  port: 4242

punchy:
  punch: true
  respond: true

relay:
  am_relay: true
  use_relays: true

tun:
  disabled: false
  dev: nebula1
  drop_multicast: false
  tx_queue: 500
  mtu: 1300

firewall:
  conntrack:
    tcp_timeout: 12m
    udp_timeout: 3m
    default_timeout: 10m

  outbound:
    - port: any
      proto: any
      host: any
  inbound:
    - port: any
      proto: icmp
      host: any
    - port: 5353
      proto: any
      host: any
    - port: any
      proto: any
      group: admin
```

6. Sign certificates for laptop
```bash
mkdir nebula/hosts/sns-laptop1.lgns; cd nebula/hosts/sns-laptop1.lgns
nebula-cert sign -ca-key ../../ca/ca.key --ca-crt ../../ca/ca.crt -out-key host.key -out-crt host.crt -name "sns-laptop1.lgns" -ip "10.121.0.11/16" -groups "admin"
```

7. Create lighthouse1 config `nano nebula/hosts/sns-laptop1/config.yml`
```yaml
pki:
  ca: /etc/nebula/ca.crt
  cert: /etc/nebula/host.crt
  key: /etc/nebula/host.key

static_host_map:
  "10.121.0.1": ["178.62.120.83:4242"]
  "10.121.0.2": ["164.92.148.83:4242"]

lighthouse:
  am_lighthouse: false
  interval: 60
  hosts:
    - "10.121.0.1"
    - "10.121.0.2"

listen:
  host: 0.0.0.0
  port: 0 # recommended for roaming clients like laptop

punchy:
  punch: true
  respond: true

relay:
  am_relay: false
  use_relays: true

tun:
  disabled: false
  dev: nebula1
  drop_local_broadcast: false
  drop_multicast: false
  tx_queue: 500
  mtu: 1300

firewall:
  conntrack:
    tcp_timeout: 12m
    udp_timeout: 3m
    default_timeout: 10m
  outbound:
    - port: any
      proto: any
      host: any
  inbound:
    - port: any
      proto: icmp
      host: any
    - port: any
      proto: any
      group: admin
```

8. Sign certificates for monvm1
```bash
mkdir nebula/hosts/tron-mainnet-node2; cd nebula/hosts/tron-mainnet-node2
nebula-cert sign -ca-key ../../ca/ca.key --ca-crt ../../ca/ca.crt -out-key host.key -out-crt host.crt -name "tron-mainnet-node2.lgns" -ip "10.121.1.13/16" -groups "tron,node"
```

9. Create monvm1 config `nano config.yml`
```yaml
=pki:
  ca: /etc/nebula/ca.crt
  cert: /etc/nebula/host.crt
  key: /etc/nebula/host.key=

static_host_map:
  "10.121.0.1": ["178.62.120.83:4242"]
  "10.121.0.2": ["164.92.148.83:4242"]

lighthouse:
  am_lighthouse: false
  interval: 60
  hosts:
    - "10.121.0.1"
    - "10.121.0.2"
    
listen:
  host: 0.0.0.0
  port: 4242

punchy:
  punch: true
  respond: true

relay:
  am_relay: false
  use_relays: true

tun:
  disabled: false
  dev: nebula1
  drop_local_broadcast: false
  drop_multicast: false
  tx_queue: 500
  mtu: 1300

firewall:
  conntrack:
    tcp_timeout: 12m
    udp_timeout: 3m
    default_timeout: 10m
  outbound:
    - port: any
      proto: any
      host: any
  inbound:
    - port: any
      proto: icmp
      host: any
    - port: any
      proto: any
      group: admin
```

10. Copy files to remote
```bash
rsync -aWz . root@51.210.209.208:/etc/nebula
rsync -aWz ../../ca/ca.crt root@51.210.209.208:/etc/nebula
```

11. Install nebula on remote hosts
```bash
wget -c "https://github.com/slackhq/nebula/releases/download/v1.6.0/nebula-linux-amd64.tar.gz" -O - | sudo tar -xz -C /usr/bin/
```

12. Setup service `sudo nano /etc/systemd/system/nebula.service`
```bash
[Unit]
Description=nebula
Wants=basic.target
After=basic.target network.target
Before=sshd.service

[Service]
SyslogIdentifier=nebula
ExecReload=/bin/kill -HUP $MAINPID
ExecStart=/usr/bin/nebula -config /etc/nebula/config.yml
Restart=always

[Install]
WantedBy=multi-user.target
```

13. In case the host is using docker to run and expose services, add `sudo nano /etc/ufw/after.rules`
```bash
# BEGIN UFW AND DOCKER
*filter
:ufw-user-forward - [0:0]
:ufw-docker-logging-deny - [0:0]
:DOCKER-USER - [0:0]
-A DOCKER-USER -j ufw-user-forward

-A DOCKER-USER -j RETURN -s 10.0.0.0/8
-A DOCKER-USER -j RETURN -s 172.16.0.0/12
-A DOCKER-USER -j RETURN -s 192.168.0.0/16

-A DOCKER-USER -p udp -m udp --sport 53 --dport 1024:65535 -j RETURN

-A DOCKER-USER -j ufw-docker-logging-deny -p tcp -m tcp --tcp-flags FIN,SYN,RST,ACK SYN -d 192.168.0.0/16
-A DOCKER-USER -j ufw-docker-logging-deny -p tcp -m tcp --tcp-flags FIN,SYN,RST,ACK SYN -d 10.0.0.0/8
-A DOCKER-USER -j ufw-docker-logging-deny -p tcp -m tcp --tcp-flags FIN,SYN,RST,ACK SYN -d 172.16.0.0/12
-A DOCKER-USER -j ufw-docker-logging-deny -p udp -m udp --dport 0:32767 -d 192.168.0.0/16
-A DOCKER-USER -j ufw-docker-logging-deny -p udp -m udp --dport 0:32767 -d 10.0.0.0/8
-A DOCKER-USER -j ufw-docker-logging-deny -p udp -m udp --dport 0:32767 -d 172.16.0.0/12

-A DOCKER-USER -j RETURN

-A ufw-docker-logging-deny -m limit --limit 3/min --limit-burst 10 -j LOG --log-prefix "[UFW DOCKER BLOCK] "
-A ufw-docker-logging-deny -j DROP

COMMIT
# END UFW AND DOCKER
```

14. Setup ufw and reload if already running
```bash
sudo ufw allow 4242/udp
sudo ufw allow 22/tcp
sudo ufw allow in on nebula1
sudo systemctl enable ufw
sudo ufw enable; sudo ufw reload
```

15. Start and enable services
```bash
sudo systemctl enable --now nebula
```

16. Update dns to support lgns domains `sudo nano /etc/systemd/resolved.conf`
```bash
DNS=10.121.0.1:5353 10.121.0.2:5353
Domains=~lgns
```

17. Reload DNS config
```bash
sudo systemctl restart systemd-resolved
```

---

## Reloading config

1. Edit configuration

2. Copy folder to remote
```bash
rsync -aWz ./ root@178.62.120.83:/etc/nebula/
```

3. Restart nebula in remote
```bash
sudo pkill nebula
```