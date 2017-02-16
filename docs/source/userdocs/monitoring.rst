.. _decapod_user_guide_monitoring:


Ceph monitoring
===============

Decapod may support integration with various monitoring
systems. It ships with simplistic in-house monitoring tool
`ceph-monitoring <https://github.com/Mirantis/ceph-monitoring/>`_.
Also, it is possible to integrate with other tools like
`Prometheus <https://prometheus.io/>`_ via `Telegraf
<https://www.influxdata.com/time-series-platform/telegraf/>`_. In future
there will be more choices presented, please check the :doc:`list of
supported plugins <../playbook-plugins>`.

:program:`ceph-monitoring` is a tool which collects statistics on
cluster state and monitors performance from time to time, you may
consider it as executed by Cron.

*admin* service serves collected data. To access it,
check :envvar:`DECAPOD_MONITORING_PORT` environment variable (default is
**10001**). So, if you access Decapod like **http://10.0.0.10:9999**,
docs will be served on **http://10.0.0.10:10001**.

If you do not have information on cluster which was just deployed,
please wait ~15 minutes and try again. If data is still not accessible,
please check logs of **admin** service. You can get them with following
command:

.. code-block:: console

    $ docker-compose -p myprojectname logs admin
