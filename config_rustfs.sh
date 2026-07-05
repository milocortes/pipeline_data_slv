#!/bin/bash
# 1.- Host Requirements
# Local path /mnt/rustfs/data (or custom path) for mounting object data
# Create data and logs 
sudo mkdir -p /mnt/rustfs/{data,logs}


# 2.- Network and Firewall
# Ensure host port 9000 is open to external access (or consistent with custom port)
sudo ufw allow 9000/tcp

# 3.- Configuration File Preparation
# Change the owner of these directories
sudo chown -R 10001:10001 /mnt/rustfs/{data,logs}
