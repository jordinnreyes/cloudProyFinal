import boto3
import json
import logging
import os

# Configuración de DynamoDB
dynamodb = boto3.client('dynamodb')
table_name = os.environ['VUELOS_TABLE']
gsi_name = "DestinoOrigenIndex"

# Configuración del logging
logging.basicConfig(level=logging.INFO)

def lambda_handler(event, context):
    logging.info("Contenido del evento: %s", event)

    # Parsear el cuerpo de la solicitud
    body = event.get("body", None)
    if not body:
        logging.error("El cuerpo del JSON está vacío")
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'El cuerpo del JSON está vacío'})
        }

    try:
        body = json.loads(body) if isinstance(body, str) else body
    except json.JSONDecodeError as e:
        logging.error("Error de decodificación JSON: %s", str(e))
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Error de decodificación JSON'})
        }

    destino = body.get('destino')
    origen = body.get('origen')

    if not destino or not origen:
        logging.error("Destino y origen son obligatorios")
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Destino y origen son obligatorios'})
        }

    # Consultar DynamoDB usando el GSI
    try:
        response = dynamodb.query(
            TableName=table_name,
            IndexName=gsi_name,  # Nombre del índice secundario global
            KeyConditionExpression="destino = :destino AND origen = :origen",
            ExpressionAttributeValues={
                ":destino": {'S': destino},
                ":origen": {'S': origen}
            }
        )

        # Recuperar los elementos
        items = response.get('Items', [])
        if not items:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': f'No se encontraron vuelos para el tenant_id {tenant_id}'})
            }

        # Retornar los vuelos encontrados
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Vuelos encontrados',
                'vuelos': items
            })
        }

    except Exception as e:
        logging.error("Error al consultar DynamoDB: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error al consultar DynamoDB', 'error': str(e)})
        }
