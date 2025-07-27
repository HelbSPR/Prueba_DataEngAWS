resource "null_resource" "build_layer" {
  provisioner "local-exec" {
    #command = "${path.root}/scripts/lambda_layers/setup_layer.sh"
    command = "echo 'Omitiendo el script que crea la lambda layer'"
  }
}

data "external" "layer_hash" {
  depends_on = [null_resource.build_layer]
  program    = ["cat", "${path.root}/scripts/lambda_layers/layer_hash.json"]
}

resource "aws_lambda_layer_version" "faker_layer" {
  depends_on = [null_resource.build_layer]

  layer_name          = "faker-layer"
  filename            = "${path.root}/scripts/lambda_layers/faker_layer.zip"
  source_code_hash    = data.external.layer_hash.result["hash"]
  compatible_runtimes = ["python3.10"]
  description         = "Faker Layer"
}


data "archive_file" "dummy_data_lambda" {
  type        = "zip"
  source_file = "${path.root}/scripts/dummy_data_lambda/main.py"
  output_path = "${path.root}/scripts/dummy_data_lambda/lambda.zip"
}

resource "aws_lambda_function" "dummy_data_lambda" {
  function_name = "${var.project}-dummy_data-lambda"
  description   = "Lambda function para crear datasets dummy y guardarlos en la capa bronze."

  layers = [
    "arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python310:25",
    aws_lambda_layer_version.faker_layer.arn
  ]
  runtime = "python3.10"
  handler = "main.lambda_handler"
  role    = aws_iam_role.dummy_data_lambda_role.arn

  package_type = "Zip"
  filename     = data.archive_file.dummy_data_lambda.output_path

  memory_size = 128
  ephemeral_storage {
    size = 512
  }
  timeout = 300


  environment {
    variables = {
      BUCKET_NAME = var.bucket_name
    }
  }

}
