Ceph Node OS deployment
=======================

.. warning::

    Baremetal provision and OS deployment is out of scope of this guide:
    Decapod does not do any OS deployment or network setup.

    This should be done by external means.

Decapod has only one requirement: OS has to execute
`cloud-init <http://cloudinit.readthedocs.io/en/latest/>`_
and it should be possible to run your own user-data.
Please check available datasources for cloud-init:
http://cloudinit.readthedocs.io/en/latest/topics/datasources.html

Also, it is possible to set user-data using kernel command line:
https://github.com/number5/cloud-init/blob/master/doc/sources/kernel-cmdline.txt

If you have no preferred choice for baremetal provision, we are
recommending to try `MAAS <http://maas.io>`_. In this guide we will
cover MAAS installation and OS deployment with this tool.



Generate user-data for cloud-init
---------------------------------

To generate user-data you need to have working Decapod installation
up and running. To do so, you need to have 2 prerequisites: server
discovery token and SSH public key.



Server discovery token
++++++++++++++++++++++

Decapod uses automatic server discovery (and cloud-init usage required
only for that). To access Decapod API, servers will access it using
authentication token with limited capabilities (basically, it can only
post to server discovery API endpoint).

Server discovery token is set in configuration file. Section for that is
*api.server_discovery_token*. Just grep for ``server_discovery`` token to
obtain it:

.. code-block:: bash

    $ grep server_discovery_token config.yaml
      server_discovery_token: "7f080dab-d803-4339-9c69-e647f7d6e200"

It is secret token so keep it private.



SSH public key
++++++++++++++

During execution of user-data, new user will be created. It will
have passwordless sudo access and should have public key in it’s
*authorized_keys*. This user is intended to be used only by ansible and
it’s default login is ``ansible`` (it is possible to redefine it).

To generate SSH public key from private one, do following:

.. code-block:: bash

    $ ssh-keygen -y -f ansible_ssh_keyfile.pem > ansible_ssh_keyfile.pem.pub

Please be noticed, that permissions on ``ansible_ssh_keyfile.pem``
should be **0600**. You may set such permissions with:

.. code-block:: bash

    $ chmod 0600 ansible_ssh_keyfile.pem



Generate user-data
++++++++++++++++++

Assuming steps above completed ok, execute following:

.. code-block:: bash

    $ decapod -u http://10.10.0.2:9999 cloud-config \
      7f080dab-d803-4339-9c69-e647f7d6e200 ansible_ssh_keyfile.pem.pub

URL has to be public URL of the Decapod machine with correct port.
Servers will send HTTP request for server discovery using this URL.

As a result, you will get YAML-like user-data. This user-data is going
to be used later.



MAAS
----

.. warning::

    Maas deployment is not part of this product. We hope that it will be
    useful to you, but can't guarantee its robustness. If you want to
    provision your ceph nodes manually then you can skip the next section.



Prerequisites
+++++++++++++

Please remember, that MAAS has it’s own DHCP server so to avoid
collisions, please disable default one.

If you are planning to run MAAS in virtual network with libvirt, please
create new network with *disabled DHCP*, but *enabled NAT*.



Install MAAS
************

Just follow these guides:

* https://maas.ubuntu.com/docs/install.html#installing-a-single-node-maas
* https://maas.ubuntu.com/docs/install.html#import-the-boot-images
* https://maas.ubuntu.com/docs/maascli.html#logging-in


Or you may want to check this series of screencasts:

* https://www.youtube.com/watch?v=ojTTgrtl-RU
* https://www.youtube.com/watch?v=GGpxpxFR7V0
* https://www.youtube.com/watch?v=Mp-QlQQ09ec
* https://www.youtube.com/watch?v=OoqQlzatnC4

We will assume that you have a CLI profile named ``mymaas``.



.. _deploy-os-using-maas:

Deploy OS using MAAS
********************

MAAS 2.0 has non backward compatible API changes so there are 2 ways to
deploy OS on your baremetal. Anyway, you need to give user-data to MAAS.
But to do that, you need to encode it to *base64* first:

.. code-block:: bash

    $ decapod -u http://10.10.0.2:9999 cloud-config \
      7f080dab-d803-4339-9c69-e647f7d6e200 ansible_ssh_keyfile.pem.pub \
      | base64 -w 0 > user_data.txt



MAAS 2.0
~~~~~~~~

First, please obtain ``system_id`` of machine you need to deploy. You can
get it from output of this command:

.. code-block:: bash

    $ maas mymaas nodes read

After you get it, deploy with

.. code-block:: bash

    $ maas mymaas machine deploy {system_id} user_data={base64-encoded of user-data}



MAAS < 2.0
~~~~~~~~~~

First, please obtain ``system_id`` of machine you need to deploy. You
can get it from output of this command:

.. code-block:: bash

    $ maas prof nodes list

After you get it, deploy with

.. code-block:: bash

    $ maas mymaas node start {system_id} user_data={base64-encoded of user-data} distro_series={distro series. Eg. trusty}
