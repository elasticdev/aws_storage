variable "db_name" {
  type       = string
  default    = "test"
}

variable "aws_default_region" {
  default = "us-east-1"
}

variable "rds_name" {
  type       = string
  default    = "test-rds"
}

variable "db_subnet_name" {
  type       = string
  default    = "db_subnet_name"
}

variable "master_username" {
  type       = string
  default    = "admin101"
}

variable "master_password" {
  type       = string
  default    = "password101"
}

variable "security_group_ids" {
}

variable "subnet_ids" {
}

variable "allocated_storage" {
  default    = 10
}

variable "engine" {
  default    = "mysql"
}

variable "engine_version" {
  default    = "5.7"
}

variable "instance_class" {
  default    = "db.t2.micro"
}

variable "multi_az" {
  default    = false
}

variable "storage_encrypted" {
  default    = false
}

variable "port" {
  default    = 3306
}

variable "publicly_accessible" {
  default    = false
}

variable "storage_type" {
  default    = "gp2"
}

variable "skip_final_snapshot" {
  default    = true
}

variable "allow_major_version_upgrade" {
  default    = true
}

variable "auto_minor_version_upgrade" {
  default    = true
}

variable "backup_retention_period" {
  default    = 1
}

variable "maintenance_window" {
  default    = "Mon:00:00-Mon:03:00"
}

variable "backup_window" {
  default    = "10:46-11:16"
}

variable "cloud_tags" {
  description = "additional tags as a map"
  type        = map(string)
  default     = {}
}
