API models
==========

Decapod API is classical RESTful JSON API, but it operates with models.
By term "models" it is meant JSON structured data in some generic way.
Each entity for end user is present is some generic way.

This chapter tries to cover models in details, describing meaning of
each field in each model. If you check :doc:`usage` or :doc:`decapodlib`
chapters, you will see some references to ``data`` field, ``version``
etc. Also, you will see, that updating of models require whole model.
This chapter is intended to explain how to update models and why whole
model is required.


Basic model
+++++++++++

Basically, simple model looks like this:

.. code-block:: json

    {
        "data": {
            "somefield": "somevalue",
        },
        "id": "ee3944e8-758e-45dc-8e9e-e220478e442c",
        "initiator_id": null,
        "model": "something",
        "time_deleted": 0,
        "time_updated": 1479295535,
        "version": 1
    }

As you can see, model has 2 parts: ``data`` field and *envelope*.
Envelope is a set of fields which are common for every model and
guaranteed to be there. ``data`` field is the model specific set of data
and can be arbitrary. The only guarantee here is that field is mapping
one (i.e ``data`` field cannot be list or null).


Basic Model JSON Schema definitions
-----------------------------------

There are some JSON Schema definitions that mentioned here to avoid
duplication.

.. code-block:: json

    {
        "non_empty_string": {
            "type": "string",
            "minLength": 1,
            "maxLength": 1024
        },
        "email": {
            "allOf": [
                {"type": "string", "format": "email"},
                {
                    "type": "string",
                    "pattern": "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
                }
            ]
        },
        "positive_integer": {
            "type": "number",
            "multipleOf": 1.0,
            "minimum": 0
        },
        "uuid4_array": {
            "type": "array",
            "items": {"$ref": "#/definitions/uuid4"}
        },
        "uuid4": {
            "type": "string",
            "pattern": "^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}$"
        },
        "dmidecode_uuid": {
            "type": "string",
            "pattern": "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
        },
        "dmidecode_uuid_array": {
            "type": "array",
            "items": {"$ref": "#/definitions/dmidecode_uuid"}
        },
        "hostname": {
            "type": "string",
            "format": "hostname"
        },
        "ip": {
            "oneOf": [
                {"type": "string", "format": "ipv4"},
                {"type": "string", "format": "ipv6"}
            ]
        }
    }


Basic Model JSON Schema
-----------------------

.. code-block:: json

    {
        "type": "object",
        "properties": {
            "id": {"$ref": "#/definitions/uuid4"},
            "model": {"$ref": "#/definitions/non_empty_string"},
            "time_updated": {"$ref": "#/definitions/positive_integer"},
            "time_deleted": {"$ref": "#/definitions/positive_integer"},
            "version": {"$ref": "#/definitions/positive_integer"},
            "initiator_id": {
                "anyOf": [
                    {"type": "null"},
                    {"$ref": "#/definitions/uuid4"}
                ]
            },
            "data": {"type": "object"}
        },
        "additionalProperties": false,
        "required": [
            "id",
            "model",
            "time_updated",
            "time_deleted",
            "version",
            "initiator_id",
            "data"
        ]
    }

All model description below contains JSON Schema only for ``data``
field.


Field description
-----------------

============    =========================================================================================
Field           Description
============    =========================================================================================
id              Unique identifier of the model. Most identifiers are simply UUID4 (:rfc:`4122`).
initiator_id    ID of the user who initiated creation of that version.
model           Name of the model.
time_deleted    UNIX timestamp when model was deleted. If model is not deleted, then this field is ``0``.
time_updated    UNIX timestamp when this model was modified last time.
version         Version of the model. Numbering starts from ``1``.
============    =========================================================================================

A few things to know about data model in Decapod:

1. Nothing is deleted. Nothing is overwritten. You can always get whole
   history of changes for every model.
2. Decapod uses numbered versioning for a model. You may consider each
   version as `value of the value
   <https://www.youtube.com/watch?v=-6BsiVyC1kM>`_.
3. If you update any field for a model, update does not occur inplace.
   Instead, new version is created. You can always access previous versions
   later to verify changes made in new version.
4. Deletion is not actual removing from database. Instead, new version
   is created. The only difference is in ``time_deleted`` field. If
   model was *deleted*, then ``time_deleted`` is UNIX timestamp
   of the moment when such event was occured. It is better to
   consider Decapod deletion as a mix of archivation and sealing.
5. Any active model (not deleted) has ``time_deleted == 0``.
6. If model was deleted, any further progression is forbidden.
7. Deleted model is excluded from listings by default but it is always
   possible to access it with parametrized listing or direct request.


User
++++


JSON Schema
-----------

Real-world Example
------------------

Field description
-----------------


Role
++++

JSON Schema
-----------

Real-world Example
------------------

Field description
-----------------


Cluster
+++++++

JSON Schema
-----------

Real-world Example
------------------

Field description
-----------------


Server
++++++

JSON Schema
-----------

Real-world Example
------------------

Field description
-----------------


Playbook Configuration
++++++++++++++++++++++

JSON Schema
-----------

Real-world Example
------------------

Field description
-----------------


Execution
+++++++++

JSON Schema
-----------

Real-world Example
------------------

Field description
-----------------



Execution Step
++++++++++++++

JSON Schema
-----------

Real-world Example
------------------

Field description
-----------------



Token
+++++

Token model presents an authentication token. Token is a string which
should be put in **Authorization** header of every request and Decapod
API uses it as an authentication mean for operations.

``version`` is rudimentary field here and kept for consistency. Do not
rely on this field, it always equals 1.


JSON Schema
-----------

.. code-block:: json

    {
        "user": {"type": "User Model"}
        "expires_at": {"$ref": "#/definitions/positive_integer"}
    }


Real-world Example
------------------

.. code-block:: json

    {
        "data":{
            "expires_at":1479455919,
            "user":{
                "data":{
                    "email":"noreply@example.com",
                    "full_name":"Root User",
                    "login":"root",
                    "role_id":"4f96f3b0-85e5-4735-8c97-34fbef157c9d"
                },
                "id":"ee3944e8-758e-45dc-8e9e-e220478e442c",
                "initiator_id":null,
                "model":"user",
                "time_deleted":0,
                "time_updated":1479295535,
                "version":1
            }
        },
        "id":"cc6cf706-2f26-4975-9885-0d9c234491b2",
        "initiator_id":"ee3944e8-758e-45dc-8e9e-e220478e442c",
        "model":"token",
        "time_deleted":0,
        "time_updated":1479454119,
        "version":1
    }


Field description
-----------------

==========    =======================================================================
Field         Description
==========    =======================================================================
expires_at    UNIX timestamp of moment when this token will be considered as expired.
user          Expanded model of user logged in.
==========    =======================================================================
