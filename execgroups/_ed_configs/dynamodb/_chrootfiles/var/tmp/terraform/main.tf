resource "aws_dynamodb_table" "run_id_workers" {
  name             = var.dynamodb_name
  billing_mode     = var.billing_mode
  hash_key         = var.hash_key

  attribute {
    name = var.hash_key
    type = "S"
  }

  ttl {
    attribute_name = "expire_at"
    enabled        = true
  }

  tags = merge(
    var.cloud_tags,
    {
      Product = var.product
    },
  )
}
