.. _decapod_install_cli:

Install decapod client libraries
================================

Decapod has 2 client libraries: 1 is `decapodlib` which is API client
implemented in RPC fashion (comparable to client libraries for other web
services). This library is supported by Python2 (>= 2.7 release) and
Python3 (>= 3.3 release). Please find details on that library in `API
reference <http://yandex.ru>`_.

Another library is called `decapodcli` and it is providing command line
interface for Decapod installation. `decapodcli` uses `decapodlib`
internally. As `decapodlib`, `decapodcli` also supports the same
Pythons: Python2 (>= 2.7) and Python3 (>= 3.3).

As for release 1.1, these libraries are not hosted on PyPI therefore you
have to install them from sources.


.. _decapod_install_decapodlib:

Install `decapodlib`
--------------------

#. Install prerequisites:

   .. code-block:: console

     $ apt-get install --no-install-recommends git gcc libssl-dev libyaml-dev python python-dev python-pip python-setuptools python-wheel

   If you would like to use Python3, then install these prerequisites:

   .. code-block:: console

     $ apt-get install --no-install-recommends git gcc libssl-dev libyaml-dev python3 python3-dev python3-pip python3-setuptools python3-wheel

#. Copy source code:

   .. code-block:: console

     $ git clone -b 1.1.0 --depth 1 https://github.com/Mirantis/ceph-lcm.git ~/decapod
     Cloning into '/home/vagrant/decapod'...
     remote: Counting objects: 1051, done.
     remote: Compressing objects: 100% (822/822), done.
     remote: Total 1051 (delta 312), reused 486 (delta 188), pack-reused 0
     Receiving objects: 100% (1051/1051), 1.15 MiB | 660.00 KiB/s, done.
     Resolving deltas: 100% (312/312), done.
     Checking connectivity... done.

#. Install `decapodlib`:

   .. code-block:: console

     $ pip2 install ~/decapod/decapodlib

   Or if you are using Python3:

   .. code-block:: console

     $ pip3 install ~/decapod/decapodlib

#. Verify that library is installed:

   .. code-block:: console

     $ python2 -c 'import decapodlib; print "OK"'
     OK

   Or with Python3:

   .. code-block:: console

     $ python3 -c 'import decapodlib; print("OK")'
     OK


Install `decapodcli`
--------------------

#. Install `decapodlib` as described in :ref:`decapod_install_decapodlib`.

#. Install CLI:

   .. code-block:: console

     $ pip2 install ~/decapod/decapodlib ~/decapod/decapodcli

   Or with Python3

   .. code-block:: console

     $ pip3 install ~/decapod/decapodlib ~/decapod/decapodcli

   .. note::

     Sometimes you may face with following bug:

     .. code-block:: pytb

       Traceback (most recent call last):
         File "/usr/lib/python2.7/dist-packages/pip/req/req_install.py", line 377, in setup_py
           import setuptools  # noqa
         File "/usr/share/python-wheels/setuptools-20.7.0-py2.py3-none-any.whl/setuptools/__init__.py", line 11, in <module>
         File "/usr/share/python-wheels/setuptools-20.7.0-py2.py3-none-any.whl/setuptools/extern/__init__.py", line 1, in <module>
       ImportError: No module named extern

    It basically means that package `cryptography` has installed latest
    `setuptools`. In that case just remove it and try again.

    .. code-block:: console

      $ pip2 uninstall setuptools

    It is safe to do because pip won't touch system `setuptools`.

#. Verify that CLI is set up:

   .. code-block:: console

     $ decapod
     Usage: decapod [OPTIONS] COMMAND [ARGS]...

     Decapod command line tool.

     With this CLI it is possible to access all API endpoints of Decapod. To do
     so, you have to provide some common configuration settings: URL, login and
     password to access.

     These settings are possible to setup using commandline parameter, but if
     you want, you can set environment variables:

         - DECAPOD_URL             - this environment variable sets URL to
                                     access.
         - DECAPOD_LOGIN           - this environment variable sets login.
         - DECAPOD_PASSWORD        - this environment variable sets password.
         - DECAPOD_TIMEOUT         - this environment variable sets timeout.
         - DECAPOD_NO_VERIFY       - this environment variable removes SSL
                                     certificate verification.
         - DECAPOD_SSL_CERTIFICATE - this environment variable sets a path
                                     to SSL client certificate.
         - DECAPOD_DEBUG           - this environment variable sets debug mode.
         - DECAPOD_NO_PAGER        - (deprecated) this environment variable
                                     removes pager support.
         - DECAPOD_PAGER           - this environment variable add pager
                                     support.

     Options:
       -u, --url TEXT                  Base URL for Decapod.  [required]
       -l, --login TEXT                Login to access Decapod.
       -p, --password TEXT             Password to access Decapod.
       -t, --timeout INTEGER           Timeout to access API. No timeout by
                                       default.
       -k, --no-verify                 Do not verify SSL certificates.
       -s, --ssl-certificate FILENAME
       -d, --debug                     Run in debug mode.
       -n, --no-pager                  Do not use pager for output.
       -r, --pager                     Use pager for output.
       -f, --output-format [json]      How to format output. Currently only JSON is
                                       supported.  [default: json]
       --version                       Show the version and exit.
       -h, --help                      Show this message and exit.

     Commands:
       cloud-config            Generates config for cloud-init.
       cluster                 Cluster subcommands.
       execution               Execution subcommands.
       info                    Request information about remove Decapod...
       password-reset          Password reset subcommands
       permission              Permission subcommands.
       playbook                Playbook subcommands.
       playbook-configuration  Playbook configuration subcommands.
       role                    Role subcommands.
       server                  Server subcommands.
       user                    User subcommands.
