variable "subnet_ids" {}

variable "region" {
  default = "us-east-1"
}

variable "name" {
  default = "docdb-default-name"
}

variable "instance_class" {
  default = "db.r4.large"
}

variable "num_count" {
  default = 1
}

variable "master_password" {
  default = "temp456pass789"
  type = string
}

variable "master_username" {
  default = "mongodb_admin"
  type = string
}

variable "backup_retention_period" {
  default = 7
  type    = number
}

variable "preferred_backup_window" {
  default = "07:00-09:00"
  type    = string
}

variable "skip_final_snapshot" {
  default = true
  type    = bool
}

variable "storage_encrypted" {
  default = true
  type    = bool
}

variable "apply_immediately" {
  default     = false
  description = "Specifies whether any cluster modifications are applied immediately, or during the next maintenance window."
  type        = bool
}

variable "ca_cert_identifier" {
  default     = "rds-ca-2019"
  description = "Optional, identifier of the CA certificate to use for DB instance"
  type        = string
}

variable "family" {
  default     = "docdb3.6"
  description = "Version of docdb family being created"
  type        = string
}

variable "engine" {
  default     = "docdb"
  description = "The name of the database engine to be used for this DB cluster. Only `docdb` is supported."
  type        = string
}

variable "engine_version" {
  default     = "3.6.0"
  description = "The database engine version. Updating this argument results in an outage."
  type        = string
}

variable "security_group_ids" {}

variable "cloud_tags" {
  description = "additional tags as a map"
  type        = map(string)
  default     = {}
}
