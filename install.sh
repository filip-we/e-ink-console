#!/bin/bash

echo "This script will setup e-ink-console on your Linux machine!"

git submodule init
git submodule update

cargo --version > /dev/null
# Install cargo
if [ $? -eq 127 ]; then
    echo "You need Cargo to compile the drivers. Trying to install Cargo..."
    curl https://sh.rustup.rs -sSf | sh
    echo "Installing base-devel to get compiler-stuff..."
    sudo pacman -Syu base-devel
else
    echo "Cargo is installed!"
fi

echo "Compiling screen drivers..."
cd rust-it8951
cargo build --example cli
cd ..

echo "Creating Python virtual environment..."
python -m venv .venv
source .venv/bin/activate
echo "Installing Ppython requirements..."
pip install -r requirements.txt

echo "Createing systemd-service-file..."
CURRENT_DIR=`pwd`

cat <<EOF > e-ink-console.service
[Unit]
Description=E-Ink Console

[Service]
Type=notify
NotifyAccess=all
ExecStart=${CURRENT_DIR}/.venv/bin/python -m e_ink_console --terminal-nr 1
Environment=PYTHONUNBUFFERED=true PYTHONPATH=${CURRENT_DIR}

[Install]
WantedBy=getty.target
EOF


echo "Installing systemd-service file - this needs root privileges!"
sudo cp e-ink-console.service /usr/lib/systemd/system/e-ink-console.service
sudo systemctl daemon-reload
sudo systemctl enable e-ink-console.service

echo "e-ink-console successfully installed! Start the service with 'sudo systemctl start e-ink-console.service'!"
