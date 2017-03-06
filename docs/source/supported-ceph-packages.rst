.. _supported_ceph_packages:


=======================
Supported Ceph packages
=======================

Mirantis provides its own Ceph packages with a set of patches that are
not included in the community yet but are crucial for customers and
internal needs. The supported LTS release of Ceph is Jewel_. And the
only supported distribution is 16.04 Xenial Xerus.

Mirantis keeps the patches as minimal and non-intrusive as possible
and tracks the community releases as close as reasonable. To publish
an urgent fix, intermediate releases can be issued. The packages are
available from the following APT repository

::

  deb http://mirror.fuel-infra.org/decapod/ceph/jewel-xenial jewel-xenial main

The following table lists packages provided for upgrades only:

.. list-table::
   :widths: 20 20 30
   :header-rows: 1

   * - Ceph release
     - Ubuntu release
     - APT repository
   * - Jewel
     - 14.04
     - ``deb http://mirror.fuel-infra.org/decapod/ceph/jewel-trusty jewel-trusty main``
   * - Hammer_ (0.94.x)
     - 14.04
     - ``deb http://mirror.fuel-infra.org/decapod/ceph/hammer-trusty hammer-trusty main``
   * - Hammer (0.94.x)
     - 12.04
     - ``deb http://mirror.fuel-infra.org/decapod/ceph/hammer-precise hammer-precise main``
   * - Firefly_
     - 14.04
     - ``deb http://mirror.fuel-infra.org/decapod/ceph/firefly-trusty firefly-trusty main``
   * - Firefly
     - 12.04
     - ``deb http://mirror.fuel-infra.org/decapod/ceph/firefly-precise firefly-precise main``

.. important::
   Packages for old LTS releases and Jewel for Ubuntu 14.04 are intended for
   upgrade purposes only and are *not* maintained other than fixing bugs
   hindering the upgrade to Jewel and Ubuntu 16.04.

.. note::

    It is possible and recommended to create and use your own
    repository. To do so, please check corresponding playbook and follow
    the instructions.

    https://github.com/Mirantis/ceph-lcm/tree/master/infrastructure_playbooks/apt_mirror_playbook

    This playbook creates only server, please setup webserver like nginx
    or caddy to serve static by yourself.

.. _Jewel: http://docs.ceph.com/docs/master/release-notes/#v10-2-0-jewel
.. _Hammer: http://docs.ceph.com/docs/master/release-notes/#v0-94-hammer
.. _Firefly: http://docs.ceph.com/docs/master/release-notes/#v0-80-firefly
