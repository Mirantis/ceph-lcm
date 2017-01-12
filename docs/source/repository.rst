Mirantis Ceph Repository
========================


Mirantis provides its own Ceph repository with a set of backported or
proposed patches which are not included in upstream, but crucial for
customers and internal needs.

Currently, supported versions are:

* `Hammer (v0.94 releases) <http://docs.ceph.com/docs/master/release-notes/#v0-94-hammer>`_
* `Firefly (v0.80 releases) <http://docs.ceph.com/docs/master/release-notes/#v0-80-firefly>`_
* `Jewel (v10.2 releases) <http://docs.ceph.com/docs/master/release-notes/#v10.2.0-jewel>`_

Current supported distros are:

* Ubuntu Precise Pangolin (12.04)
* Ubuntu Trusty Tahr (14.04)
* Ubuntu Xenial Xerus (16.04)

.. important::

  Not all releases of Ceph are available for all distributions. Please
  pay attention to the table.

Please find corresponding line for APT repository in the table below:

+--------------+----------------+----------------------------------------------------------------------------------------+
| Ceph Release | Ubuntu Release | APT repository                                                                         |
+==============+================+========================================================================================+
| Firefly      | 12.04          | ``deb http://mirror.fuel-infra.org/decapod/ceph/firefly-precise firefly-precise main`` |
+--------------+----------------+----------------------------------------------------------------------------------------+
| Firefly      | 14.04          | ``deb http://mirror.fuel-infra.org/decapod/ceph/firefly-trusty firefly-trusty main``   |
+--------------+----------------+----------------------------------------------------------------------------------------+
| Hammer       | 12.04          | ``deb http://mirror.fuel-infra.org/decapod/ceph/hammer-precise hammer-precise main``   |
+--------------+----------------+----------------------------------------------------------------------------------------+
| Hammer       | 14.04          | ``deb http://mirror.fuel-infra.org/decapod/ceph/hammer-trusty hammer-trusty main``     |
+--------------+----------------+----------------------------------------------------------------------------------------+
| Jewel        | 14.04          | ``deb http://mirror.fuel-infra.org/decapod/ceph/jewel-trusty jewel-trusty main``       |
+--------------+----------------+----------------------------------------------------------------------------------------+
| Jewel        | 16.04          | ``deb http://mirror.fuel-infra.org/decapod/ceph/jewel-xenial jewel-xenial main``       |
+--------------+----------------+----------------------------------------------------------------------------------------+

For example, if we want to add Jewel for Xenial, execute command below:

::

  echo 'deb http://mirror.fuel-infra.org/decapod/ceph/jewel-xenial jewel-xenial main' | sudo tee /etc/apt/sources.list.d/ceph.list

Similar commands will work for other repositories.
