Decapod
=======

|Build Status| |Code Coverage|

Decapod is intendend to simplify deployment and lifecycle management of
`Ceph <http://ceph.com>`_.

Using this tool, it is possible to deploy clusters with best known
practices, add new nodes to cluster, remove them and purge cluster
if not needed anymore. It provides simple API to manage cluster
configurations. Also, it is possible to use it web UI to manage your
clusters in several clicks.

Decapod uses `Ansible <https://www.ansible.com/>`_ with `ceph-ansible
<https://github.com/ceph/ceph-ansible>`_ community project to deliver
the best user experience. Every action is supported by plugins, which
encapsulate best practices and settings. If user do not like proviided
settings, it is always possible to customize configuration before
execution.


Demo
----

.. image:: http://img.youtube.com/vi/hvEyqutiwZs/sddefault.jpg
   :target: https://www.youtube.com/watch?v=hvEyqutiwZs

.. |Build Status| image:: https://travis-ci.org/Mirantis/ceph-lcm.svg?branch=master
    :target: https://travis-ci.org/Mirantis/ceph-lcm

.. |Code Coverage| image:: https://codecov.io/gh/Mirantis/ceph-lcm/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/Mirantis/ceph-lcm
