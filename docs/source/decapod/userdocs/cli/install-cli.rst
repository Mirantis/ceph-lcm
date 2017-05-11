.. _decapod_install_cli:

=======================
Install the Decapod CLI
=======================

To install the Decapod CLI on a local machine, install two packages:

* ``decapodlib``, the RPC client library to access the Decapod API
* ``decapod-cli``, the CLI wrapper for the library

**To install the Decapod CLI:**

#. At the top level of the source code repository, run the following command
   to build the packages and place them to the ``output/eggs`` directory::

   $ make build_eggs

#. Install the packages::

   $ pip install output/eggs/decapodlib*.whl output/eggs/decapod_cli*.whl

#. Run :command:`decapod` to verify the installation.

.. seealso::

   * :ref:`decapod_access_cli`
