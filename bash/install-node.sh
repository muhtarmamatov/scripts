#! /bin/bash

set -e

# NODE_VERSIONS = (
#     [19.8.1]=
#     [18.10.0]=8.19.2
#     [17.9.1]=
#     [16.19.1]=
#     [14.21.3]=
#     [12.2.0]=
#     [11.12.0]=
#     [10.15.3]=
#     [8.15.1]=
# )

INSTALL_NODE_VERSION=10
INSTALL_NVM_VERSION=0.33.11
INSTALL_YARN_VERSION=1.7.0


echo "======================== ENTER NODE VERSION IF NOT WILL BE INSTALLED NODE v${INSTALL_NODE_VERSION} ==========================="

echo "==> specify node version as argument ex: ./install-node --version 11"



# pass specific version using --version <NODE_VERSION>
re='^[0-9]+$'
if [ "$1" == '--version' ]; then
    if ! [[ "$2" =~ $re ]]; then
        echo "==> version(second argument) should be number" >$2
        exit 1
    fi
    echo "==> Using specified node version - $2"
    INSTALL_NODE_VERSION=$2 
fi

echo "==> Ensuring .bashrc exists and is writable"
touch ~/.bashrc

echo "==> Installing node version manager (NVM). Version $INSTALL_NVM_VER"
# Removed if already installed
rm -rf ~/.nvm
# Unset exported variable
export NVM_DIR=

# Install nvm 
curl -o- https://raw.githubusercontent.com/creationix/nvm/v$INSTALL_NVM_VER/install.sh | bash
# Make nvm command available to terminal
source ~/.nvm/nvm.sh

echo "==> Installing node js version $INSTALL_NODE_VER"
nvm install $INSTALL_NODE_VER

echo "==> Make this version system default"
nvm alias default $INSTALL_NODE_VER
nvm use default

#echo -e "==> Update npm to latest version, if this stuck then terminate (CTRL+C) the execution"
#npm install -g npm

echo "==> Installing Yarn package manager"
rm -rf ~/.yarn
curl -o- -L https://yarnpkg.com/install.sh | bash -s -- --version $INSTALL_YARN_VER

echo "==> Adding Yarn to environment path"
# Yarn configurations
export PATH="$HOME/.yarn/bin:$PATH"
yarn config set prefix ~/.yarn -g

echo "==> Checking for versions"
nvm --version
node --version
npm --version
yarn --version

echo "==> Print binary paths"
which npm
which node
which yarn

echo "==> List installed node versions"
nvm ls

nvm cache clear
echo "==> Now you're all setup and ready for development. If changes are yet totake effect, I suggest you restart your computer"
