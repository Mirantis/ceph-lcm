.. _decapod_config_yaml:

==========================
Decapod configuration file
==========================

Decapod configuration is performed within the ``config.yaml`` file in `YAML
<http://www.yaml.org/>`_ format. Decapod searches for the configuration file
in several locations in the following order:

* ``$(pwd/decapod.yaml``
* ``$XDG_CONFIG_HOME/decapod/config.yaml``
* ``:`$HOME/.decapod.yaml``
* ``/etc/decapod/config.yaml``
* Default configuration file of the ``decapod_common`` package

If a configuration file was found and parsed before, other alternatives
will not be used. Therefore, if you have the default configuration file in
``/etc/decapod/config.yaml`` then placing the configuration to
``$XDG_CONFIG_HOME/decapod/config.yaml`` will override the default one. For
details, see `XDG Base Directory Specification
<https://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html>`_.

Default configuration in containerized Decapod stack is placed in
``/etc/decapod/config.yaml``.

.. toctree::
   :maxdepth: 1

   config-yaml-example.rst
   settings-description.rst
   auth-backends/authentication-backends.rst
