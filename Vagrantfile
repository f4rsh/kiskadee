# -*- mode: ruby -*-
# et ft=ruby :
#

# We conveniently get the VMs IP addresses from hosts.local ansible inventory
# in ./playbook/hosts.local

vms_inventory = "playbook/hosts.local"
ips = {}
File.open(vms_inventory, "r") do |f|
  f.each_line do |l|
    if ip = /core-host ansible_host=(.+)/.match(l)
      ips[:core] = ip[1]
    elsif ip = /frontend-host ansible_host=(.+)/.match(l)
      ips[:frontend] = ip[1]
    elsif ip = /ci-host ansible_host=(.+)/.match(l)
      ips[:ci] = ip[1]
    end
  end
end

if not ips.key?(:core) or not ips.key?(:frontend) or not ips.key?(:ci)
  abort("All IPs must be set in playbook/hosts.local")
end

Vagrant.configure(2) do |config|
  config.vm.define "kiskadee-core" do |core|
    core.vm.box = "fedora/27-cloud-base"
    # https://developer.fedoraproject.org/tools/vagrant/vagrant-nfs.html
    # After enable nfs-server, you will need to start the service.
    core.vm.synced_folder "./", "/home/vagrant/kiskadee", type: "nfs", nfs_udp: false
    core.vm.network "public_network", ip: ips[:core],
    :bridge => 'virbr0', :dev => 'virbr0'
    core.vm.network "forwarded_port", guest: 5000, host: 5000
    core.vm.provider "libvirt" do |v|
      v.memory = 2048
    end
  end

  config.vm.define "kiskadee-frontend" do |frontend|
    frontend.vm.box = "fedora/27-cloud-base"
    frontend.vm.network "private_network", ip: ips[:frontend]
  end

  config.vm.define "kiskadee-ci" do |ci|
    ci.vm.box = "fedora/27-cloud-base"
    ci.vm.network "private_network", ip: ips[:ci]
  end
end
