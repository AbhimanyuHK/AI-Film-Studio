output "film_bucket_name" {
  description = "Private S3 bucket for film assets"
  value       = aws_s3_bucket.film.bucket
}

output "terraform_state_bucket_name" {
  description = "Private S3 bucket reserved for this environment's Terraform state"
  value       = aws_s3_bucket.terraform_state.bucket
}
