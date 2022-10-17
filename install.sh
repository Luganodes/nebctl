#!/usr/bin/env bash

INSTALL_DIR=/opt/nebctl
REPO_URL=

# clone the repository
git clone $REPO_URL $INSTALL_DIR

# install nebula if not present already
if ! command -v nebula &> /dev/null; then
    wget -c "https://github.com/slackhq/nebula/releases/download/v1.6.1/nebula-linux-amd64.tar.gz" -O - | sudo tar -xz -C /usr/bin/
fi

# install python dependencies
pip install -r $INSTALL_DIR/requirements.txt

# create required directories
mkdir -p $INSTALL_DIR/{ca,hosts,store}

# change ownership of the install dir to current user
chown -R $USER:$USER $INSTALL_DIR

# give executable permissions
chmod +x $INSTALL_DIR/nebctl

# create symlink to script
ln -s $INSTALL_DIR/nebctl /usr/bin/nebctl

echo "Installation complete."
