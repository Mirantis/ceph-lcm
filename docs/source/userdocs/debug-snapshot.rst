.. _decapod_user_guide_debug_snapshot:


Debug snapshot
==============

To simplify communication interface between production and development,
Decapod has a concept of debug snapshot, similar to `Fuel snapshots
<http://docs.openstack.org/developer/fuel-docs/userdocs/fuel-user-guide/maintain-environment/create-snapshot.html>`_: snapshot is an archive which contains all
information, required to debug and troubleshoot problems.

To generate snapshot, just execute following:

.. code-block:: console

    $ ./scripts/debug_snapshot.py snapshot

or, if you have containers only:

.. code-block:: console

    $ docker-compose exec -T admin cat /debug-snapshot | python - snapshot

If you use last way, please check docs and set correct settings if required:

.. code-block:: console

    $ docker-compose -p myproject exec -T admin cat /debug-snapshot | python - --help
    usage: - [-h] [-f COMPOSE_FILE] [-p PROJECT_NAME] snapshot_path

    Create debug snapshot for Decapod.

    positional arguments:
      snapshot_path         Path where to store snapshot (do not append extension,
                            we will do it for you).

    optional arguments:
      -h, --help            show this help message and exit
      -f COMPOSE_FILE, --compose-file COMPOSE_FILE
                            path to docker-compose.yml file. (default:
                            /vagrant/docker-compose.yml)
      -p PROJECT_NAME, --project-name PROJECT_NAME
                            the name of the project. (default: vagrant)

    Please find all logs in syslog by ident 'decapod-debug-snapshot'.

    $ docker-compose -p myproject exec -T admin cat /debug-snapshot | python - -p myproject snapshot

After execution, you will get snapshot as :file:`snapshot_path.*`
(snapshot tool will calculate best compression algorithm
available on your platform and use its extension. So you may get
:file:`snapshot_path.tar.bz2` or :file:`snapshot_path.tar.xz` depepnding
on how your Python was built).

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
