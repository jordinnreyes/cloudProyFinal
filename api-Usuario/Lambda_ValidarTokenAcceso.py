import boto3
from datetime import datetime
import os
import json

def lambda_handler(event, context):
    # Entrada (json)
    token = event['token']
    user_id_request = event.get('user_id')  
    
    # Proceso
    dynamodb = boto3.resource('dynamodb')
    table_name = os.environ['t_tokens_acceso']  # Usa la variable de entorno
    table = dynamodb.Table(table_name)

    try:
        response = table.get_item(Key={'token': token})
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error al acceder a la base de datos: {str(e)}'
        }

    if 'Item' not in response:
        return {
            'statusCode': 403,
            'body': 'Token no existe'
        }

    # Obtener el usuario asociado al token
    user_id = response['Item'].get('user_id')
    expires = response['Item']['expires']

    # Convierte 'expires' y 'now' a objetos datetime para compararlos
    expires_datetime = datetime.strptime(expires, '%Y-%m-%d %H:%M:%S')
    now_datetime = datetime.now()

    if now_datetime > expires_datetime:
        return {
            'statusCode': 403,
            'body': 'Token expirado'
        }

    # Validar que el user_id del token coincida con el user_id de la solicitud
    if user_id_request != user_id:
        return {
            'statusCode': 403,
            'body': 'El token no corresponde al usuario logueado'
        }

    # Salida (json)
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Token válido',
            'user_id': user_id
        })
    }
