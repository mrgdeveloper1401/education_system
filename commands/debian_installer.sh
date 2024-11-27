#!/usr/bin/env bash

sudo apt update -y
sudo apt upgrade -y
sudo apt install -y --reinstall make
sudo apt install -y curl

sudo apt install git

curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo groupadd docker
sudo usermod -aG docker $USER
sudo systemctl enable docker.service
sudo systemctl enable containerd.service
sudo systemctl restart network-manager
sudo systemctl restart docker