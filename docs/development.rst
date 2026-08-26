Development
===========

Repository workflow
-------------------

Use focused changes and keep service boundaries intact. Do not duplicate AI provider logic between workers, Film Runtime, and AI Engine.

Recommended workflow
--------------------

1. Create a feature branch.
2. Implement the smallest service-local change.
3. Add or update tests.
4. Run the relevant service tests.
5. Run the complete local/CI checks.
6. Review security and configuration changes.
7. Open a pull request.

Code ownership boundaries
-------------------------

* API behavior belongs in ``backend/``.
* Job execution belongs in ``workers/``.
* Film scope belongs in ``film-runtime/``.
* AI provider/model execution belongs in ``ai-engine/``.
* Infrastructure belongs in ``terraform/``.
* Deployment automation belongs in ``deployment/``.
* Documentation belongs in ``docs/``.

Configuration changes
---------------------

When adding a new environment variable, update the relevant ``.env.example`` and this documentation. Never add a production secret to an example file.

Database changes
----------------

Add a new numbered migration rather than modifying an already-applied migration. Update ORM models and tests together.
