# Deployment Orchestrator

This directory contains the deployment entry point and production-readiness checks for isolated film environments.

## Deployment flow

```text
central SaaS film record
        ↓
environment_id
        ↓
Terraform format / validate / plan
        ↓
Terraform apply
        ↓
AWS film environment
        ↓
database migrations 001 → 004
        ↓
service deployment
        ↓
health checks
        ↓
queue smoke test
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

## End-to-end smoke test

After the local stack is running:

```bash
python deployment/smoke_test.py
```

The smoke test creates a client, film, isolated environment and one production job, then waits for the worker to execute it through the configured AI integration executor.

The local executor is intentionally deterministic and metadata-only. It verifies the control-plane/worker/AI transport path but does not pretend to generate production media.

## AWS prerequisites

- AWS credentials configured for the deployment account.
- Terraform >= 1.8.
- An isolated AWS account or delegated environment for production films.
- Service quotas approved for RDS, GPU compute and networking.
- CI role with least-privilege Terraform permissions.
- Remote Terraform state with locking for production deployments.
- Private networking between application, worker, runtime and database services.
- AWS Secrets Manager/SSM for credentials and service-to-service secrets.
- GPU capacity and model licenses for the selected production AI providers.

## Production configuration

Use `production.env.example` as the configuration contract. Never commit real values.

Production authentication uses JWT and requires `JWT_SECRET` of at least 32 characters. The current built-in verifier supports HS256; if an enterprise OIDC/JWKS provider is required, replace the verifier with the organization's identity integration before public launch.

The deterministic `ai_engine.integration_executor` is for local/CI validation only. Production must configure `AI_EXECUTOR_FACTORY` to a real provider-backed executor with the required model weights, credentials and GPU runtime.

## CI production-readiness gates

The repository CI now checks:

1. Backend tests.
2. AI Engine tests.
3. Film Runtime tests.
4. Worker compilation.
5. Frontend build.
6. Docker Compose configuration.
7. Terraform format.
8. Terraform initialization and validation.
9. All application container builds.
10. Complete local-stack startup.
11. End-to-end job submission and worker execution.
12. Service diagnostics on failure.

A successful CI run proves repository-level integration. It does not create AWS resources or prove production GPU/provider behavior.

## Deployment gate

A production release requires all repository CI checks plus:

- reviewed Terraform plan
- real AWS secrets
- real model/provider executor
- GPU capacity
- production database backup/restore verification
- TLS/domain/WAF configuration
- monitoring and alerting
- film/client isolation verification against the deployed environment
- artifact upload/download verification against production S3

Secrets must never be committed to this repository.
