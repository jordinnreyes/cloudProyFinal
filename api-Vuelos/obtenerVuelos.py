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
    logging.info("Contenido del evento: %s", event)

    # Obtener el tenant_id desde los parámetros de la URL o cuerpo del evento
    tenant_id = event.get('queryStringParameters', {}).get('tenant_id', '')
    
    if not tenant_id:
        logging.error("El tenant_id es obligatorio")
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'El tenant_id es obligatorio'})
        }

    # Consultar los vuelos en DynamoDB por tenant_id
    try:
        response = dynamodb.query(
            TableName=table_name,
            IndexName="tenant_id-index",  # Suponiendo que tienes un índice secundario global por tenant_id
            KeyConditionExpression="tenant_id = :tenant_id",
            ExpressionAttributeValues={
                ":tenant_id": {'S': tenant_id}
            }
        )

        # Si no hay vuelos encontrados
        if 'Items' not in response or not response['Items']:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': f'No se encontraron vuelos para el tenant_id {tenant_id}'})
            }

        # Retornar los vuelos encontrados
        vuelos = response['Items']
        return {
            'statusCode': 200,
            'body': json.dumps({'vuelos': vuelos})
        }

    except Exception as e:
        logging.error("Error al consultar los vuelos en DynamoDB: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error al consultar los vuelos', 'error': str(e)})
        }
