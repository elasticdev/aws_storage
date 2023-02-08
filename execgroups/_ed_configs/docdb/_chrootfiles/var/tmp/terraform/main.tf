resource "aws_docdb_subnet_group" "service" {
  name       = "docdb-${var.name}"
  subnet_ids = var.subnet_ids
  #subnet_ids = ["${module.vpc.private_subnets}"]
}

resource "aws_docdb_cluster_instance" "service" {
  count              = var.num_count
  identifier         = "${var.name}-${count.index}"
  cluster_identifier = aws_docdb_cluster.service.id
  instance_class     = var.instance_class
  ca_cert_identifier = var.ca_cert_identifier
}

resource "aws_docdb_cluster" "service" {
  db_subnet_group_name            = aws_docdb_subnet_group.service.name
  cluster_identifier_prefix       = var.name
  engine                          = var.engine
  engine_version                  = var.engine_version
  master_username                 = var.master_username
  master_password                 = var.master_password
  db_cluster_parameter_group_name = aws_docdb_cluster_parameter_group.service.name
  vpc_security_group_ids          = var.security_group_ids
  storage_encrypted               = var.storage_encrypted
  skip_final_snapshot             = var.skip_final_snapshot
  apply_immediately               = var.apply_immediately
  backup_retention_period = var.backup_retention_period
  preferred_backup_window = var.preferred_backup_window
}

resource "aws_docdb_cluster_parameter_group" "service" {
  family = var.family
  name = var.name

  parameter {
    name  = "tls"
    value = "disabled"
  }
}
