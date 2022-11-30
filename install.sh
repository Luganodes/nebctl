#!/usr/bin/env bash

INSTALL_DIR=~/.nebctl
REPO_URL="https://github.com/Luganodes/nebctl"

# clone the repository
git clone $REPO_URL $INSTALL_DIR

# install nebula if not present already
if ! command -v nebula &> /dev/null; then
    sudo sh -c 'wget -c "https://github.com/slackhq/nebula/releases/download/v1.6.1/nebula-linux-amd64.tar.gz" -O - | sudo tar -xz -C /usr/local/bin/'
fi

# install dependencies
if [[ "$OSTYPE" == "darwin"* ]]; then
    brew install nebula wget unzip git
    pip3 install -r $INSTALL_DIR/requirements.txt
else
    sudo apt install python3-pip ufw wget unzip zip git
    pip install -r $INSTALL_DIR/requirements.txt
fi

# create required directories
mkdir -p $INSTALL_DIR/ca
mkdir -p $INSTALL_DIR/hosts

# change ownership of the install dir to current user
chown -R $USER:$USER $INSTALL_DIR

# give executable permissions
chmod +x $INSTALL_DIR/nebctl

# add env to export install directory to PATH variable
cat > $INSTALL_DIR/env <<EOF
#!/bin/sh
case ":\${PATH}:" in
    *:"$INSTALL_DIR":*)
        ;;
    *)
        # Prepending path in case a system installed binary must be overwritten
        export PATH="$INSTALL_DIR:\$PATH"
        ;;
esac
EOF
# add env to profile
if [[ "$OSTYPE" == "darwin"* ]]; then
    profile_path="~/.zprofile"
    cat >> ~/.zprofile <<EOF
    source "$INSTALL_DIR/env"
EOF
else
    profile_path="~/.profile"
    cat >> ~/.profile <<EOF
    source "$INSTALL_DIR/env"
EOF
fi

printf "\n\nInstallation complete.\nTo use nebctl, you need the install directory ($INSTALL_DIR) to be in your PATH variable. Next time you log in this will be done automatically. To access nebctl in the current shell, run 'source $profile_path' first.\n"
