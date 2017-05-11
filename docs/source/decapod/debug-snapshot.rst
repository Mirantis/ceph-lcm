.. _decapod_user_guide_debug_snapshot:

==============================
Generate a diagnostic snapshot
==============================

To simplify the interaction between development and operation, Decapod
supports diagnostic or debug snapshots, similar to `Fuel snapshots
<http://docs.openstack.org/developer/fuel-docs/userdocs/fuel-user-guide/maintain-environment/create-snapshot.html>`_.
A snapshot is an archive that contains all information required to debug and
troubleshoot issues.

Snapshots store the following information:

* Backup of the database
* Logs from services
* File :file:`docker-compose.yml`
* Configuration files from Decapod services (:file:`config.yaml`)
* Datetimes from services
* Data from :ref:`ceph-monitoring <decapod_user_guide_monitoring>`
* Version of installed packages
* Git commit SHAs of Decapod itself
* Information about docker and containers

Snapshots do not store Ansible private keys or user passwords. Passwords are
hashed by `Argon2 <https://github.com/p-h-c/phc-winner-argon2>`_.

**To generate a diagnostic snapshot:**

Run the script:

.. code-block:: console

   $ ./scripts/debug_snapshot.py snapshot

Alternatively, if you have containers only, follow the steps below.

#. Run the following command:

   .. code-block:: console

      $ docker-compose exec -T admin cat /debug-snapshot | python - snapshot

#. Configure the snapshot settings as required:

   .. code-block:: console

      $ docker-compose -p myproject exec -T admin cat /debug-snapshot | python - --help
      usage: - [-h] [-f COMPOSE_FILE] [-p PROJECT_NAME] snapshot_path

      Create a debug snapshot for Decapod.

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

As a result, you will get a snapshot like :file:`snapshot_path.*`. The snapshot
tool calculates the best compression algorithm available on your platform
and uses its extension. Therefore, the snapshot may look like
:file:`snapshot_path.tar.bz2` or :file:`snapshot_path.tar.xz` depending on how
your Python was built.
