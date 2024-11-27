import boto3
import hashlib
import json
import os  # Para acceder a las variables de entorno

# Hashear contraseña
def hash_password(password):
    # Retorna la contraseña hasheada
    return hashlib.sha256(password.encode()).hexdigest()

# Función que maneja el registro de user y validación del password
def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))  # Esto maneja el caso donde no haya un cuerpo válido
        # Obtener el email y el password
        user_id = event.get('user_id')
        password = event.get('password')
        

        print(f"Received user_id: {user_id}, password: {password}")


        # Verificar que el email y el password existen
        if user_id and password:
            # Hashea la contraseña antes de almacenarla
            hashed_password = hash_password(password)

            print(f"Hashed password: {hashed_password}")
            


            # Conectar DynamoDB
            dynamodb = boto3.resource('dynamodb')
            table_name = os.environ['tabla_usuarios']
            t_usuarios = dynamodb.Table(table_name)
            # Almacena los datos del user en la tabla de usuarios en DynamoDB
            response = t_usuarios.put_item(
                Item={
                    'user_id': user_id,
                    'password': hashed_password,
                }
            )


            print(f"Put item response: {response}")  

            # Retornar un código de estado HTTP 200 (OK) y un mensaje de éxito
            mensaje = {
                'message': 'User registered successfully',
                'user_id': user_id
            }
            return {
                'statusCode': 200,
                'body': json.dumps(mensaje)
            }
        else:
            mensaje = {
                'error': 'Invalid request body: missing user_id or password'
            }
            return {
                'statusCode': 400,
                'body': json.dumps(mensaje)
            }

    except Exception as e:
        # Excepción y retornar un código de error HTTP 500
        print("Exception:", str(e))
        mensaje = {
            'error': str(e)
        }        
        return {
            'statusCode': 500,
            'body': json.dumps(mensaje)
        }
