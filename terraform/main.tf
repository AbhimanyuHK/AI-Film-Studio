terraform {
  required_version = ">= 1.8.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "AI-Film-Studio"
      FilmID      = var.film_id
      Environment = var.environment_id
      ManagedBy   = "terraform"
    }
  }
}

resource "aws_s3_bucket" "film" {
  bucket = "${var.name_prefix}-film-${var.film_id}"
}

resource "aws_s3_bucket_public_access_block" "film" {
  bucket = aws_s3_bucket.film.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "film" {
  bucket = aws_s3_bucket.film.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "film" {
  bucket = aws_s3_bucket.film.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket" "terraform_state" {
  bucket = "${var.name_prefix}-tfstate-${var.film_id}"
}

resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
