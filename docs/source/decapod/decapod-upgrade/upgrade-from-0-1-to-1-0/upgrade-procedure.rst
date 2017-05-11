.. _decapod_upgrade_from_01_to_02:

===============
Upgrade Decapod
===============

**To upgrade Decapod from 0.1.x to 1.0.0:**

#. Back up the database:

   * To use the existing configuration, run the following command from the
     directory where you run Decapod:

     .. code-block:: console

        $ docker exec -i proj_database_1 mongodump --gzip --archive --ssl \
        --sslAllowInvalidCertificates > ~/pre_upgrade

     Where ``proj`` is the lowercase container name.

     .. note:: To restore the database:

               .. code-block:: console

                 $ docker exec -i proj_database_1 mongorestore --drop --gzip \
                 --archive --ssl --sslAllowInvalidCertificates < ~/pre_upgrade

   * To use the default configuration, rename the database in MongoDB from
     ``shrimp`` to ``decapod`` and back up the data.

     #. Rename the database:

        .. code-block:: console

           $ docker-compose -p PROJ exec database moshell
           MongoDB shell version: 3.2.10
           connecting to: false
           2017-02-14T06:38:15.400+0000 W NETWORK  [thread1] The server \
           certificate does not match the host name 127.0.0.1
           Welcome to the MongoDB shell.
           For interactive help, type "help".
           For more comprehensive documentation, see
                   http://docs.mongodb.org/
           Questions? Try the support group
                   http://groups.google.com/group/mongodb-user
           Server has startup warnings:
           2017-02-14T06:20:54.806+0000 I CONTROL  [initandlisten]
           2017-02-14T06:20:54.806+0000 I CONTROL  [initandlisten] ** WARNING:\
            /sys/kernel/mm/transparent_hugepage/enabled is 'always'.
           2017-02-14T06:20:54.806+0000 I CONTROL  [initandlisten] **        \
           We suggest setting it to 'never'
           2017-02-14T06:20:54.806+0000 I CONTROL  [initandlisten]
           2017-02-14T06:20:54.806+0000 I CONTROL  [initandlisten] ** WARNING:\
            /sys/kernel/mm/transparent_hugepage/defrag is 'always'.
           2017-02-14T06:20:54.806+0000 I CONTROL  [initandlisten] **        \
           We suggest setting it to 'never'
           2017-02-14T06:20:54.806+0000 I CONTROL  [initandlisten]
           > db.copyDatabase("shrimp", "decapod", "localhost")
           { "ok" : 1 }
           > use shrimp
           switched to db shrimp
           > db.dropDatabase()
           { "dropped" : "shrimp", "ok" : 1 }

     #. Back up the database:

        .. code-block:: console

           $ docker exec -i proj_database_1 mongodump --gzip --archive --ssl \
           --sslAllowInvalidCertificates > ~/pre_upgrade_renamed

#. Optional. If you have modified any configuration files such as
   ``config.yaml`` or ``id_rsa``, copy the files to a custom directory, for
   example, `~/decapod_runtime`. To do so, run the following commands from the
   same directory used to run Decapod 0.1:

   .. code-block:: console

      $ mkdir ~/decapod_runtime
      $ docker cp "$(docker-compose -p PROJ ps -q api):/etc/shrimp/config.yaml" ~/decapod_runtime
      $ docker cp "$(docker-compose -p PROJ ps -q controller):/root/.ssh/id_rsa" ~/decapod_runtime
      $ docker cp "$(docker-compose -p PROJ ps -q frontend):/ssl/dhparam.pem" ~/decapod_runtime
      $ docker cp "$(docker-compose -p PROJ ps -q frontend):/ssl/ssl.crt" ~/decapod_runtime
      $ docker cp "$(docker-compose -p PROJ ps -q frontend):/ssl/ssl.key" ~/decapod_runtime
      $ docker cp "$(docker-compose -p PROJ ps -q database):/certs/mongodb.pem" ~/decapod_runtime
      $ docker cp "$(docker-compose -p PROJ ps -q database):/certs/mongodb-ca.crt" ~/decapod_runtime

   .. note:: If you did not generate any custom configuration files and used
             the default configuration, skip this step and proceed to step 4.

#. Obtain the Decapod 1.0.0 images. To do so, follow steps 1-2 in the
   *Install Decapod* section of *MCP Deployment Guide*.

   .. note:: The required configuration files are stored in
             ``~/decapod_runtime`` and the repository for Decapod 1.0.0 is
             cloned to ``~/decapod`` as described in
             :ref:`decapod_upgrade_01_10_prerequisites`.

#. Stop and remove containers for version 0.1.x. Since Docker containers are
   stateless and you have created a backup of the state (the database backup),
   drop the existing containers and start new ones. Execute the following
   command from the directory where you run Decapod:

   .. code-block:: console

      $ docker-compose -p PROJ down -v

#. Run Decapod 1.0.0.

   #. Change the directory to ``~/decapod_runtime``.
   #. Run Decapod:

      .. code-block:: console

          $ docker-compose -p PROJ up --remove-orphans -d

#. Restore the database:

   .. code-block:: console

      $ docker exec -i $(docker-compose -p PROJ ps -q admin) decapod-admin db \
      restore < ~/pre_upgrade_renamed

   Alternatively, if you did not rename the database:

   .. code-block:: console

      $ docker exec -i (docker-compose -p PROJ ps admin) decapod-admin db restore < ~/pre_upgrade

#. Apply migrations:

   .. code-block:: console

       $ docker-compose -p PROJ exec admin decapod-admin migration apply

#. Optional. You can configure MongoDB to be not backward compatible with the
   previous release. To do so, run:

   .. code-block:: console

       $ docker-compose -p PROJ exec database moshell
       MongoDB server version: 3.4.2
       Welcome to the MongoDB shell.
       For interactive help, type "help".
       For more comprehensive documentation, see
               http://docs.mongodb.org/
       Questions? Try the support group
               http://groups.google.com/group/mongodb-user
       Server has startup warnings:
       2017-02-14T07:00:13.729+0000 I STORAGE  [initandlisten]
       2017-02-14T07:00:13.730+0000 I STORAGE  [initandlisten] ** WARNING: \
       Using the XFS filesystem is strongly recommended with the WiredTiger storage engine
       2017-02-14T07:00:13.730+0000 I STORAGE  [initandlisten] **          \
       See http://dochub.mongodb.org/core/prodnotes-filesystem
       2017-02-14T07:00:15.199+0000 I CONTROL  [initandlisten]
       2017-02-14T07:00:15.199+0000 I CONTROL  [initandlisten] ** WARNING: \
       Access control is not enabled for the database.
       2017-02-14T07:00:15.199+0000 I CONTROL  [initandlisten] **          \
       Read and write access to data and configuration is unrestricted.
       2017-02-14T07:00:15.199+0000 I CONTROL  [initandlisten]
       2017-02-14T07:00:15.199+0000 I CONTROL  [initandlisten]
       2017-02-14T07:00:15.199+0000 I CONTROL  [initandlisten] ** WARNING: \
       /sys/kernel/mm/transparent_hugepage/enabled is 'always'.
       2017-02-14T07:00:15.199+0000 I CONTROL  [initandlisten] **        \
       We suggest setting it to 'never'
       2017-02-14T07:00:15.199+0000 I CONTROL  [initandlisten]
       2017-02-14T07:00:15.199+0000 I CONTROL  [initandlisten] ** WARNING: \
       /sys/kernel/mm/transparent_hugepage/defrag is 'always'.
       2017-02-14T07:00:15.199+0000 I CONTROL  [initandlisten] **        \
       We suggest setting it to 'never'
       2017-02-14T07:00:15.199+0000 I CONTROL  [initandlisten]
       > db.adminCommand({setFeatureCompatibilityVersion: "3.4"})
       { "ok" : 1  }

#. Optional. Change the ``root`` password as described in
   :ref:`decapod_admin_service_password_reset`.
