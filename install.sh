#!/usr/bin/env bash

INSTALL_DIR=/opt/nebula-control
REPO_URL=https://gitlab.com/lgns-platform-team/nebula-control.git

# clone the repository
git clone $REPO_URL $INSTALL_DIR

# create required directories
mkdir -p $INSTALL_DIR/{ca,hosts,store}

# change ownership of the install dir to current user
chown -R $USER:$USER $INSTALL_DIR

# create symlink to script
ln -s $INSTALL_DIR/nebula-control /usr/bin/nebula-control
