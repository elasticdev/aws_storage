variable "aws_default_region" {
  default = "us-east-1"
}

variable "name" {
  type        = string
  description = "Name of the supported"
}

variable "image_tag_mutability" {
  type        = string
  default     = "MUTABLE"
}

variable "image_scanning_configuration" {
  type        = map
  description = "Configuration block that defines image scanning configuration for the repository. By default, image scanning must be manually triggered. See the ECR User Guide for more information about image scanning."
  default     = {}
}

variable "tags" {
  type        = map
  description = "A map of tags to assign to the resource"
  default     = {}
}

variable "scan_on_push" {
  type        = bool
  description = "Indicates whether images are scanned after being pushed to the repository (true) or not scanned (false)"
  default     = "true"
}

variable "cloud_tags" {
  description = "additional tags as a map"
  type        = map(string)
  default     = {}
}

variable "lifecycle_policy" {
  default = <<EOF
{
    "rules": [
        {
            "rulePriority": 1,
            "description": "Keep last 15 images",
            "selection": {
                "tagStatus": "tagged",
                "tagPrefixList": ["test","dev"],
                "countNumber": 15,
                "countType": "imageCountMoreThan"
            },
            "action": {
                "type": "expire"
            }
        }
    ]
}
EOF
}

################################################
# Below doesn't work
################################################

#variable "encryption_configuration" {
#  type        = map
#  description = "Encryption configuration for the repository"
#  default     = {}
#}
#
#
#variable "encryption_type" {
#  type        = string
#  description = "The encryption type to use for the repository. Valid values are AES256 or KMS. Defaults to AES256"
#  default     = "KMS" 
#}
#
#variable "kms_key" {
#  type        = string
#  default     = ""
#}
#
