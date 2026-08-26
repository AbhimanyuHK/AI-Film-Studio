Security
========

Authentication
--------------

Use strong, rotated production JWT secrets and HTTPS. Internal service calls should use dedicated service credentials.

Authorization
-------------

Authorization must be checked at the backend control plane and reinforced at film-scoped runtime boundaries. A valid user token does not automatically grant access to every film.

Secrets
-------

Never commit:

* API keys;
* database passwords;
* JWT signing secrets;
* AWS access keys;
* internal service tokens.

Use a secret manager and inject values at runtime.

Network security
----------------

Only the required public endpoints should be internet reachable. Database, worker, Film Runtime, and AI Engine ports should remain private unless a specific architecture requires otherwise.

AI security
-----------

Treat model output as untrusted data. Validate generated structured output, constrain model/tool access, enforce model allowlists, and avoid placing secrets in prompts or model context.

Artifact security
-----------------

Use scoped S3 keys and short-lived presigned URLs where direct browser downloads are required. Validate ownership before issuing artifact access.

Logging
-------

Use structured logs with request/job/film identifiers. Redact credentials and sensitive content.
