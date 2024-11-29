import boto3
import random
import uuid
from datetime import datetime
import os 


# Configuración de DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table_name = "servicio-vuelos-r-dev-resenas"

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
            'user_id': user_id,
            'id_resenia': str(uuid.uuid4()),
            'id_vuelo': id_vuelo,
            'calificacion': calificacion,
            'comentario': comentario,
            'fecha_resena': fecha_resena
        }


        # Insertar el item en DynamoDB
        try:
            table = dynamodb.Table(table_name)
            table.put_item(Item=item)

            print(f'Reseña agregada: {item["id_resenia"]}')

        except Exception as e:
            print(f"Error al insertar la reseña: {e}")

if __name__ == "__main__":
    crear_resenas()
