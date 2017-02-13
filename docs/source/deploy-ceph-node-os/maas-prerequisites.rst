.. _maas_prerequisites:

=============
Prerequisites
=============

MAAS installation has the following requirements:

* MAAS has its own DHCP server. To avoid collisions, disable the default one.
* If you plan to run MAAS in a virtual network with libvirt, create a new
  network with disabled DHCP, but enabled NAT.
