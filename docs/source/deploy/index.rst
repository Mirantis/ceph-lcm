Deployment
==========

In the future, it will be possible to run decapod services on different
machines, but this guide assumes that you have only one machine with
docker and docker-compose. There may be one build machine and another
production one.

If you have such a diversity, please use Docker registry to manage
Decapod images or dump/load them manually. To do so, build images and
execute the following commands:

.. code-block:: bash

    $ make dump_images
    $ rsync -a output/images/ <remote_machine>:images/
    $ scp docker-compose.yml <remote_machine>:docker-compose.yml
    $ ssh <remote_machine>
    $ cd images
    $ for i in $(\ls -1 *.bz2); do docker load -i "$i"; done;
    $ cd ..
    $ docker-compose up

This will dump docker images, copy them to remote host and load. After
that it will be possible to run ``docker-compose``.


.. toctree::

     run_docker_containers
