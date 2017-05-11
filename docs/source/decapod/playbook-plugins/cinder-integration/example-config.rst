.. _plugin_cinder_integration_example_config:

=====================
Configuration example
=====================

The following is an example of the *Cinder integration* plugin configuration:

.. code-block:: json

   {
     "global_vars": {
       "cluster": "ceph"
     },
     "inventory": {
       "_meta": {
         "hostvars": {
           "10.0.0.20": {
             "ansible_user": "ansible",
             "clients": {
               "compute": {
                 "mon": "allow r",
                 "osd": "allow class-read object_prefix rbd_children, allow \
                 rwx pool=compute, allow rwx pool=volumes, allow rx pool=images"
               },
               "images": {
                 "mon": "allow r",
                 "osd": "allow class-read object_prefix rbd_children, allow \
                 rwx pool=images"
               },
               "volumes": {
                 "mon": "allow r",
                 "osd": "allow class-read object_prefix rbd_children, allow \
                 rwx pool=volumes, allow rx pool=images"
               }
             },
             "pools": {
               "compute": 64,
               "images": 64,
               "volumes": 64
             }
           }
         }
       },
       "mons": [
         "10.0.0.20"
       ]
     }
   }
