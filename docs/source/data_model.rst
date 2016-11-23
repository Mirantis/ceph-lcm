Data model
==========

Decapod is used to deploy and manage Ceph clusters. All management
functionality is distributed using plugins, called "playbooks". Each
playbook requires playbook configuration.

This document tries to describe Decapod user model in detail to
establish mental connection between different entities and terms used in
other documentation chapters.



User
++++

User is just an entity which presents common information about user. It
has login, email, password, full name and role. User model is used for
authentication/authorization purposes.

On creating of new user in Decapod, there is no way to set his password.
When new model is creating in system, Decapod will send new password
on his email. After that it is possible to reset that password and set
required one.

If user is created without a `Role`_, it can do bare minimum with
system: even listing of entities requires permissions. Authorization
is done assigning a role to the user. User may have only one role in
Decapod.


Role
++++

Role is entity, which has 2 properties: name and permissions. You may
consider role as a named set of permissions.

In Decapod, there are 2 types of permissions: api and playbook.

API permissions allow user to use different API endpoints and therefore
a set of actions available for usage. For example, if user wants to view
a list of user, she needs permission ``view_user``. If she wants to
modify some information about user, she needs ``edit_user`` permission.

.. note::

    Some API endpoints require several permissions. For example,
    mentioned user editing requires both ``view_user`` and ``edit_user``.

Playbook permissions works slightly different: they define a list of
playbooks which user can execute. For example, user with some role can
execute service playbooks for safe host package updates or adding of
new OSDs but it is strictly forbidden for her to execute destructive
playbooks like purging cluster or removing OSD hosts.



Cluster
+++++++

Cluster defines separate Ceph cluster. By default, it has a name and
it is possible to edit name only explicitly. It is possible to delete
cluster but only if it has no servers in it.

Explicit cluster model is required because it defines a name of FSID for
Ceph. By default name of the model is used as a name of the Ceph cluster
and its ID as FSID.

Cluster model has configuration. This configuration is a simple mapping
of roles to the list of servers. User cannot manage that configuration
explicitly, this is why playbooks exist. On execution of playbook for
adding new OSD host, this host will be added to the list of servers for
role "osds". If user removes Rados Gateways from the clusters using
appropriate playbook, these servers will be deleted from the list.



Server
++++++

Server model defines server which should be used for Ceph purposes.
Servers are found during server discovery process. Each server has a
name (FQDN by default), ip, fqdn, state, cluster_id and facts. User
only allowed to modify server name, other attributes are updated
automatically on server discovery.

Facts property are simple set of facts, collected by Ansible,
returned as is. By default Ansible collects only its own facts,
ignoring `ohai <https://docs.chef.io/ohai.html>`_ and `facter
<https://docs.puppet.com/facter/>`_.

.. note::

    Despite that facts that it is possible to manually create new
    server using API, it is recommended not to do so. Servers should be
    discovered by discovery protocol.


Server Discovery
----------------

Server discovery is an automatic process of discovering new servers in
Decapod. During this process, Decapod works passively. Server discovery
is done using cloud-init and this is the only requirement for the node
OS.

.. important::

    Node OS deployment is out of scope of Decapod. There is only one
    requirement for OS: it has to have cloud-init.

Server discovery is done using `cloud-init
<http://cloudinit.readthedocs.io/en/latest/index.html>`_. cloud-init is
required to create required user for Ansible, set deployment SSH public
key for her authorized keys and update ``/etc/rc.local`` file. After
that, execution of ``/etc/rc.local`` will execute script which register
host in Decapod.

Server discovery process is done in 6 steps:

1. User generates required user-data config for cloud-init. It
   can be done using CLI (TODO).
2. After that, user deploys her
   OS with that config. For example of such deployment, please
   check :ref:`deploy-os-using-maas`, `official documentation
   <http://cloudinit.readthedocs.io/en/latest/topics/datasources.html>`_
   or way to use `kernel parameter
   <https://github.com/number5/cloud-init/blob/master/doc/sources/kernel-cmdline.txt>`_.
3. On the execution of cloud-init, contents of ``/etc/rc.local``
   will be generated so first and next reboots will call Decapod API for
   server registering. Such registration is indempotent operation.
4. On execution of Decapod API (``POST /v1/server``) it create task for
   controller server on facts discovery.
5. Controller execute this task and collect facts from remote host.
6. After facts are collected new version (or update of existing one) will
   be performed.


Playbook Configuration
++++++++++++++++++++++

To define playbook configuration, we need to define playbook first.

Decapod uses plugins to deliver Ceph management functionality. Plugins
are just Python packages, which contain Ansible playbooks, configuration
file and Python code itself which is glue between playbook YAML file
and Decapod internals.

In most cases, Ansible playbooks are generic ones: they have abilities
to inject some values into them: not only hosts where playbook has to
be executed, but some arbitrary parameters also (e.g Ceph FSID). Those
parameters are injected into Ansible by ``--extra-vars`` commandline
option or by setting them in inventory.

Playbook configuration is a named set of such parameters for a playbook.
It defines tuple of (*name*, *playbook*, *parameters*).

For simplicity, each parameters are split into 2 sections:
``global_vars`` and ``inventory``.

``global_vars`` are variables which are global for playbook. Basically,
there is no need in them: all might be defined in inventory section.
But to avoid copypaste, they were moved into that section. Each
parameter in this section is defined for every host and if inventory
is not redefining it, it would be used. If inventory redefines, then
inventory's version would be used.

.. note::

    If you can image running of :program:`ansible-playbook`
    then ``global_vars`` will be passed as ``--extra-vars``
    parameter. Please `check official documentation on such injection
    <http://docs.ansible.com/ansible/playbooks_variables.html#passing-variables-on-the-command-line>`_.

``inventory`` will be used as Ansible inventory. In 99% of cases, this
would be real inventory. Sometimes it might differ to exclude sensitive
information like monitor secret from public view, but in most cases this
parameter will be used as is.

.. note::

    If you are familiar with :program:`ansible-playbook` program,
    then playbook configuration is equal to do following:

    1. Put contents of ``global_vars`` into ``./inventoryfile``
    2. Execute

    .. code-block:: bash

         $ ansible-playbook -i ./inventoryfile --extra-vars "inventory_section|to_json" playbook.yaml

Decapod will try to generate best possible configuration for given set
of `Server`_ models. After that you can modify it as you want.

.. note::

    Decapod will use `Server`_'s IP as hosts. Those IPs are IPs of
    machine visible by Decapod, they are not belonging to any other
    network other then that which is used by Decapod to SSH on those
    machines.


Execution
+++++++++

Execution model defines execution of `Playbook Configuration`_.

Each playbook configuration can be run various amount of time, and this
model defines a single execution. As a result, model has result of the
execution (completed, failed etc) and execution log.

Execution log can be present in 2 ways: execution steps and raw log. Raw
log is pure Ansible log of whole execution as is, taken from stdout.
Execution steps are parsed steps of the execution.

Each execution step has timestamps (started, finished), ID of the
`Server`_ which issued event, role and task name of the event, status of
the task and detailed information on error.
