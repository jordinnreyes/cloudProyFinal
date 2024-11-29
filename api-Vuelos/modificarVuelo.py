import boto3
import json
import logging
import os


# Configuración de DynamoDB
dynamodb = boto3.client('dynamodb')
lambda_client = boto3.client('lambda')
table_name = os.environ['VUELOS_TABLE']

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


    print("Headers recibidos:", event['headers'])
     # Inicio - Proteger el Lambda con la validación del token
    authorization_header = event['headers'].get('Authorization', '')
    if not authorization_header.startswith('Bearer '):
        logging.error("Encabezado Authorization ausente o mal formado.")
        return {
            'statusCode': 401,
            'body': json.dumps({'message': 'Token de autorización ausente o mal formado'})
        }

    token = authorization_header.split(' ')[1]
    logging.info("Token recibido: %s", token)
    #verifica su valor
    print("Token extraído:", token)


    if not token:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Token no proporcionado'})
        }

    # Invocar el Lambda de Python para validar el token
    try:
        logging.info("Payload enviado al servicio de validación: %s", json.dumps({'token': token}))
        print("Payload enviado al servicio de validación: :", json.dumps({'token': token}))
        
        validation_response = lambda_client.invoke(
            FunctionName='servicio-vuelos-aero-dev-validarToken',  # Nombre del Lambda Python
            Payload=json.dumps({'body': json.dumps({'token': token})})# Pasamos el token en el evento
        )

        response_payload = validation_response['Payload'].read().decode('utf-8')
        logging.info("Respuesta del servicio de validación: %s", response_payload)
        print("Respuesta de validación del token: %s", response_payload)

        # Parsear la respuesta principal
        parsed_response = json.loads(response_payload)  # Convertir a dict
        logging.info("Respuesta principal parseada: %s", parsed_response)
    
        # Parsear el cuerpo anidado (body) si existe
        parsed_body = json.loads(parsed_response.get('body', '{}'))  # Obtener y parsear el cuerpo
        logging.info("Cuerpo anidado parseado: %s", parsed_body)
    
        # Validar el estado del token
        if parsed_response.get('statusCode') != 200:
            message = parsed_body.get('message', 'Token inválido o error en la validación')
            return {
                'statusCode': parsed_response.get('statusCode', 400),
                'body': json.dumps({'message': message})
            }
    
        # Validación específica del token
        if parsed_body.get('message') == "Token válido":
            logging.info("El token es válido")
            user_id = parsed_body.get('user_id', 'Usuario desconocido')
            logging.info("Usuario autenticado: %s", user_id)
        else:
            logging.error("El token no es válido")
            return {
                'statusCode': 401,
                'body': json.dumps({'message': 'Token no válido'})
            }
    
    except json.JSONDecodeError as e:
        logging.error("Error al parsear la respuesta de validación: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error al procesar la respuesta de validación'})
        }

    except Exception as e:
        logging.error("Error inesperado al manejar la respuesta: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error interno del servidor'})
        }


    # Fin - Proteger el Lambda  - El token ha sido validado

    # Obtener tenant_id y otros parámetros del body
    tenant_id = data.get('tenant_id')
    id_vuelo = data.get('id_vuelo')
    destino = data.get('destino')
    origen = data.get('origen')

    if not tenant_id or not id_vuelo:
        logging.error("El tenant_id o id_vuelo no están presentes en el cuerpo de la solicitud.")
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'El tenant_id y id_vuelo son obligatorios'})
        }

    # Proceso - Modificar la aerolínea en DynamoDB
    try:
        response = dynamodb.update_item(
            TableName=table_name,
            Key={
                'tenant_id': {'S': tenant_id},
                'id_vuelo': {'S': id_vuelo}
            },
            UpdateExpression="SET destino = :destino, origen = :origen",
            ExpressionAttributeValues={
                ':destino': {'S': destino},
                ':origen': {'S': origen}
            },
            ReturnValues="ALL_NEW"
        )

        updated_item = response['Attributes']
        logging.info("vuelo modificada: %s", updated_item)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'vuelo modificada con éxito',
                'updated_vuelo': updated_item
            })
        }
    except Exception as error:
        logging.error("Error al modificar la vuelo en DynamoDB: %s", error)
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Ocurrió un error al modificar la vuelo'})
        }
