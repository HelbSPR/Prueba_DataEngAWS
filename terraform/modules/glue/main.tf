locals {
  layers = ["bronze","silver","gold"]
}

resource "aws_glue_catalog_database" "database" {
  for_each = toset(local.layers)
  name        = "${var.project}-${each.value}"
  description = "Database para capa ${each.value}"
}

resource "aws_glue_crawler" "crawler" {

  for_each = toset(local.layers)

  name          = "${var.project}-${each.value}-crawler"
  database_name = aws_glue_catalog_database.database[each.value].name
  role          = aws_iam_role.glue_role.arn

  s3_target {
    path = "s3://${var.bucket_name}/${each.value}"
  }

  recrawl_policy {
    recrawl_behavior = "CRAWL_NEW_FOLDERS_ONLY"
  }

  schema_change_policy {
    delete_behavior = "LOG"
    update_behavior = "LOG"
  }
}

