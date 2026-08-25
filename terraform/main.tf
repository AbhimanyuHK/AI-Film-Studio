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

resource "aws_vpc" "film" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
}

resource "aws_internet_gateway" "film" {
  vpc_id = aws_vpc.film.id
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.film.id
  cidr_block              = var.public_subnet_cidr
  availability_zone       = var.availability_zone
  map_public_ip_on_launch = false
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.film.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.film.id
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}
