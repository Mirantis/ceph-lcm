.. _decapod_user_guide_monitoring:

============
Monitor Ceph
============

Decapod supports integration with various monitoring systems. By default, it
uses an in-house tool called
`ceph-monitoring <https://github.com/Mirantis/ceph-monitoring/>`_. You can
also integrate Decapod with other tools, such as
`Prometheus <https://prometheus.io/>`_ through
`Telegraf <https://www.influxdata.com/time-series-platform/telegraf/>`_. For a
list of supported plugins, see :ref:`decapod_playbook_plugins`.

The ``ceph-monitoring`` tool collects statistics on the cluster state and
monitors its performance by running particular scripts under the ``admin``
service.

**To access the collected data:**

#. Obtain the Decapod monitoring port. The port is the value of the
   ``DECAPOD_MONITORING_PORT`` environment variable and is ``10001`` by
   default.

#. Access the data using the obtained port and your credentials. For example,
   if you access Decapod using ``http://10.0.0.10:9999``, the data will be
   served on ``http://10.0.0.10:10001``.

If there is no information available about a recently deployed cluster, try
again in 15 minutes. If the data is still not accessible, obtain the logs of
the ``admin`` service:

.. code-block:: console

   $ docker-compose -p myprojectname logs admin
