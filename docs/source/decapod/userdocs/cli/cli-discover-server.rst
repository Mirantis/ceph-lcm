.. _decapod_cli_discover_server:

=================
Discover a server
=================

**To discover a server:**

#. Generate the user-data configuration for ``cloud-init``. For details, see
   :ref:`decapod_generate_user_data`.

   The ``cloud-init`` execution generates the content of ``/etc/rc.local``.
   The first and next reboots will call the Decapod API for server registering.
   Such registration is an idempotent operation. The execution of the Decapod
   API (POST /v1/server) creates a task for the controller server on facts
   discovery. The controller executes this task and collects facts from the
   remote host. A new server model is created or the information on the
   existing one is updated.
#. With this configuration, deploy an operating system on a Ceph node. For an
   example of such deployment, see: :ref:`decapod_deploy_ceph_node_os`,
   `official cloud-init documentation <http://cloudinit.readthedocs.io/en/latest/topics/datasources.html>`_,
   or use `kernel parameters <https://github.com/number5/cloud-init/blob/master/doc/sources/kernel-cmdline.txt>`_.

As a result, the server should be listed in Decapod. The server discovery takes
time because of ``cloud-init``. Therefore, the server may appear in five
minutes after deployment. Once the server appears in Decapod, the tool can use
it.

.. seealso::

   *Ceph cluster deployed by Decapod* in *MCP Reference Architecture*
