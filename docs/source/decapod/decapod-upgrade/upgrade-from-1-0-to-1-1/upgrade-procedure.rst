.. _decapod_upgrade_from_10_to_11:

===============
Upgrade Decapod
===============

**To upgrade Decapod from 1.0.x to 1.1.x:**

#. Back up the database.

   * Follow procedure, described in :ref:`decapod_user_guide_backup_restore`.

   * Try to restore database on another installation to verify that backup
     is not corrupted.

#. Obtain images for Decapod 1.1.x. to do so, follow steps 1-2 in the
   :ref:`decapod_install`

#. Create containers from existing images:

   .. code-block:: console

     $ docker-compose -p PROJECT create
     decapod_database_1 is up-to-date
     Recreating decapod_api_1
     Recreating decapod_frontend_1
     Recreating decapod_controller_1
     Recreating decapod_admin_1

   This command won't restart existing containers, just prepare new ones.

#. Restart services.

   * If you can have a maintenence window, then restart all services
     at once:

     .. code-block:: console

       $ docker-compose -p PROJECT restart
       Restarting decapod_frontend_1 ... done
       Restarting decapod_api_1 ... done
       Restarting decapod_admin_1 ... done
       Restarting decapod_controller_1 ... done
       Restarting decapod_database_1 ... done
       Restarting decapod_database_data_1 ... done


   * Otherwise, please restart services in following sequence:

     #. ``api`` service

       .. code-block:: console

         $ docker-compose -p PROJECT restart api
         Restarting decapod_api_1 ... done

     #. ``frontend`` service

       .. code-block:: console

         $ docker-compose -p PROJECT restart frontend
         Restarting decapod_frontend_1 ... done

     #. ``admin`` service

       .. code-block:: console

         $ docker-compose -p PROJECT restart admin
         Restarting decapod_admin_1 ... done

     #. ``controller`` service

       .. code-block:: console

         $ docker-compose -p PROJECT restart controller
         Restarting decapod_controller_1 ... done

     #. ``database`` service

       .. code-block:: console

         $ docker-compose -p PROJECT restart database
         Restarting decapod_database_1 ... done


#. Run database migrations:

   .. code-block:: console

     $ docker-compose -p PROJECT exec -T admin decapod-admin migration apply
