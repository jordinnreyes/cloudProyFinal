import boto3
import hashlib
import uuid  # Genera valores únicos
from datetime import datetime, timedelta
import os  # Para acceder a las variables de entorno
import json  # Para manejar el cuerpo de la respuesta en JSON

# Hashear contraseña
def hash_password(password):
    print("Hashing password...")
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        print("Lambda function invoked.")
        
        # Leer cuerpo de la solicitud
        try:
            body = json.loads(event.get('body', '{}'))
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'body': '{"message": "Invalid JSON format in request body"}}'
            }

        print(f"Request body: {body}")
        
        user_id = body.get('user_id')
        password = body.get('password')

        if not user_id or not password:
            print("Missing user_id or password.")
            return {
                'statusCode': 400,
                'body': '{"message": "Missing user_id or password"}}'
            }

        # Hashear la contraseña ingresada
        hashed_password = hash_password(password)
        print(f"Hashed password: {hashed_password}")

        # Conexión a DynamoDB
        dynamodb = boto3.resource('dynamodb')
        users_table_name = os.environ['tabla_usuarios']
        print(f"Users table name: {users_table_name}")
        t_usuarios = dynamodb.Table(users_table_name)

        # Obtener usuario de DynamoDB
        response = t_usuarios.get_item(Key={'user_id': user_id})
        print(f"DynamoDB response: {response}")

        if 'Item' not in response:
            print("User not found in DynamoDB.")
            return {
                'statusCode': 403,
                'body': '{"message": "User does not exist"}}'
            }

        # Validar contraseña
        hashed_password_bd = response['Item']['password']
        print(f"Stored hashed password: {hashed_password_bd}")

        if hashed_password != hashed_password_bd:
            print("Incorrect password.")
            return {
                'statusCode': 403,
                'body': '{"message": "Password Incorrecto"}}'
            }

        # Generar token
        token = str(uuid.uuid4())
        fecha_hora_exp = datetime.now() + timedelta(minutes=60)
        print(f"Generated token: {token}, expires at: {fecha_hora_exp}")

        # Guardar token en la tabla DynamoDB
        tokens_table_name = os.environ['t_tokens_acceso']
        print(f"Tokens table name: {tokens_table_name}")
        t_tokens_acceso = dynamodb.Table(tokens_table_name)

        registro = {
            'token': token,
            'expires': fecha_hora_exp.strftime('%Y-%m-%d %H:%M:%S'),
            'user_id': user_id  # Agregar user_id al registro del token
        }
        print(f"Token record: {registro}")

        t_tokens_acceso.put_item(Item=registro)
        print("Token stored successfully.")

        # Respuesta exitosa
        #user_id = user_id.replace('"', '\\"')
        #token = token.replace('"', '\\"')
        #return {
        #    'statusCode': 200,
        #    'body': f'{{"message": "User login successfully", "user_id": "{user_id}", "token": "{token}"}}'
        #}
        return {
            'statusCode': 200,
            'body': json.dumps({
                "message": "User login successfully",
                "user_id": user_id,
                "token": token
            })
        }

    except Exception as e:
        # Imprimir error completo para depuración
        print("Exception occurred:", str(e))
        return {
            'statusCode': 500,
            'body': f'{{"message": "Internal server error", "error": "{str(e)}"}}'
        }
