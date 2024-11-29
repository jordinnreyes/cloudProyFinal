import json
import boto3
from datetime import datetime
import os

def lambda_handler(event, context):
    # Obtener el token de la solicitud
    # Obtener el cuerpo de la solicitud y parsearlo como JSON
    body = json.loads(event.get('body', '{}'))  # Esto maneja el caso donde no haya un cuerpo válido

    # Obtener el token de la solicitud
    token = body.get('token')
    if not token:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Token no proporcionado'
            })
        }
    
    # Primera validación: Token fijo (puede ser para pruebas o un token especial)
    if token == 'valido':
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Token fijo válido',
                'user_id': '12345'
            })
        }
    
    # Segunda validación: Verificación del token en DynamoDB
    # Usar DynamoDB para verificar si el token existe y es válido
    dynamodb = boto3.resource('dynamodb')
    table_name = os.environ['t_tokens_acceso']  # Nombre de la tabla en DynamoDB desde las variables de entorno
    table = dynamodb.Table(table_name)

    try:
        # Obtener el token desde DynamoDB
        response = table.get_item(Key={'token': token})
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error al acceder a la base de datos: {str(e)}'
            })
        }

    # Verificar si el token existe en la base de datos
    if 'Item' not in response:
        return {
            'statusCode': 403,
            'body': json.dumps({
                'message': 'Token no existe'
            })
        }

    # Obtener el user_id asociado al token
    user_id = response['Item'].get('user_id')
    expires = response['Item']['expires']

    # Verificar si el token ha expirado
    expires_datetime = datetime.strptime(expires, '%Y-%m-%d %H:%M:%S')
    now_datetime = datetime.now()

    if now_datetime > expires_datetime:
        return {
            'statusCode': 403,
            'body': json.dumps({
                'message': 'Token expirado'
            })
        }

  
    # Si todo es válido, devolver el user_id y un mensaje de éxito
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Token válido',
            'user_id': user_id
        })
    }