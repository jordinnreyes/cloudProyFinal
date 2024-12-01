import boto3
import json
import logging
import os

# Configuración de DynamoDB
dynamodb = boto3.client('dynamodb')
table_name = os.environ['VUELOS_TABLE']

# Configuración del logging
logging.basicConfig(level=logging.INFO)

def format_vuelo(vuelo):
    """
    Función para formatear los vuelos, desestructurando el formato de DynamoDB
    y convirtiendo las claves y valores a un formato más comprensible.
    """
    return {
        'codigo': vuelo.get('codigo', {}).get('S'),
        'origen': vuelo.get('origen', {}).get('S'),
        'destino': vuelo.get('destino', {}).get('S'),
        'fecha_salida': vuelo.get('fecha_salida', {}).get('S'),
        'fecha_llegada': vuelo.get('fecha_llegada', {}).get('S'),
        'capacidad': vuelo.get('capacidad', {}).get('N'),
        'tenant_id': vuelo.get('tenant_id', {}).get('S'),
        'id_vuelo': vuelo.get('id_vuelo', {}).get('S')
    }

def lambda_handler(event, context):
    logging.info("Iniciando Lambda para obtener todos los vuelos")

    try:
        # Consultar todos los vuelos en DynamoDB
        response = dynamodb.scan(
            TableName=table_name
        )
        
        # Recuperar los elementos
        items = response.get('Items', [])
        
        if not items:
            logging.info("No se encontraron vuelos en la tabla")
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'No se encontraron vuelos'})
            }

        # Formatear los vuelos para hacerlos más legibles
        vuelos_formateados = [format_vuelo(vuelo) for vuelo in items]
        
        # Retornar los vuelos de manera estructurada
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Vuelos encontrados',
                'vuelos': vuelos_formateados
            })
        }

    except Exception as error:
        logging.error("Error al consultar los vuelos en DynamoDB: %s", error)
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error al obtener los vuelos'})
        }
