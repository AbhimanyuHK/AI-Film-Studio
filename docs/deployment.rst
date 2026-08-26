Deployment
==========

Deployment stages
-----------------

Use separate environments for development, staging, and production.

::

    development -> staging -> production

Local deployment
----------------

Use Docker Compose for local integration testing. Do not treat local credentials or localhost networking as production configuration.

AWS deployment
--------------

Infrastructure is defined under ``terraform/`` and deployment automation is under ``deployment/`` and ``.github/workflows/``.

Recommended flow:

::

    terraform fmt
    terraform init
    terraform validate
    terraform plan
    terraform apply

GitHub Actions
--------------

The deployment workflows are designed to authenticate to AWS using GitHub OIDC and an AWS IAM deployment role rather than long-lived AWS access keys stored in GitHub.

Staging should be deployable automatically after validation. Production should remain protected by a GitHub Environment approval gate.

Pre-deployment checklist
------------------------

* AWS account and region selected.
* Terraform state backend configured.
* GitHub OIDC trust configured.
* Deployment IAM role follows least privilege.
* Production secrets exist in AWS Secrets Manager/SSM.
* Database backup policy enabled.
* S3 encryption and lifecycle policy enabled.
* DNS and ACM certificate configured.
* WAF policy reviewed.
* AI provider/GPU capacity validated.
* End-to-end smoke test passes.

Rollback
--------

Keep application images versioned by immutable commit SHA. Roll back the application image first when appropriate, then revert infrastructure changes through Terraform deliberately. Database migrations require backward-compatible planning because application rollback cannot safely undo an already-applied schema migration in general.
