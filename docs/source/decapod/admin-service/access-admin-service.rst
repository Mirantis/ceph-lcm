.. _decapod_admin_service_access:

========================
Access the admin service
========================

To access the Decapod admin service:

.. code-block:: console

   $ docker-compose -p PROJECT_NAME exec admin bash

.. note::

   The :option:`-p` option is the name of the project. If you have not
   specified it when running ``docker-compose``, do not specify it now.

As a result, you will enter the container. The default environment allows you
to run the :program:`decapod` utility with a configured URL and login/password
pair ``root``/``root``.

.. code-block:: console

    root@7252bfd5947d:/# env | grep DECAPOD
    DECAPOD_PASSWORD=root
    DECAPOD_LOGIN=root
    DECAPOD_URL=http://frontend:80

The ``admin`` service provides bundled documentation within the container. To
access documentation:

#. Obtain the documentation port. The port is the value of the
   ``DECAPOD_DOCS_PORT`` environment variable and is ``9998`` by default.
#. Access the documentation using the obtained port and your credentials. For
   example, if you access Decapod using ``http://10.0.0.10:9999``, the
   documentation will be served on ``http://10.0.0.10:9998``.
