.. _decapod_access_cli:

======================
Access the Decapod CLI
======================

To access Decapod, you need to know its URL (http://10.10.0.2:9999 or
https://10.10.0.2:10000), your username and password (``root``/``root`` for a
development installation).

**To access Decapod using CLI:**

#. Set your credentials directly to the Decapod CLI or use the environment
   variables::

    export DECAPOD_URL=http://10.10.0.2:9999
    export DECAPOD_LOGIN=root
    export DECAPOD_PASSWORD=root

   Save this to a file and source when required.

#. Verify that it works::

    $ decapod -u http://10.10.0.2:9999 -l root -p root user get-all

   If you used environment variables, run::

    $ decapod user get-all
