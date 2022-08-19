#!/usr/bin/env bash

INSTALL_DIR=/opt/nebula-control
REPO_URL=https://gitlab.com/lgns-platform-team/nebula-control.git

git clone $REPO_URL $INSTALL_DIR
mkdir -p $INSTALL_DIR/{ca,hosts,store}
ln -s $INSTALL_DIR/nebula-control /usr/bin/nebula-control
