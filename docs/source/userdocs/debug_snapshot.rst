.. _decapod_user_guide_debug_snapshot:


Debug snapshot
==============

To simplify communication interface between production and development,
Decapod has a concept of debug snapshot, similar to `Fuel snapshots
<http://docs.openstack.org/developer/fuel-docs/userdocs/fuel-user-guide/maintain-environment/create-snapshot.html>`_: snapshot is an archive which contains all
information, required to debug and troubleshoot problems.

To generate snapshot, just execute following:

.. code-block:: console

    $ ./scripts/debug_snapshot.sh snapshot.tar.xz

Information, stored in the snapshot:

* Backup of the database
* Logs from services
* :file:`docker-compose.yml` file
* Configuration files from Decapod services (:file:`config.yaml`)
* Datetimes from services
* Data from :ref:`ceph-monitoring <decapod_user_guide_monitoring>`
* Version of installed packages
* Git commit SHAs of Decapod itself
* Information about docker and containers

No ansible private keys or user passwords (they are hashed by `Argon2
<https://github.com/p-h-c/phc-winner-argon2>`_) are stored in debug
snapshot.
