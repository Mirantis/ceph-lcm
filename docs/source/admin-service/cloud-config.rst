.. _decapod_admin_service_cloud_config:


Generate cloud-init user-data config
====================================

You can generate user-data config for cloud-init with :program:`decapod`
as described in :ref:`decapod_generate_user_data` chapter, but since
:program:`decapod-admin` knows about Decapod installation much more
than :program:`decapod` is expected to know, you can use it to generate
correct config.

**Overview**

.. code-block:: console

    root@7252bfd5947d:/# decapod-admin cloud-config --help
    Usage: decapod-admin cloud-config [OPTIONS] PUBLIC_URL

      Generate cloud-init user-data config for current installation.

    Options:
      -u, --username TEXT    Username which should be used by Ansible  [default:
                             ansible]
      -n, --no-discovery     Generate config with user and packages but no
                             discovery files.
      -t, --timeout INTEGER  Timeout for remote requests.  [default: 20]
      -h, --help             Show this message and exit.

So, you need to set only URL accessible by Ceph nodes.

.. code-block:: console

    root@7252bfd5947d:/# decapod-admin cloud-config http://10.0.0.10:9999
    #cloud-config
    packages: [python]
    runcmd:
    - [echo, === START DECAPOD SERVER DISCOVERY ===]
    - [sh, -xc, 'grep -q ''/usr/share/server_discovery.sh'' /etc/rc.local || sed -i ''s?^exit 0?/usr/share/server_discovery.sh >> /var/log/server_discovery.log 2>\&1\nexit 0?'' /etc/rc.local']
    - [sh, -xc, systemctl enable rc-local.service || true]
    - [sh, -xc, /usr/share/server_discovery.sh 2>&1 | tee -a /var/log/server_discovery.log]
    - [echo, === FINISH DECAPOD SERVER DISCOVERY ===]
    users:
    - groups: [sudo]
      name: ansible
      shell: /bin/bash
      ssh-authorized-keys: [ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC7K9bHPrSu5VHnUOis2Uwc822fMyPTtwjfOkzNi/oVOxmd1QE3DilrO5fJ33pRwEj7r1DfTlJmZWs8XwWaaUXkQ+iyfRPtgt/Ox+X5A/XaLdi/yz7UjnHc8ERDUT/z73RzDwf21KNQOopGRuyhe+gvGZ5mhYDz3bnnYY9IRBNYaGw4bjS0q1AbkPa1PvCo7P5b5UuRjhi4H74zCFkQD4evQsrQOcgev5GimnODqMntU0jnI/eEJwnnd1TcYG7dS6FqMWpFX1gqcKjFIuqNTZLYzJu9U8mxxKmGOQSI6KWfP0etBw1YRHRIfdZmdaqSKHh0ZhUUHjbf8Hb5Vqv1Fkzf0cGPbfrazEDI5FaVjkZMGFfdgs1be6xO7NHqzu1JJ3ZEur28o0AQyOVvrEJIxQayDM0qyKi7B4+j6QDL0CDaWN3dUZO45il/KOm/eXCm4yQg0ImXHUmsDoW+6W6akI/fSCAn8r9GK2QBBJPeTPA95WlOSXtICnrsqgb74yKPEsslzfrTUIiyoXBuuR9o5OoPXghKrazqcTeK/Vdl7w4nZ00O4jllHMTrS1xyubN0QeBd+3D8Hy2bN5h7WjiJsZ2XhlKR0Z1i5AbgCR9hfQl84aFIXRARz+6uuDDHe2ONXujcS9jhuN7SOLGckiaXNfAeAsbEkYZytnUgdoxbHYSfzw==]
      sudo: ['ALL=(ALL) NOPASSWD:ALL']
    write_files:
    - content: |
        #-*- coding: utf-8 -*-

        from __future__ import print_function

        import json
        import ssl
        import sys

        try:
            import urllib.request as urllib2
        except ImportError:
            import urllib2

        data = {
            "username": 'ansible',
            "host": sys.argv[1].lower().strip(),
            "id": sys.argv[2].lower().strip()
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": '26758c32-3421-4f3d-9603-e4b5337e7ecc',
            "User-Agent": "cloud-init server discovery"
        }

        def get_response(url, data=None):
            if data is not None:
                data = json.dumps(data).encode("utf-8")
            request = urllib2.Request(url, data=data, headers=headers)
            request_kwargs = {"timeout": 20}
            if sys.version_info >= (2, 7, 9):
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                request_kwargs["context"] = ctx
            try:
                return urllib2.urlopen(request, **request_kwargs).read()
            except Exception as exc:
                print("Cannot request {0}: {1}".format(url, exc))

        metadata_ip = get_response('http://169.254.169.254/latest/meta-data/public-ipv4')
        if metadata_ip is not None:
            data["host"] = metadata_ip
            print("Use IP {0} discovered from metadata API".format(metadata_ip))

        response = get_response('http://10.0.0.10:9999', data)
        if response is None:
            sys.exit("Server discovery failed.")
        print("Server discovery completed.")
      path: /usr/share/server_discovery.py
      permissions: '0440'
    - content: |
        #!/bin/bash
        set -xe -o pipefail

        echo "Date $(date) | $(date -u) | $(date '+%s')"

        main() {
            local ip="$(get_local_ip)"
            local hostid="$(get_local_hostid)"

            python /usr/share/server_discovery.py "$ip" "$hostid"
        }

        get_local_ip() {
            local remote_ipaddr="$(getent ahostsv4 "10.0.0.10" | head -n 1 | cut -f 1 -d ' ')"

            ip route get "$remote_ipaddr" | head -n 1 | rev | cut -d ' ' -f 2 | rev
        }

        get_local_hostid() {
            dmidecode | grep UUID | rev | cut -d ' ' -f 1 | rev
        }

        main
      path: /usr/share/server_discovery.sh
      permissions: '0550'
