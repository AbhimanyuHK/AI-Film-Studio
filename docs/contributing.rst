Contributing
============

Before submitting changes
-------------------------

* keep secrets out of Git;
* update tests for behavior changes;
* update documentation for public configuration or API changes;
* preserve client/film/environment isolation;
* avoid coupling UI code directly to AI providers;
* verify migrations are forward-safe.

Pull requests
-------------

A pull request should explain the change, affected components, configuration changes, migration requirements, and how it was tested.

Release readiness
-----------------

Before release, CI must pass and the deployment plan should be reviewed. Production changes that require AWS resources, provider credentials, DNS, or secrets must be explicitly validated in the target environment.
