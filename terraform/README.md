# Terraform

Terraform provisions the isolated AWS environment for each film.

Planned modules:
- Account/environment bootstrap
- VPC and network security
- IAM
- S3
- RDS PostgreSQL
- SQS/EventBridge
- GPU compute
- Container/application deployment
- Secrets Manager
- KMS
- CloudWatch/CloudTrail
- Route 53

The central SaaS supplies film/environment configuration and invokes the deployment workflow. Terraform state must remain isolated per deployment.
