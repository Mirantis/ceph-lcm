.. _plugins_update_ceph_configuration_parameters_and_roles:

====================
Parameters and roles
====================

The *Update Ceph Configuraiton* plugin has only one parameter,
``ceph_conf_overrides``.

This parameters is a mapping, where keys are corresponding sections in
:file:`ceph.conf` and values are mappings of option name to value.

**Example**

.. code-block:: json

    {
        "ceph_conf_overrides": {
            "global": {
                "foo": 1,
                "bar": 2
            },
            "osd": {
                "osd journal size": 10000
            }
        }
    }

produce following modifications in :file:`ceph.conf`:

.. code-block:: ini

    [global]
    ...
    foo = 1
    bar = 2
    ...

    [osd]
    ...
    osd journal size = 10000
    ...

Following sections are supported: ``global``, ``mons``, ``osd``, ``rgw``.


.. seealso::

    `Configuring Ceph <http://docs.ceph.com/docs/master/rados/configuration/ceph-conf/>`_
