import boto3
import json
import logging
import os


# Configuración de DynamoDB
dynamodb = boto3.client('dynamodb')
lambda_client = boto3.client('lambda')
table_name = os.environ['VUELOS_TABLE']



aerolineas_table = os.environ['AEROLINEAS_TABLE'] 


# Configuración del logging
logging.basicConfig(level=logging.INFO)


def lambda_handler(event, context):
    print(event)
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



    # Validar tenant_id en la tabla de aerolíneas
    codigo = data.get('codigo')
    if not codigo:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'El codigo es obligatorio'})
        }

    tenant_id = data.get('tenant_id')
    if not tenant_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'El tenant_id es obligatorio'})
        }

    try:
        # Consultar si el tenant_id existe en la tabla de aerolíneas
        response = dynamodb.get_item(
            TableName=aerolineas_table,
            Key={
                'tenant_id': {'S': tenant_id},
                'codigo': {'S': codigo}
            }
        )

        # Si no se encuentra el tenant_id
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': f'Tenant_id {tenant_id} no existe en la tabla de aerolíneas'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error al verificar el tenant_id', 'error': str(e)})
        }
    





    # Proceso - Guardar la reseña en DynamoDB
    try:
        item = {
            'tenant_id': {'S': tenant_id},
            'codigo': {'S': data.get('codigo')},#  Tenant_id como parte de la clave primaria
            'id_vuelo': {'S': data.get('id_vuelo')},  # veulo identificada por 'codigo'
            'origen': {'S': data.get('origen')},
            'destino': {'S': data.get('destino')},
            'fecha_salida': {'S': data.get('fecha_salida')},
            'fecha_llegada': {'S': data.get('fecha_llegada')},
            'capacidad': {'S': data.get('capacidad')}
        }

        # Guardar la aerolínea en DynamoDB
        dynamodb.put_item(
            TableName=table_name,
            Item=item
        )

        return {
            'statusCode': 201,
            'body': json.dumps({
                'message': 'Vuelo creada con éxito',
                'tenant_id': item['tenant_id']['S'],
                'id_vuelo': item['id_vuelo']['S']
            })
        }
    except Exception as error:
        logging.error("Error al guardar la aerolínea en DynamoDB: %s", error)
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Ocurrió un error al crear el Vuelo'})
        }
