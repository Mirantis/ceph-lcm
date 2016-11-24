Cluster Deployment
==================

This chapters covers :ref:`workflows-cluster-deployment` workflow with UI.

.. note::

    The same workflow is present in `demo
    <https://www.youtube.com/watch?v=hvEyqutiwZs>`_ of Decapod.

Let's proceed by workflow steps. First, we need to have cluster.



Create Cluster
++++++++++++++

Proceed to the **Cluster** tab and click **Create new cluster**.

.. image:: /images/ui/cm-create-cluster.png

Click **Save changes** and you are done.

Empty cluster has almost nothing: no servers therefore no details.

.. image:: /images/ui/cm-empty-cluster.png



Servers
+++++++

To check our servers proceed to **Servers** tab.

.. image:: /images/ui/cm-servers.png

This page lists servers, known and accessible by Decapod. For
information on how to add servers to Decapod, please check
:ref:`workflows-server-discovery` workflow.

If you click little arrow on the side of server, you can check details.

.. image:: /images/ui/cm-servers-details.png



Create Playbook Configuration
+++++++++++++++++++++++++++++

To create playbook configuration, proceed to **Playbook Configuration**
page and click **New playbook configuration**.

.. image:: /images/ui/cm-playbook-configuration-new.png

User creates playbook configuration using 3 steps wizard:

1. First screen (above) sets name of the configuration and cluster
   for that.
2. Second screen will give you a possibility to select playbook.
3. Third screen will list you a servers to select.

So, click on **Next** button will lead you to the screen with playbooks.

.. image:: /images/ui/cm-playbook-configuration-playbooks.png

This table shows you playbooks available for execution. The most
interesting parameter here is **Servers required**. Some playbooks
requires explicit list of servers, some - don't. For example, if you
want to purge whole cluster, Decapod will use servers in this cluster,
there is not need to specify them manually: it is clear from the
context.

Next screen is server list. We choose all servers here.

.. image:: /images/ui/cm-playbook-configuration-servers.png

Click on **Save changes** creates new playbook configuration. After that
you get a screen where user can edit playbook configuration. Right now
it is a JSON, described in :ref:`data-model-playbook-configuration` data
model.



Execute Playbook Configuration
++++++++++++++++++++++++++++++

Having playbook configuration created, you can execute it clicking
**Execute** button.

.. image:: /images/ui/cm-playbook-configuration-execute.png

If you have several versions (like on the screenshot below), you can
execute any version in history, not only latest one.

.. image:: /images/ui/cm-playbook-configuration-execute3.png

Let's execute our initial version. After you click **Execute**, you will
get new execution on the page **Executions**.

.. image:: /images/ui/cm-execution-created.png

After a while, its status will be changed to ``started``.

.. image:: /images/ui/cm-execution-started.png

During execution process, you can check how it is going checking
execution log. After execution will be finished, you can download whole
log of execution clicking on **Download** button.

.. image:: /images/ui/cm-execution-steps.png

After a while, execution will be finished.

.. image:: /images/ui/cm-execution-completed.png
