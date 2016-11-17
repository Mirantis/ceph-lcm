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

Description of these fields:

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

JSON Schema
-----------

Real-world Example
------------------

Field description
-----------------
