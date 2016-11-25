Playbook Plugins
================

This chapter describes different playbook plugins available for Decapod.

Every action related to host node management, if it is Decapod
responsibility, is done using such plugin. Later this documentation
will cover creating of new plugins, but right now it describes existing
official plugins and third party (community) plugins.

Decapod responsibility is Ceph management therefore most of plugins are
written to support different activities related to Ceph management:
cluster deployment, adding or removing of new OSDs etc. It is possible
to create plugins which works differently, doing the same tasks as
generic configuration management playbooks are doing. It is possible
but Decapod official set of plugins won't inclde them by default.
Nevertheless, it is possible to implement such plugins.

.. note::

    If you have such plugin, feel free to add it to the list in this
    document, section `Community Plugins`_.


Official Plugins
++++++++++++++++

.. toctree::
   :maxdepth: 1

   cluster_deploy
   add_osd




Community Plugins
+++++++++++++++++

No known plugins yet. Feel free to contribute!
