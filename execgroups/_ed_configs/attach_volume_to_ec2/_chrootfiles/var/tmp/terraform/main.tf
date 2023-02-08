resource "aws_volume_attachment" "data-vol-attachment" {
 device_name  = var.device_name
 volume_id    = var.volume_id
 instance_id  = var.instance_id
 force_detach = true
}
