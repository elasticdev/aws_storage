variable "product" {
  type        = string
  default     = "dynamodb"
}

variable "aws_default_region" {
  type        = string
  default     = "eu-west-1"
}

variable "dynamodb_name" {}

variable "billing_mode" { 
  default     = "PAY_PER_REQUEST"
}

variable "hash_key" {
  default         = "_id"
}

variable "cloud_tags" {
  description = "additional tags as a map"
  type        = map(string)
  default     = {}
}
