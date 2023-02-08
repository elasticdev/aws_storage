variable "aws_default_region" {
  type        = string
  description = "ap-southeast-1"
}

variable "availability_zone" {
  type        = string
  description = "availability_zone"
}

variable "volume_size" {
  default     = 10
}

variable "volume_name" {
  type        = string
  default     = "data"
}

variable "volume_type" {
  type        = string
  default     = "gp2"
}

variable "cloud_tags" {
  description = "additional tags as a map"
  type        = map(string)
  default     = {}
}
