#!/bin/bash
set -e
cd ./scripts/lambda_layers/
rm -rf python faker_layer.zip
rm -rf layer_hash.json 
pip install -r requirements.txt -t python -q
zip -r -q faker_layer.zip python
echo "✅ Capa lista: faker_layer.zip"
HASH=$(openssl dgst -sha256 -binary faker_layer.zip | openssl base64)
echo "{\"hash\": \"${HASH}\"}" > layer_hash.json

