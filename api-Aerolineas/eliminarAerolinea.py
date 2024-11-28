import boto3
import json
import logging
import os


# Configuración de DynamoDB
dynamodb = boto3.client('dynamodb')
lambda_client = boto3.client('lambda')
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

    # Inicio - Validación del token
    token = event['headers'].get('Authorization', '').split(' ')[1] if 'Authorization' in event['headers'] else None
    logging.info("Token recibido: %s", token)

    if not token:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Token no proporcionado'})
        }

    # Invocar el Lambda de Python para validar el token
    try:
        logging.info("Payload enviado al servicio de validación: %s", json.dumps({'token': token}))
        
        validation_response = lambda_client.invoke(
            FunctionName='servicio-vuelos-aero-dev-validarToken',  # Nombre del Lambda Python
            Payload=json.dumps({'body': json.dumps({'token': token})})  # Pasamos el token en el evento
        )
        
        logging.info("Respuesta de validación del token: %s", validation_response['Payload'].read().decode())
    except Exception as error:
        logging.error("Error al invocar la función Lambda de validación: %s", error)
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error al invocar la validación de token'})
        }

    # Parsear la respuesta de validación
    try:
        parsed_response = json.loads(validation_response['Payload'].read().decode())
        parsed_body = json.loads(parsed_response.get('body', '{}'))
    except Exception as error:
        logging.error("Error al parsear la respuesta de validación: %s", error)
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error al procesar la respuesta de validación'})
        }

    # Verificar si la respuesta contiene el código de estado esperado
    if parsed_response.get('statusCode') != 200:
        message = parsed_body.get('message', 'Token inválido o error en la validación')
        return {
            'statusCode': parsed_response.get('statusCode', 400),
            'body': json.dumps({'message': message})
        }

    # Fin - Validación del Token

    # Obtener tenant_id y codigo del body
    tenant_id = data.get('tenant_id')
    codigo = data.get('codigo')

    if not tenant_id or not codigo:
        logging.error("El tenant_id o codigo no están presentes en el cuerpo de la solicitud.")
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'El tenant_id y codigo son obligatorios'})
        }

    # Proceso - Eliminar la aerolínea de DynamoDB
    try:
        response = dynamodb.delete_item(
            TableName=table_name,
            Key={
                'tenant_id': {'S': tenant_id},
                'codigo': {'S': codigo}
            }
        )

        if response.get('Attributes'):
            logging.info("Aerolinea eliminada: %s", response['Attributes'])
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Aerolinea eliminada con éxito'})
            }
        else:
            logging.warning("Aerolinea no encontrada para eliminar")
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Aerolinea no encontrada'})
            }
    except Exception as error:
        logging.error("Error al eliminar la aerolínea de DynamoDB: %s", error)
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Ocurrió un error al eliminar la aerolínea'})
        }
