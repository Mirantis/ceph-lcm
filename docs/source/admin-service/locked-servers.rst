.. _decapod_admin_service_locked_servers:


Unlock servers
==============

All playbook executions lock servers they use. This is done to eliminate
situation when concurrent execution will cause unexpected problems.
But sometimes bugs happen and you need to unlock servers manually. Of
course, you have to be really cautious on that but as a last resort, you
can break lock with :program:`decapod-admin`.

**Overview**

.. code-block:: console

    root@7252bfd5947d:/# decapod-admin locked-servers get-all -h
    Usage: decapod-admin locked-servers get-all [OPTIONS]

      List locked servers

    Options:
      -f, --output-format [json|csv]  Format of the output  [default: json]
      -h, --help                      Show this message and exit.
    root@7252bfd5947d:/# decapod-admin locked-servers --help
    Usage: decapod-admin locked-servers [OPTIONS] COMMAND [ARGS]...

      Commands to manage locked servers.

    Options:
      -h, --help  Show this message and exit.

    Commands:
      get-all  List locked servers
      unlock   Unlock servers.

    root@7252bfd5947d:/# decapod-admin locked-servers get-all --help
    Usage: decapod-admin locked-servers get-all [OPTIONS]

      List locked servers

    Options:
      -f, --output-format [json|csv]  Format of the output  [default: json]
      -h, --help                      Show this message and exit.

    root@7252bfd5947d:/# decapod-admin locked-servers unlock --help
    Usage: decapod-admin locked-servers unlock [OPTIONS] SERVER_ID...

      Unlock servers.

    Options:
      -h, --help  Show this message and exit.
