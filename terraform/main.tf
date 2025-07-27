module "datalake" {
  source  = "./modules/datalake"
  project = var.project
}

module "lambda" {
  source = "./modules/lambda"

  project     = var.project
  bucket_name = module.datalake.bucket_id
}
