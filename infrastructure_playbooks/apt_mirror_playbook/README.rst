Create a local mirror of Mirantis' Ceph packages
================================================

Preparations
------------

* Install ansible version >= 2.1.x. On Ubuntu 16.04 this can be done
  with::

    apt-get install -t xenial-backports -y ansible

* Adjust ``group_vars/all``. You might want to set the source repository
  location, the path to the local mirror (which will be created), HTTP
  proxy, etc.

* Adjust ``hosts`` if you want to put the mirror somewhere else than
  localhost.


Making an initial copy
----------------------

::

  ansible-playbook -i hosts site.yml

This will take a while depending on the bandwith of your Internet link.


Updating the mirror
-------------------

Run the same command as above::

  ansible-playbook -i hosts site.yml

It's a no-op if the local mirror is up to date.
