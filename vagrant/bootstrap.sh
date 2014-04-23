#!/bin/bash -e

export DEBIAN_FRONTEND=noninteractive
readonly JOBS=$(($(nproc) * 2))
_system_update()
{
	# the box already comes with sudo and aptitude
	aptitude update
	aptitude upgrade --assume-yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold"
}

_fix_time()
{
	echo "America/Los_Angeles" > /etc/timezone
	dpkg-reconfigure -f noninteractive tzdata
}

_install_packages()
{
	local pkgs=$(cat /vagrant/pkglist | grep -v "^#" | awk '{print $1}')
	aptitude install --assume-yes ${pkgs}
	aptitude install --assume-yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" mysql-server
}

_install_git()
{
	local gitver=1.9.2
	local gitdir=/root/git.git
	apt-get build-dep --assume-yes git
	git clone https://github.com/git/git ${gitdir}
	cd ${gitdir} && git checkout v${gitver}
	make prefix=/usr/local install --directory ${gitdir} --jobs ${JOBS}
}

_install_kernel()
{
	local kver=3.12
	local kdir=/root/linux-${kver}
	apt-get build-dep --assume-yes linux
	aptitude install --assume-yes kernel-package
	cd /root && wget http://www.kernel.org/pub/linux/kernel/v3.0/linux-${kver}.tar.gz && tar --extract --file linux-${kver}.tar.gz
	cd ${kdir} && cp /vagrant/kernelconfig .config
	make oldconfig
	make --jobs ${JOBS}
	make-kpkg clean
	fakeroot make-kpkg -j$(($(nproc) * 2)) --initrd kernel_image kernel_headers
	dpkg --install ../linux-{image,headers}-${kver}.0_${kver}.0-10.00.Custom_amd64.deb
}

# comment out the actions you want to skip
_system_update # required
_fix_time # recommended
_install_packages # required
#_install_git # optional
#_install_kernel # optional
