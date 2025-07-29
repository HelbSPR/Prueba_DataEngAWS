import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from datetime import datetime
  
sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)


# Parametros
database_name = "amaris-bronze"

fecha_actual = datetime.now().strftime('%Y-%m-%d')

transacciones = glueContext.create_dynamic_frame.from_catalog(
    database=database_name, table_name="transacciones")
transacciones = transacciones.toDF()
transacciones.createOrReplaceTempView("transacciones")


ventas_por_proveedor = spark.sql("""
    SELECT fecha, nombre_cliente_proveedor as proveedor, 
      ROUND(SUM(CASE WHEN tipo_transaccion='Compra' THEN cantidad_kwh ELSE 0 END),2) AS cantidad_kwh_comprados,
      ROUND(SUM(CASE WHEN tipo_transaccion='Venta' THEN cantidad_kwh ELSE 0 END),2) AS cantidad_kwh_vendidos,
      ROUND(SUM(CASE WHEN tipo_transaccion='Compra' THEN -precio_total 
               WHEN tipo_transaccion='Venta' THEN precio_total
               ELSE 0 END),2) AS ingresos_netos
      
      FROM transacciones
      GROUP BY fecha, nombre_cliente_proveedor""")


#ventas_por_proveedor.show(50)

ventas_por_proveedor.write.mode("append") \
  .parquet("s3://amaris-datalake-14607647321122413655/silver/ventas_por_proveedor/")