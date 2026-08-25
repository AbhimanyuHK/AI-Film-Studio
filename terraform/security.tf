resource "aws_kms_key" "film" {
  description             = "KMS key for AI Film Studio film ${var.film_id}"
  deletion_window_in_days = 30
  enable_key_rotation     = true
}

resource "aws_kms_alias" "film" {
  name          = "alias/aifilm-${var.film_id}"
  target_key_id = aws_kms_key.film.key_id
}

resource "aws_iam_role" "runtime" {
  name = "${var.name_prefix}-${var.film_id}-runtime"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_policy" "runtime_film_storage" {
  name = "${var.name_prefix}-${var.film_id}-storage"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ]
      Resource = [
        aws_s3_bucket.film.arn,
        "${aws_s3_bucket.film.arn}/*"
      ]
    }]
  })
}

resource "aws_iam_role_policy_attachment" "runtime_storage" {
  role       = aws_iam_role.runtime.name
  policy_arn = aws_iam_policy.runtime_film_storage.arn
}
