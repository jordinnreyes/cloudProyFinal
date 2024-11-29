import boto3
import random
import uuid
from datetime import datetime
import os 

# Configuración de DynamoDB
dynamodb = boto3.client('dynamodb')
table_name = os.environ['REVIEWS_TABLE']
 # Cambia esto por el nombre de tu tabla

# Función para generar un comentario aleatorio
def generar_comentario():
    comentarios = [
        "Excelente servicio, muy recomendado!",
        "El vuelo estuvo bien, aunque hubo algunos retrasos.",
        "No me gustó la experiencia, el servicio debe mejorar.",
        "Muy buena atención, el personal es amable.",
        "El vuelo fue cómodo, pero el ambiente podría mejorar.",
        "Excelente, todo salió como se esperaba.",
        "Mal servicio, no repetiría.",
        "La comida fue excelente durante el vuelo.",
        "Muy puntual y eficiente el embarque.",
        "El piloto fue muy profesional durante el vuelo."
    ]
    return random.choice(comentarios)

# Función para generar una calificación aleatoria entre 1 y 5
def generar_calificacion():
    return random.randint(1, 5)

# Función para generar una fecha aleatoria (en el pasado reciente)
def generar_fecha():
    fecha = datetime.now()
    return fecha.strftime("%Y-%m-%d %H:%M:%S")

# Crear reseñas en DynamoDB
def crear_resenas():
    for _ in range(100):  # Crear 100 reseñas
        user_id = str(uuid.uuid4())  # Generar un UUID aleatorio para el user_id
        id_vuelo = str(random.randint(1000, 9999))  # ID de vuelo aleatorio
        calificacion = generar_calificacion()
        comentario = generar_comentario()
        fecha_resena = generar_fecha()

        # Crear el item para DynamoDB
        item = {
            'user_id': {'S': user_id},
            'id_resenia': {'S': str(uuid.uuid4())},  # ID de reseña único
            'id_vuelo': {'S': id_vuelo},
            'calificacion': {'N': str(calificacion)},
            'comentario': {'S': comentario},
            'fecha_resena': {'S': fecha_resena}
        }

        # Insertar el item en DynamoDB
        try:
            response = dynamodb.put_item(
                TableName=table_name,
                Item=item
            )
            print(f'Reseña agregada: {item["id_resenia"]["S"]}')
        except Exception as e:
            print(f"Error al insertar la reseña: {e}")

if __name__ == "__main__":
    crear_resenas()
