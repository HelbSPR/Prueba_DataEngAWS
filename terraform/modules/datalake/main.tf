resource "random_id" "bucket_suffix" {
  byte_length = 8
}

resource "aws_s3_bucket" "datalake_bucket" {
  bucket = "${var.project}-datalake-${random_id.bucket_suffix.dec}"
}

locals {
  layer = ["bronze/", "silver/", "gold/"]
}

resource "aws_s3_object" "datalake_folders" {
  for_each = toset(local.layer)
  bucket   = aws_s3_bucket.datalake_bucket.id
  key      = each.value
  content  = "" # crea un objeto de 0 bytes
}
