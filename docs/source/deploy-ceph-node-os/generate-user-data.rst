.. _decapod_generate_user_data:

==================
Generate user data
==================

Verify that you have completed the steps described in
:ref:`decapod_generate_user_data_prerequisites`.

**To generate user data:**

Run the following command::

 $ decapod -u http://10.10.0.2:9999 cloud-config \
   7f080dab-d803-4339-9c69-e647f7d6e200 ansible_ssh_keyfile.pem.pub

Where the URL is the public URL of the Decapod machine with a correct port.
The servers will send an HTTP request for server discovery using this URL. As
a result, you will obtain a YAML-like user data.

MAAS requires user-data config to be BASE64 encoded. You can do that with::

  $ decapod -u http://10.10.0.2:9999 cloud-config \
        7f080dab-d803-4339-9c69-e647f7d6e200 ansible_ssh_keyfile.pem.pub \
    | base64 -w 0

:option:`-w` in :program:`base64` means line wrapping. We need to disable it.
