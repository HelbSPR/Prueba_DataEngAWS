
import os
import pandas as pd
import random
import boto3
from faker import Faker
from datetime import datetime
from io import StringIO

fake = Faker('es_CO')

# ----------- Parámetros del entorno -------------
BUCKET_NAME = os.getenv("BUCKET_NAME")
S3_PREFIX = 'bronze' 



TIPOS_ENERGIA = ['Eólica', 'Hidroeléctrica', 'Nuclear']
TIPOS_TRANSACCION = ['Compra', 'Venta']
TIPOS_IDENTIFICACION = ['CC', 'NIT', 'CE']

def generar_csvs(fecha_actual):
    NUM_PROVEEDORES = 5
    NUM_CLIENTES = 20
    NUM_TRANSACCIONES = 50

    # Proveedores
    proveedores = []
    for _ in range(NUM_PROVEEDORES):
        proveedores.append({
            'nombre_proveedor': fake.company(),
            'tipo_energia': random.choice(TIPOS_ENERGIA)
        })
    df_proveedores = pd.DataFrame(proveedores)

    # Clientes
    clientes = []
    for _ in range(NUM_CLIENTES):
        clientes.append({
            'tipo_identificacion': random.choice(TIPOS_IDENTIFICACION),
            'identificacion': fake.unique.random_number(digits=10),
            'nombre': fake.name(),
            'ciudad': fake.city()
        })
    df_clientes = pd.DataFrame(clientes)

    # Transacciones
    transacciones = []
    for _ in range(NUM_TRANSACCIONES):
        tipo_transaccion = random.choice(TIPOS_TRANSACCION)
        if tipo_transaccion == 'Compra':
            p = random.choice(proveedores)
            nombre = p['nombre_proveedor']
            tipo_energia = p['tipo_energia']
        else:
            c = random.choice(clientes)
            nombre = c['nombre']
            tipo_energia = random.choice(TIPOS_ENERGIA)

        cantidad = round(random.uniform(10, 1000), 2)
        precio = round(cantidad * random.uniform(0.1, 0.5), 2)

        transacciones.append({
            'tipo_transaccion': tipo_transaccion,
            'nombre_cliente_proveedor': nombre,
            'cantidad_kwh': cantidad,
            'precio_total': precio,
            'tipo_energia': tipo_energia,
            'fecha': fecha_actual
        })
    df_transacciones = pd.DataFrame(transacciones)

    return {
        'proveedores.csv': df_proveedores,
        'clientes.csv': df_clientes,
        'transacciones.csv': df_transacciones
    }

def subir_a_s3(df, bucket, key):
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    s3 = boto3.client('s3')
    s3.put_object(Bucket=bucket, Key=key, Body=csv_buffer.getvalue())

def lambda_handler(event, context):
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    ruta_particion = f"{S3_PREFIX}/fecha={fecha_actual}"

    archivos = generar_csvs(fecha_actual)

    for nombre_archivo, df in archivos.items():
        s3_key = f"{ruta_particion}/{nombre_archivo}"
        subir_a_s3(df, BUCKET_NAME, s3_key)

    return {
        'statusCode': 200,
        'body': f"Archivos cargados en {ruta_particion}"
    }
