resource "aws_security_group" "rds" {
  name        = "${var.name_prefix}-${var.film_id}-rds"
  description = "Film-isolated PostgreSQL access"
  vpc_id      = aws_vpc.film.id

  ingress {
    description = "PostgreSQL from film VPC"
    protocol    = "tcp"
    from_port   = 5432
    to_port     = 5432
    cidr_blocks = [var.vpc_cidr]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}
