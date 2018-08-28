=============
Release Notes
=============

This is the summary list of changes to Girder Worker between each release. For full
details, see the commit logs at https://github.com/girder/girder_worker_utils

Unreleased
==========

Added Features
--------------

Bug fixes
---------

Changes
-------

Deprecations
------------

DevOps
------

Removals
--------

Security Fixes
--------------

0.8.4
=====

Added Features
--------------

* Added a new transform for uploading files to Girder jobs as artifacts.
  `#26 <https://github.com/girder/girder_worker_utils/pull/26>`_.
* Added a new hook to ResultTransforms to allow an action to be taken if an
  exception occurred during the task.
  `#27 <https://github.com/girder/girder_worker_utils/pull/27>`_.
