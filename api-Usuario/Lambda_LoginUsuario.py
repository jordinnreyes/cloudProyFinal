import boto3
import hashlib
import uuid # Genera valores únicos
from datetime import datetime, timedelta

import os  # Para acceder a las variables de entorno
import json  # Para manejar el cuerpo de la respuesta en JSON

# Hashear contraseña
def hash_password(password):
    # Retorna la contraseña hasheada
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    # Entrada (json)
    user_id = event['user_id']
    password = event['password']
    hashed_password = hash_password(password)
    # Proceso
    dynamodb = boto3.resource('dynamodb')
    users_table_name = os.environ['tabla_usuarios']
    t_usuarios = dynamodb.Table(users_table_name)

    response = t_usuarios.get_item(
        Key={
            'user_id': user_id
        }
    )
    if 'Item' not in response:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'User does not exist'})
        }
    else:
        hashed_password_bd = response['Item']['password']


        if hashed_password == hashed_password_bd:
            # Genera token
            token = str(uuid.uuid4())
            fecha_hora_exp = datetime.now() + timedelta(minutes=60)

            tokens_table_name = os.environ['t_tokens_acceso']
            t_tokens_acceso = dynamodb.Table(tokens_table_name)

            registro = {
                'token': token,
                'expires': fecha_hora_exp.strftime('%Y-%m-%d %H:%M:%S'),
                'user_id': user_id  # Agregar user_id al registro del token
            }
            
            t_tokens_acceso.put_item(Item=registro)

        

        else:
            return {
                'statusCode': 403,
                'body': 'Password incorrecto'
            }
    
    # Salida (json)
    return {
        'statusCode': 200,
        'token': json.dumps({'token': token})
    }
