output "film_bucket_name" {
  description = "Private S3 bucket for film assets"
  value       = aws_s3_bucket.film.bucket
}

output "terraform_state_bucket_name" {
  description = "Private S3 bucket reserved for this environment's Terraform state"
  value       = aws_s3_bucket.terraform_state.bucket
}

output "film_database_endpoint" {
  description = "Private RDS endpoint for the film environment"
  value       = aws_db_instance.film.address
}

output "film_jobs_queue_url" {
  description = "Encrypted SQS queue used by the film runtime"
  value       = aws_sqs_queue.film_jobs.url
}

output "film_runtime_role_arn" {
  description = "IAM role used by film runtime workloads"
  value       = aws_iam_role.runtime.arn
}
