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

     # **Inicio de manejo del cuerpo del evento**
    logging.info("Contenido de event.body: %s", event.get('body', ''))
     # Bloque 1: Verificar si el cuerpo está vacío y parsearlo
    body = event.get("body", "")
    if not body:
        logging.error("El cuerpo del JSON está vacío")
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'El cuerpo del JSON está vacío'})
        }

    # Intentamos parsear el cuerpo de la solicitud
    try:
        data = json.loads(body)
        logging.info("JSON parseado correctamente: %s", data)
    except json.JSONDecodeError as e:
        logging.error("Error de decodificación JSON: %s", str(e))
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Error de decodificación JSON'})
        }
    
     # Inicio - Proteger el Lambda con la validación del token
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


    # Fin - Proteger el Lambda  - El token ha sido validado


    # Obtener tenant_id desde el payload (si está disponible)
    tenant_id = data.get('tenant_id')
    if not tenant_id:
        logging.error("El tenant_id no está presente en el cuerpo de la solicitud.")
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'El tenant_id es obligatorio'})
        }


    # Proceso - Guardar la reseña en DynamoDB
    try:
        item = {
            'tenant_id': {'S': tenant_id},#  Tenant_id como parte de la clave primaria
            'codigo': {'S': data.get('codigo')},  # Aerolínea identificada por 'codigo'
            'nombre': {'S': data.get('nombre')},
            'pais_origen': {'S': data.get('pais_origen')}
        }

        # Guardar la aerolínea en DynamoDB
        dynamodb.put_item(
            TableName=table_name,
            Item=item
        )

        return {
            'statusCode': 201,
            'body': json.dumps({
                'message': 'Aerolinea creada con éxito',
                'tenant_id': item['tenant_id']['S'],
                'codigo': item['codigo']['S']
            })
        }
    except Exception as error:
        logging.error("Error al guardar la aerolínea en DynamoDB: %s", error)
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Ocurrió un error al crear la aerolínea'})
        }
