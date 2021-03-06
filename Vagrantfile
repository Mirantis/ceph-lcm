# -*- mode: ruby -*-
# vi: set ft=ruby :
# Copyright (c) 2016 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


VAGRANTFILE_API_VERSION = "2"

CURRENT_DIR = File.expand_path(File.dirname(__FILE__))
CLOUD_CONFIG_USERNAME = "ansible"
CLOUD_CONFIG_URL = "10.0.0.10:9999"
CLOUD_CONFIG_KEY = File.join(
  CURRENT_DIR,
  "containerization", "files", "devconfigs", "ansible_ssh_keyfile.pub")
CLOUD_CONFIG_GEN = File.join(CURRENT_DIR, "devenv", "vagrant-cloud-config.py")
CLOUD_CONFIG_TOKEN = "26758c32-3421-4f3d-9603-e4b5337e7ecc"

cloud_config_file = ""
cloud_config_file = `#{CLOUD_CONFIG_GEN} #{CLOUD_CONFIG_USERNAME} #{CLOUD_CONFIG_URL} #{CLOUD_CONFIG_KEY} #{CLOUD_CONFIG_TOKEN}`
at_exit do
  File.delete cloud_config_file
end


Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box_check_update = false
  config.ssh.forward_agent   = true

  config.vm.define "devbox", primary: true do |devbox|
    devbox.vm.hostname = "decapod"
    devbox.vm.network "private_network", ip: "10.0.0.10"
    devbox.vm.synced_folder ".", "/vagrant",
      type:          "nfs",
      mount_options: ["rw", "vers=3", "noatime", "async"]

    devbox.vm.provider "virtualbox" do |vb, override|
      override.vm.box = "ubuntu/xenial64"

      vb.gui    = false
      vb.memory = 4096
      vb.cpus   = 3
    end

    devbox.vm.provider "libvirt" do |lv, override|
      override.vm.box = "yk0/ubuntu-xenial"

      lv.nested               = false
      lv.memory               = 4096
      lv.cpus                 = 3
      lv.cpu_mode             = "host-passthrough"
      lv.machine_virtual_size = 60
      lv.disk_bus             = "virtio"
      lv.nic_model_type       = "virtio"
    end

    if Vagrant.has_plugin?("vagrant-cachier")
      devbox.cache.scope = :box

      devbox.cache.enable :apt
      devbox.cache.enable :apt_lists
      devbox.cache.enable :npm

      devbox.cache.synced_folder_opts = {
        type: :nfs, mount_options: ['rw', 'vers=3', 'tcp', 'nolock']
      }
    else
      print "vagrant-cachier plugin has not been found."
      print "You can install it by `vagrant plugin install vagrant-cachier`"
    end

    devbox.vm.provision "ansible" do |ansible|
      ansible.playbook = "devenv/devbox.yaml"
    end
  end

  ["node01", "node02", "node03", "node04", "node05"].each_with_index do |host, idx|
    config.vm.define "#{host}", autostart: false do |client|
      client.vm.hostname = "ceph-#{host}"
      client.vm.network "private_network", ip: "10.0.0.2#{idx}"
      client.vm.synced_folder ".", "/vagrant", disabled: true

      # http://foo-o-rama.com/vagrant--stdin-is-not-a-tty--fix.html
      client.vm.provision "fix-no-tty", type: "shell" do |s|
        s.privileged = false
        s.inline     = "sudo sed -i '/tty/!s/mesg n/tty -s \\&\\& mesg n/' /root/.profile"
      end

      client.vm.provision "set-utc-timezone", type: "shell" do |s|
        s.privileged = true
        s.inline     = "ln -fs /usr/share/zoneinfo/UTC /etc/localtime && dpkg-reconfigure -f noninteractive tzdata"
      end

      # http://www.whiteboardcoder.com/2016/04/install-cloud-init-on-ubuntu-and-use.html
      # https://raymii.org/s/tutorials/Automating_Openstack_with_Cloud_init_run_a_script_on_VMs_first_boot.html
      client.vm.provision :ansible do |ansible|
        ansible.playbook = File.join(
          CURRENT_DIR, "infrastructure_playbooks", "server_discovery_playbook",
          "playbook.yaml"
        )
        ansible.extra_vars = {
          user_data: cloud_config_file,
          cloud_init: false
        }
      end

      client.vm.provider "virtualbox" do |vb, override|
        override.vm.box = "ubuntu/xenial64"

        vb.gui    = false
        vb.memory = 512
        vb.cpus   = 1

        (0..2).each do |d|
            disk_name = "#{host}-#{idx}-#{d}"
            vb.customize ["createhd",
                          "--filename", disk_name,
                          "--size", "5000"] unless File.exist?("#{disk_name}.vdi")
            vb.customize ["storageattach", :id,
                          '--storagectl', "SATAController",
                          "--port", 3 + d,
                          "--device", 0,
                          "--type", "hdd",
                          "--medium", "#{disk_name}.vdi"]
        end
      end

      client.vm.provider "libvirt" do |lv, override|
        override.vm.box = "yk0/ubuntu-xenial"

        lv.nested         = false
        lv.memory         = 512
        lv.cpus           = 1
        lv.cpu_mode       = "host-passthrough"
        lv.disk_bus       = "virtio"
        lv.nic_model_type = "virtio"

        5.times do
          lv.storage :file, :size => "5G"
          lv.storage :file, :size => "1G"
        end
      end
    end
  end
end
