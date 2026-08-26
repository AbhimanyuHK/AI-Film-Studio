Backend
=======

Responsibilities
----------------

The backend is the platform control plane. It provides authentication, authorization, client and film management, environment management, job creation, job status, and integration boundaries.

The backend should remain responsive. Long-running generation is delegated to workers.

Job lifecycle
-------------

Typical states are:

::

    queued -> running -> completed
                    \-> failed
                    \-> cancelled

Workers use leases so interrupted workers do not leave jobs permanently stuck.

Authentication
--------------

Production authentication is configured through external environment variables. Use a strong random JWT secret and HTTPS in production.

Service-to-service authentication should use dedicated internal credentials rather than exposing internal endpoints without authentication.

API contract
------------

The backend is the public API boundary. Internal AI Engine and Film Runtime endpoints should not be exposed directly to the public internet unless there is an explicit security reason and corresponding authentication policy.
