import boto3
from datetime import datetime

def lambda_handler(event, context):
    # Entrada (json)
    token = event['token']

    user_id_request = event.get('user_id')  
    # Proceso
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_tokens_acceso')
    response = table.get_item(
        Key={
            'token': token
        }
    )
    if 'Item' not in response:
        return {
            'statusCode': 403,
            'body': 'Token no existe'
        }
    
    # Obtener el usuario asociado al token
    user_id = response['Item'].get('user_id')
    expires = response['Item']['expires']
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if now > expires:
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