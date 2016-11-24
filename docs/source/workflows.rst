Workflows
=========

This chapter describes different workflows for Decapod. These workflows
should help user to understand how to work with Decapod and perform
required actions.



.. _workflows-server-discovery:

Server discovery
++++++++++++++++

As mentioned in :ref:`data-model-server-discovery`, it has to be done in
several steps.

1. Choose OS image with cloud-init support
2. Generate user-data config with :program:`decapod cloud-config` CLI
3. Deploy OS with such config

After that, if everything is correct, eventually server will be listed
in Decapod. Server discovery takes time because of cloud-init execution
therefore it might be listed in 5 minutes after deployment. If server
appears in Decapod, it means that tool can use it.



.. _workflows-cluster-deployment:

Cluster Deployment
++++++++++++++++++

As mentioned in :doc:`data_model` several models are required.

1. First, we need to create empty :ref:`data-model-server` model.
   This model is a holder for configuration of cluster, also it defines
   Ceph FSID and the name.
2. We need to create :ref:`data-model-playbook-configuration` model for
   ``deploy_cluster`` playbook. This and playbook will allow user to
   deploy cluster. Also, keep in mind that cluster deployment is
   idempotent operation and you may execute it several times.
3. Execute that playbook configuration, creating new
   :ref:`data-model-execution`. If something went wrong, examine
   execution steps or log.
