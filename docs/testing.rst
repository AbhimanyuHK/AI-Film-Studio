Testing
=======

Test levels
-----------

Unit tests validate individual modules. Integration tests validate service boundaries and database behavior. End-to-end tests validate the complete production job path.

CI
--

CI should validate:

* backend tests;
* AI Engine tests;
* Film Runtime tests;
* worker checks;
* frontend build;
* Docker image builds;
* Terraform formatting and validation;
* complete-stack smoke tests where infrastructure permits.

End-to-end scenario
-------------------

The minimum happy-path scenario is:

::

    create client
      -> create film
      -> create environment
      -> create production job
      -> worker claims job
      -> AI Engine executes
      -> artifact/result recorded
      -> job completed

Negative tests
--------------

Also test:

* invalid authentication;
* unauthorized film access;
* cross-film scope mismatch;
* duplicate job submission;
* worker crash and stale lease;
* retry exhaustion;
* AI provider timeout;
* unsupported model;
* cancellation;
* missing artifact;
* database outage.

Load testing
------------

Run the repository's deployment load test against a staging environment. Validate queue behavior and job completion rather than only measuring HTTP throughput.
