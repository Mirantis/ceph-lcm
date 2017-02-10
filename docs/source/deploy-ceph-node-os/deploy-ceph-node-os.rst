.. _decapod_deploy_ceph_node_os:

=========================================
Deploy an operating system on a Ceph node
=========================================

.. warning::

   Decapod does not perform bare metal provisioning, OS deployment, and
   network setup. Perform these operations by external means.

The OS must support ``cloud-init``. Also, it must be possible to run your own
user data. For the available datasources for
``cloud-init``,
see `Datasources <http://cloudinit.readthedocs.io/en/latest/topics/datasources.html>`_.
Alternatively, you can set user data using the
`kernel command line <https://github.com/number5/cloud-init/blob/master/doc/sources/kernel-cmdline.txt>`_.
For bare metal provisioning, try MAAS. This section covers the MAAS
installation and OS deployment with this tool.

The section contains the following topics:

.. toctree::
   :maxdepth: 1

   generate-user-data-for-cloud-init.rst
   maas.rst
