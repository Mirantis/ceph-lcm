==========
Change Log
==========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <http://keepachangelog.com>`_
and this project adheres to `Sematic Versioning <http://semver.org>`_.



--------------------
[1.0.1] - 2017-05-15
--------------------

Changed
*******

* Fixes for `cidner_integration` playbook
* Correct task canceling
* Support for NIC aliases on playbook generation
* More liberal verification of IDs on server discovery


------------------
[1.0] - 2017-03-14
------------------

Added
*****

* New *admin* service was introduced. Admin service replace old *cron*
  service and contains a list of migrations and various misc utilities.
* Reworked UI wizard, introduced a lots of improvements and fixes
* Integration with Keystone
* New plugins:
  * Add monitor
  * Cinder integration
  * Telegraf integration
* Verification of installed Ceph versions on adding new OSDs and monitors
* New scripts for backup/restore
* Script for creating debug snapshot

Changed
*******

* Project has been renamed from Shrimp to Decapod
* Only docker and make are required to build service
* There is no need to embed configuration files into images, user can
  inject them as volumes
* MongoDB 3.4 is used as database

Removed
*******

* Cron service is removed



--------------------
[0.1.2] - 2017-02-15
--------------------

Added
*****

* Documentation has been added
* Scripts were fixed to support upgrade procedure to 0.2



--------------------
[0.1.1] - 2016-11-23
--------------------

Added
*****

* Scripts for backup/restore

Changed
*******

* Force CLI to return JSONs even on errors
* Do not block collecting of Ceph facts on broken ceph command
* Support of hyphenated interface naming
* Enable monitors on host restart
* Enable RGWs on host restart



--------------------
[0.1.0] - 2016-11-03
--------------------

Initial MVP release
