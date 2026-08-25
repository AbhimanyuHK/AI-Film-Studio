# Deployment Orchestrator

The deployment layer turns a film record into an isolated production environment.

Flow:

1. Create film in central SaaS.
2. Allocate environment identity.
3. Provision/delegate AWS account.
4. Apply Terraform.
5. Deploy film runtime.
6. Configure DNS/subdomain.
7. Run health checks.
8. Mark environment ready.

The orchestrator controls infrastructure lifecycle; it does not move film content between environments.
