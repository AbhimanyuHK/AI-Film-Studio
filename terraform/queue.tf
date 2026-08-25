resource "aws_sqs_queue" "film_jobs_dlq" {
  name = "${var.name_prefix}-${var.film_id}-jobs-dlq"
  kms_master_key_id = aws_kms_key.film.arn
}

resource "aws_sqs_queue" "film_jobs" {
  name = "${var.name_prefix}-${var.film_id}-jobs"
  visibility_timeout_seconds = 900
  message_retention_seconds = 1209600
  receive_wait_time_seconds = 20
  kms_master_key_id = aws_kms_key.film.arn
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.film_jobs_dlq.arn
    maxReceiveCount = 3
  })
}

resource "aws_iam_policy" "runtime_queue" {
  name = "${var.name_prefix}-${var.film_id}-queue"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:ChangeMessageVisibility", "sqs:GetQueueAttributes"]
      Resource = aws_sqs_queue.film_jobs.arn
    }]
  })
}

resource "aws_iam_role_policy_attachment" "runtime_queue" {
  role = aws_iam_role.runtime.name
  policy_arn = aws_iam_policy.runtime_queue.arn
}
