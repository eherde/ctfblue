#!/bin/bash -e

# the box already comes with sudo and aptitude
export DEBIAN_FRONTEND=noninteractive
aptitude update
aptitude upgrade --assume-yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold"

# install new packages
readonly PKGS=$(cat /vagrant/pkglist | grep -v "^#" | awk '{print $1}')
aptitude --assume-yes install ${PKGS}
aptitude --assume-yes install -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" mysql-server
