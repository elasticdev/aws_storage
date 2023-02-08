resource "aws_ecr_repository" "ecr_repository" {
  name                 = var.name
  image_tag_mutability = var.image_tag_mutability

  image_scanning_configuration {
    scan_on_push = var.scan_on_push
  }

  ###########################################
  # Below doesn't work
  #encryption_configuration {
  #  encryption_type = var.encryption_type
  #  kms_key         = var.kms_key
  #}
  ###########################################
}

resource "aws_ecr_lifecycle_policy" "lifecycle_policy" {
  repository = aws_ecr_repository.ecr_repository.name
  policy     = var.lifecycle_policy
}
