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
    Función para formatear un vuelo de DynamoDB a un formato más legible.
    """
    return {key: value.get('S') if isinstance(value, dict) and 'S' in value else value.get('N') if isinstance(value, dict) and 'N' in value else value for key, value in vuelo.items()}


def lambda_handler(event, context):
    logging.info("Evento recibido: %s", event)

    # Obtener tenant_id de los parámetros de la solicitud
    tenant_id = event.get('pathParameters', {}).get('tenant_id', None)
    if not tenant_id:
        logging.error("El tenant_id no está presente en los parámetros de la solicitud.")
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'El tenant_id es obligatorio'})
        }

    try:
        # Consultar los vuelos por tenant_id en DynamoDB
        response = dynamodb.query(
            TableName=table_name,
            IndexName='tenant_id-index',  # Nombre del índice secundario global, si aplica
            KeyConditionExpression='tenant_id = :tenant_id',
            ExpressionAttributeValues={
                ':tenant_id': {'S': tenant_id}
            }
        )

        # Recuperar los elementos
        items = response.get('Items', [])
        if not items:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': f'No se encontraron vuelos para el tenant_id: {tenant_id}'})
            }

        # Convertir los vuelos a un formato legible
        vuelos = [format_vuelo(item) for item in items]

        # Retornar los vuelos encontrados
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Vuelos encontrados',
                'vuelos': vuelos
            })
        }

    except Exception as error:
        logging.error("Error al consultar los vuelos en DynamoDB: %s", error)
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error al obtener los vuelos', 'error': str(error)})
        }
