import boto3
import json
import logging
import os

# Configuración de DynamoDB
dynamodb = boto3.client('dynamodb')
table_name = os.environ['VUELOS_TABLE']

# Configuración del logging
logging.basicConfig(level=logging.INFO)

def lambda_handler(event, context):
    logging.info("Iniciando lambda para obtener todas las vuelos")

    # Consultar todas las vuelos en DynamoDB
    try:
        response = dynamodb.scan(
            TableName=table_name
        )
        
        # Recuperar los elementos
        items = response.get('Items', [])
        if not items:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'No se encontraron vuelos'})
            }

        # Retornar todas las vuelos encontradas
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'vuelos encontradas',
                'vuelos': items
            })
        }

    except Exception as error:
        logging.error("Error al consultar las vuelos en DynamoDB: %s", error)
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error al obtener las vuelos'})
        }