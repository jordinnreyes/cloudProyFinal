import boto3
import json
import logging
import os


# Configuración de DynamoDB
dynamodb = boto3.client('dynamodb')
table_name = os.environ['AEROLINEAS_TABLE']

# Configuración del logging
logging.basicConfig(level=logging.INFO)


def lambda_handler(event, context):
    print(event)

    logging.info("Contenido de event.body: %s", event.get('body', ''))

    # Intentamos parsear el cuerpo de la solicitud (si es necesario)
    try:
        data = json.loads(event['body']) if event.get('body') else {}
    except Exception as error:
        logging.error("Error al parsear event.body: %s", error)
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Body no es un JSON válido'})
        }
    
    # Aquí no hacemos validación de token, solo obtendremos la lista de aerolíneas

    # Si deseas obtener aerolíneas por algún parámetro, como tenant_id, lo puedes hacer
    tenant_id = event.get('pathParameters', {}).get('tenant_id', None)
    if not tenant_id:
        logging.error("El tenant_id no está presente en los parámetros de la solicitud.")
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'El tenant_id es obligatorio'})
        }

    # Consultar las aerolíneas en DynamoDB
    try:
        response = dynamodb.query(
            TableName=table_name,
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
                'body': json.dumps({'message': 'No se encontraron aerolíneas para este tenant_id'})
            }

        # Retornar las aerolíneas encontradas
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Aerolineas encontradas',
                'aerolineas': items
            })
        }

    except Exception as error:
        logging.error("Error al consultar las aerolíneas en DynamoDB: %s", error)
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error al obtener las aerolíneas'})
        }
