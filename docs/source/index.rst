Welcome to Decapod's documentation!
===================================

Decapod is intendend to simplify deployment and lifecycle management of
`Ceph <http://ceph.com>`_.

Using this tool, it is possible to deploy clusters with best known
practices, add new nodes to cluster, remove them and purge cluster
if not needed anymore. It provides simple API to manage cluster
configurations. Also, it is possible to use it web UI to manage your
clusters in several clicks.

Decapod uses `Ansible <http://ansible.com>`_ with `ceph-ansible
<https://github.com/ceph/ceph-ansible>`_ community project to deliver
the best user experience. Every action is supported by plugins, which
encapsulate best practices and settings. If user do not like proviided
settings, it is always possible to customize configuration before
execution.



Contents
--------

.. toctree::
   :maxdepth: 1

   installation/index.rst
   deploy/index.rst
   data_model
   workflows
   cli
   ui/index.rst
   ceph_node
   playbook_plugins/index.rst
   api/index.rst



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

