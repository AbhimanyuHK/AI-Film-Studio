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
  description = "CIDR for the public-facing subnet"
  type        = string
  default     = "10.42.1.0/24"
}

variable "availability_zone" {
  description = "Availability zone for the initial foundation"
  type        = string
  default     = "us-east-1a"
}
