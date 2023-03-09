variable "aws_default_region" {
  type        = string
  description = "ap-southeast-1"
}

variable "volume_id" {
  type        = string
}

variable "device_name" {
  type        = string
  default     = "/dev/xvdc"
}

variable "instance_id" {
  type        = string
}

variable "cloud_tags" {
  description = "additional tags as a map"
  type        = map(string)
  default     = {}
}

