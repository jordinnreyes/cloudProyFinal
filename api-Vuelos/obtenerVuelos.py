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

    # Bloque 1: Verificar si el cuerpo está vacío
    body = event.get("body", None)
    if not body:
        logging.error("El cuerpo del JSON está vacío")
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'El cuerpo del JSON está vacío'})
        }

    # Bloque 2: Intentar parsear el cuerpo
    if isinstance(body, str):  # Si es un string, cargarlo como JSON
        try:
            body = json.loads(body)
        except json.JSONDecodeError as e:
            logging.error("Error de decodificación JSON: %s", str(e))
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Error de decodificación JSON'})
            }
    elif not isinstance(body, dict):  # Validar formato
        logging.error("Formato de cuerpo no válido: %s", type(body))
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Formato del cuerpo no válido'})
        }

    logging.info("JSON parseado correctamente: %s", body)
    data = body  # Renombrar para consistencia

    # Obtener el tenant_id del cuerpo
    tenant_id = data.get('tenant_id', None)
    logging.info(f"tenant_id recibido: {tenant_id}")

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
        # Deserializar los resultados de DynamoDB para facilitar la lectura
        vuelos_deserializados = [
            {k: list(v.values())[0] for k, v in vuelo.items()} for vuelo in vuelos
        ]
        return {
            'statusCode': 200,
            'body': json.dumps({'vuelos': vuelos_deserializados})
        }

    except Exception as e:
        logging.error("Error al consultar los vuelos en DynamoDB: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error al consultar los vuelos', 'error': str(e)})
        }
