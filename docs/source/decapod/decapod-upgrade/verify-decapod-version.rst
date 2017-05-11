.. _decapod_verify_version:

======================
Verify Decapod version
======================

**To verify the Decapod version installed:**

#. Obtain the project name:

   .. code-block:: console

      $ docker-compose ps | grep api | cut -f 1 -d '_' | sort -u
      shrimp

#. Verify the Decapod version:

   .. code-block:: console

      docker inspect -f '{{ .Config.Labels.version }}' $(docker-compose -p \
      PROJ ps -q database | head -n 1)

   Where ``PROJ`` is the project name.

   **Example:**

   .. code-block:: console

      docker inspect -f '{{ .Config.Labels.version }}' $(docker-compose -p \
      PROJ ps -q database | head -n 1)
      0.1.0
