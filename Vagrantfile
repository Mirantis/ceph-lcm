# -*- mode: ruby -*-
# vi: set ft=ruby :


VAGRANTFILE_API_VERSION = "2"


Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box            = "ubuntu/xenial64"
  config.vm.hostname       = "vsm"
  config.ssh.forward_agent = true

  config.vm.network "private_network", ip: "10.0.0.200"

  config.vm.synced_folder ".", "/vagrant", type: "nfs"

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
      type:          :nfs,
      mount_options: ['rw', 'vers=3', 'tcp', 'nolock']
    }
  else
    print "vagrant-cachier plugin has not been found."
    print "You can install it by `vagrant plugin install vagrant-cachier`"
  end

  config.vm.provider "virtualbox" do |vb|
    vb.gui    = false
    vb.memory = 3092
    vb.cpus   = 2
  end

  if Vagrant.has_plugin?("vagrant-host-shell")
    config.vm.provision :host_shell do |host_shell|
      host_shell.inline = "ansible-galaxy install -r devenv/requirements.yaml -p devenv/galaxy"
    end
  else
    abort "You have to install vagrant-host-shell plugin to continue"
  end

  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "devenv/main.yaml"
  end
end
