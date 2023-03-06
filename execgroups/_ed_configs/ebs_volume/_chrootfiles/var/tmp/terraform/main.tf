resource "aws_ebs_volume" "data-vol" {

 availability_zone = var.availability_zone
 size = var.volume_size
 encrypted = true

 tags = merge(
   var.cloud_tags,
   {
     Name = var.volume_name
     Product = "ebs"
   },
 )
 type = var.volume_type
}



