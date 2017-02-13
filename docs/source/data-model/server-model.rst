.. _decapod_server:

============
Server model
============

The server model defines a server used for Ceph purposes. Servers are detected
during the server discovery process. Each server has a name (FQDN by default),
IP, FQDN, state, cluster ID, and facts. A user is only allowed to modify the
server name, other attributes are updated automatically on the server
discovery.
The facts property is a set of facts collected by Ansible and returned as is.
By default, Ansible collects only its own facts, ignoring Ohai and Facter.

.. note::

   We do not recommend that you manually create a new server using the API.
   Servers must be discovered by the discovery protocol.

Server discovery is an automatic process of discovering new servers in Decapod.
During this process, Decapod works passively.

.. important::

   A node operating system deployment is not in the scope of Decapod. The
   server discovery is performed using ``cloud-init``, so the only requirement
   for the node OS is to support ``cloud-init``.

The cloud-init package is required to create a user for Ansible, set the
deployment SSH public key for the user's authorized keys, and update the
``/etc/rc.local`` script. Then, the ``/etc/rc.local`` script registers the
host in Decapod.

.. seealso::

   * `Ohai <https://docs.chef.io/ohai.html>`_
   * `Facter <https://docs.puppet.com/facter>`_
   * `The cloud-init documentation <http://cloudinit.readthedocs.io/en/latest/index.html>`_
