variable "aws_default_region" {
  type        = string
  default = "us-east-2"
}

variable "ssm_type" {
  type        = string
  default     = "SecureString"
}

variable "ssm_description" {
  type        = string
  default     = "The parameter description"
}

# ssm_key is a actually a path e.g. /dev/database/mysql/password
variable "ssm_key" {
  type        = string
}

variable "ssm_value" {
  type        = string
}

variable "cloud_tags" {
  description = "additional tags as a map"
  type        = map(string)
  default     = {}
}
