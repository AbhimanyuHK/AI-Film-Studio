resource "aws_db_subnet_group" "film" {
  name       = "${var.name_prefix}-${var.film_id}"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]
}

resource "aws_db_instance" "film" {
  identifier                  = "${var.name_prefix}-${var.film_id}"
  engine                      = "postgres"
  engine_version              = "16"
  instance_class              = var.db_instance_class
  allocated_storage           = var.db_allocated_storage
  db_name                     = "filmstudio"
  username                    = var.db_username
  manage_master_user_password = true
  db_subnet_group_name        = aws_db_subnet_group.film.name
  publicly_accessible         = false
  storage_encrypted           = true
  kms_key_id                  = aws_kms_key.film.arn
  backup_retention_period     = 7
  deletion_protection         = var.db_deletion_protection
  skip_final_snapshot         = false
  final_snapshot_identifier   = "${var.name_prefix}-${var.film_id}-final"
  vpc_security_group_ids      = [aws_security_group.rds.id]
}

resource "aws_subnet" "private_a" {
  vpc_id            = aws_vpc.film.id
  cidr_block        = var.private_subnet_a_cidr
  availability_zone = var.availability_zone
}

resource "aws_subnet" "private_b" {
  vpc_id            = aws_vpc.film.id
  cidr_block        = var.private_subnet_b_cidr
  availability_zone = var.secondary_availability_zone
}
