variable "aws_region" {
  description = "AWS region for the isolated film environment"
  type        = string
  default     = "us-east-1"
}

variable "film_id" {
  description = "Immutable film identifier"
  type        = string
  validation {
    condition     = can(regex("^[a-z0-9-]{3,40}$", var.film_id))
    error_message = "film_id must contain 3-40 lowercase letters, numbers, or hyphens."
  }
}

variable "environment_id" {
  description = "Immutable film environment identifier"
  type        = string
  validation {
    condition     = can(regex("^[a-z0-9-]{3,40}$", var.environment_id))
    error_message = "environment_id must contain 3-40 lowercase letters, numbers, or hyphens."
  }
}

variable "name_prefix" {
  description = "Short resource naming prefix"
  type        = string
  default     = "aifilm"
}

variable "vpc_cidr" {
  description = "CIDR range for the isolated film VPC"
  type        = string
  default     = "10.42.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR for the public subnet"
  type        = string
  default     = "10.42.1.0/24"
}

variable "private_subnet_a_cidr" {
  description = "CIDR for private database subnet A"
  type        = string
  default     = "10.42.11.0/24"
}

variable "private_subnet_b_cidr" {
  description = "CIDR for private database subnet B"
  type        = string
  default     = "10.42.12.0/24"
}

variable "availability_zone" {
  description = "Primary availability zone"
  type        = string
  default     = "us-east-1a"
}

variable "secondary_availability_zone" {
  description = "Secondary availability zone"
  type        = string
  default     = "us-east-1b"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.micro"
}

variable "db_allocated_storage" {
  description = "Initial RDS storage in GiB"
  type        = number
  default     = 20
}

variable "db_username" {
  description = "RDS master username"
  type        = string
  default     = "filmstudio"
}

variable "db_deletion_protection" {
  description = "Prevent accidental database deletion"
  type        = bool
  default     = true
}
