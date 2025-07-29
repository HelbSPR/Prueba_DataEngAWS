module "datalake" {
  source  = "./modules/datalake"
  project = var.project
}

module "lambda" {
  source = "./modules/lambda"

  project     = var.project
  bucket_name = module.datalake.bucket_id
}

module "glue" {
  source = "./modules/glue"

  project     = var.project
  bucket_name = module.datalake.bucket_id
}