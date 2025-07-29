import boto3
import time

athena = boto3.client('athena', region_name='us-east-1') 

database = 'amaris-silver'
query = "SELECT * FROM silver WHERE fecha = '2025-07-27'"
output = 's3://amaris-datalake-14607647321122413655/gold/'

response = athena.start_query_execution(
    QueryString=query,
    QueryExecutionContext={'Database': database},
    ResultConfiguration={'OutputLocation': output}
)

query_id = response['QueryExecutionId']
while True:
    result = athena.get_query_execution(QueryExecutionId=query_id)
    state = result['QueryExecution']['Status']['State']
    if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
        break
    time.sleep(2)


if state == 'SUCCEEDED':
    print(f"Query succeeded! Results in: {output}{query_id}.csv")
else:
    print(f"Query failed with status: {state}")
