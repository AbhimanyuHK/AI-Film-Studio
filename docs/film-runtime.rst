Film Runtime
============

Purpose
-------

Film Runtime is the isolated execution boundary for a film environment. It keeps film-specific context and artifact access separate from the platform control plane.

Scope
-----

A runtime is configured for a client, film, and environment. Requests must match that scope. Cross-film requests must be rejected before invoking AI generation.

Responsibilities
---------------

* film-scoped configuration;
* film context and knowledge access;
* artifact storage integration;
* runtime job execution boundary;
* AI Engine invocation;
* film-level isolation controls.

Not responsible for
-------------------

Film Runtime is not the model provider layer. It should not duplicate the AI Engine's provider adapters or model execution implementation.

Deployment
----------

Film environments can be provisioned using the deployment/Terraform tooling. Each environment should have explicit configuration and credentials scoped to the resources it is allowed to access.
