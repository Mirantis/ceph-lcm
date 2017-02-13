.. _decapod_install_run_containers:


Run containers with Decapod
===========================

When you have your docker images built, it is time to run Decapod.
To do that, you do not need to have source code at all, images are
enough. Minimal requirements to run Decapod in containers are installed
docker-engine and docker-compose.

To install docker-engine, please check instructions for build
machine. To install docker-compose, please check the official guide:
https://docs.docker.com/compose/install/

.. important::

    docker-compose should be version 1.6 or later. Please make
    sure, that you are running a proper one:

    .. code-block:: console

        $ pip install 'docker-compose>=1.6'

The next thing you need, is configuration for docker-compose.
It is placed in the top level of the source code repository as
docker-compose.yml. Place it in any place you like. After that, run it
as follows

.. code-block:: console

    $ docker-compose up

This will start the service. Docker-compose will use 2 socket binds:
0.0.0.0:9999 and 0.0.0.0:10000. Port 9999 is HTTP endpoint, 10000 -
HTTPS. Assuming, that your Decapod production machine uses IP 10.10.0.2,
you may access UI with http://10.10.0.2:9999 or https://10.10.0.2:10000.
