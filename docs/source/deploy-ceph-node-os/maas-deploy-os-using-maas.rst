.. _maas_deploy_os_using_maas:

=======================
Deploy an OS using MAAS
=======================

**To deploy an operating system using MAAS:**

#. Encode the user data to ``base64`` and send it to MAAS::

    $ decapod -u http://10.10.0.2:9999 cloud-config \
      7f080dab-d803-4339-9c69-e647f7d6e200 ansible_ssh_keyfile.pem.pub \
      | base64 -w 0 > user_data.txt

#. Deploy an OS using the required MAAS version.

   .. note::

      MAAS 2.0 has non-backward-compatible API changes.

   * MAAS 2.0:

     #. Obtain ``system_id`` of the machine to deploy::

         $ maas mymaas nodes read

     #. Deploy the OS::

         $ maas mymaas machine deploy {system_id} user_data={base64-encoded of user-data}

        Where ``mymaas`` is the profile name of the MAAS command line.

   * MAAS prior to 2.0:

     #. Obtain ``system_id`` of the machine to deploy::

         $ maas prof nodes list

     #. Deploy the OS::

         $ maas mymaas node start {system_id} user_data={base64-encoded of user-data} distro_series={distro series. Eg. trusty}

        Where ``mymaas`` is the profile name of the MAAS command line.
