.. _plugins_update_ceph_configuration_parameters_and_roles:

====================
Parameters and roles
====================

``ceph_conf_overrides``
  This parameter redefines some options which are propagated in ceph
  cluster configuration (e.g. `/etc/ceph/ceph.conf`). This is a mapping
  where keys are sections in config file and values are mappings between
  options and their actual values.

  **Example**

  .. code-block:: ini

    [global]
    journal size = 512

    [some other section]
    option1 = 1
    option2 = yes

  The relevant ``ceph_conf_overrides`` is:

  .. code-block:: json

      {
          "global": {
              "journal size": 512
          },
          "some other section": {
              "option1": "1",
              "option2": "yes"
          }
      }
