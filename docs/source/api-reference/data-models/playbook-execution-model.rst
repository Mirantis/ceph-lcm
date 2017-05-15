.. _decapod_data_model_playbook_execution:

==================
Playbook execution
==================

The execution model defines the execution of a playbook configuration. You can
run each playbook configuration several times, and this model defines a single
execution. As a result, you receive the execution status (completed, failed,
and others) and the execution log. The execution log can be shown as:

* Execution steps, which are the parsed steps of the execution.
* Raw log, which is a pure Ansible log of the whole execution as is, taken
  from ``stdout`` and ``stderr``.

Each execution step has timestamps (started, finished), ID of the server that
issued the event, role and task name of the event, status of the task, and
detailed information on the error, if any.

.. seealso::

   * :ref:`decapod_data_model_playbook_configuration`
