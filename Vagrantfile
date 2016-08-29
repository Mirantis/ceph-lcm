# -*- mode: ruby -*-
# vi: set ft=ruby :


VAGRANTFILE_API_VERSION = "2"


Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box_check_update = false
  config.ssh.forward_agent   = true

  if Vagrant.has_plugin?("vagrant-cachier")
    config.cache.scope = :box

    config.cache.enable :apt
    config.cache.enable :apt_lists
    config.cache.enable :bower
    config.cache.enable :npm
    config.cache.enable :generic, {
      "pip" => { :cache_dir => ".cache/pip" },
      "ccache" => { :cache_dir => ".ccache"  }
    }
    config.cache.synced_folder_opts = {
      type: :nfs, mount_options: ['rw', 'vers=3', 'tcp', 'nolock']
    }
  else
    print "vagrant-cachier plugin has not been found."
    print "You can install it by `vagrant plugin install vagrant-cachier`"
  end

  config.vm.define "default", primary: true do |devbox|
    devbox.vm.box = "ubuntu/xenial64"
    devbox.vm.hostname = "cephlcm"
    devbox.vm.network "private_network", ip: "10.0.0.10"
    devbox.vm.synced_folder ".", "/vagrant", type: "nfs"

    devbox.vm.provider "virtualbox" do |vb|
      vb.gui = false
      vb.memory = 3092
      vb.cpus = 2
    end

    if Vagrant.has_plugin?("vagrant-host-shell")
      devbox.vm.provision :host_shell do |host_shell|
        host_shell.inline = "ansible-galaxy install -r devenv/requirements.yaml -p devenv/galaxy"
      end
    else
      abort "You have to install vagrant-host-shell plugin to continue"
    end

    devbox.vm.provision "ansible" do |ansible|
      ansible.playbook = "devenv/devbox.yaml"
    end
  end

  config.vm.define "mon", autostart: false do |mon|
    mon.vm.box = "ubuntu/trusty64"
    mon.vm.hostname = "ceph-mon"
    mon.vm.network "private_network", ip: "10.1.0.10"

    mon.vm.provider "virtualbox" do |vb|
      vb.gui = false
      vb.memory = 1024
      vb.cpus = 2
    end
  end

  config.vm.define "osd", autostart: false do |osd|
    osd.vm.box = "ubuntu/trusty64"
    osd.vm.hostname = "ceph-osd"
    osd.vm.network "private_network", ip: "10.1.0.11"

    osd.vm.provider "virtualbox" do |vb|
      vb.gui = false
      vb.memory = 1024
      vb.cpus = 2
    end
  end
end
