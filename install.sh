#!/usr/bin/env bash

INSTALL_DIR=/opt/nebulactl
REPO_URL=

# clone the repository
git clone $REPO_URL $INSTALL_DIR

# install dependencies
pip install -r $INSTALL_DIR/requirements.txt

# create required directories
mkdir -p $INSTALL_DIR/{ca,hosts,store}

# change ownership of the install dir to current user
chown -R $USER:$USER $INSTALL_DIR

# give executable permissions
chmod +x $INSTALL_DIR/nebulactl

# create symlink to script
ln -s $INSTALL_DIR/nebulactl /usr/bin/nebulactl

echo "Installation complete."
