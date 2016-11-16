Decapod CLI
===========

Installation
------------

To install Decapod CLI on your local machine, you need to install 2
packages: ``decapodlib`` and ``decapod-cli``. First package is RPC
client library to access Decapod API, second is CLI wrapper for that
library.

To build packages, execute the following for the top level of the source
code repository:

.. code-block:: bash

    $ make build_eggs

This will build the packages and put them in the ``output/eggs``
directory. After that, you need to install them with

.. code-block:: bash

    $ pip install output/eggs/decapodlib*.whl output/eggs/decapod_cli*.whl

Execute decapod to check that installation succeed.



Usage
-----

To access Decapod, you need to know URL (``http://10.10.0.2:9999`` or
``https://10.10.0.2:10000``) and username with password. For development
installation is ``root``/``root``.

You need to set it to CLI directly or use environment variables:

.. code-block:: bash

    export DECAPOD_URL=http://10.10.0.2:9999
    export DECAPOD_LOGIN=root
    export DECAPOD_PASSWORD=root

Save it to a file and source when required.

To verify that it works, execute the following:

.. code-block:: bash

    $ decapod -u http://10.10.0.2:9999 -l root -p root user get-all

Or, if you prefer environment variables,

.. code-block:: bash

    $ decapod user get-all
