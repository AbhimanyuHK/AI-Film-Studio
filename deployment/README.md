# Deployment Orchestrator

This directory contains the deployment entry point for isolated film environments.

## Deployment flow

```text
central SaaS film record
        ↓
environment_id
        ↓
Terraform plan
        ↓
Terraform apply
        ↓
AWS film environment
        ↓
health checks
        ↓
mark environment ready
```

The orchestrator never copies film content between environments.

## Commands

From the repository root:

```bash
pip install -e deployment
film-deploy plan --film-id film-001 --environment-id env-001
film-deploy apply --film-id film-001 --environment-id env-001
```

Use `--auto-approve` only in a controlled CI/CD workflow after a reviewed plan.

Destroy is intentionally explicit:

```bash
film-deploy destroy --film-id film-001 --environment-id env-001
```

## AWS prerequisites

- AWS credentials configured for the deployment account.
- Terraform >= 1.8.
- An isolated AWS account or delegated environment for production films.
- Service quotas approved for RDS, GPU compute and networking.
- CI role with least-privilege Terraform permissions.
- Remote Terraform state with locking for production deployments.

## Production gate

The deployment is not considered ready until CI has successfully executed:

1. `terraform fmt -check`
2. `terraform init`
3. `terraform validate`
4. `terraform plan`
5. application image builds
6. database migration checks
7. service health checks
8. worker queue smoke test
9. film-scope isolation test
10. artifact upload/download test

Secrets must be supplied by AWS Secrets Manager or the CI secret store. They must never be committed to this repository.
