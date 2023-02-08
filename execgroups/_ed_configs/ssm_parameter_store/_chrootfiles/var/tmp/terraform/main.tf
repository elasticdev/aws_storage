resource "aws_ssm_parameter" "secret" {
  name        = var.ssm_key
  description = var.ssm_description
  type        = var.ssm_type
  value       = var.ssm_value

  # tags = {
  #   environment = "production"
  # }

}
