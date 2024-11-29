import boto3
import random
import uuid
from datetime import datetime, timedelta
import hashlib
import os 


# Configuración de DynamoDB
# Configuración de DynamoDB con credenciales
dynamodb = boto3.resource(
    'dynamodb',
    region_name='us-east-1',
    aws_access_key_id='ASIAREVE542P5UMBBDF7',
    aws_secret_access_key='ExwHOMhih9gX8mWG5uffTg6I3vSNZXCmgyof9WEN',
    aws_session_token='IQoJb3JpZ2luX2VjENT//////////wEaCXVzLXdlc3QtMiJIMEYCIQD8oe7hQFLIdyvK3+JBd6+GxIf+d7UMzbGFcGVALTcSUgIhAPBcB0OCWfXkOl7+MviBSKD4XLIZGaUD3ECxfjxcBhOZKrcCCH0QAxoMMDc4NzI5MDQ1NjYzIgyVM+i6VBXODkN2W2wqlAIzWECRskbK6Y3/34DaAEyUCGqEz7v30DbxG5P2uKjHYhmL+GQWDndVJbFnFRAgs6tubdWPkJB8Mq1mtBkSsnvdrhlOqzTuFNZi/Eu3wkSt3fVQUZybNCJP33yRSrqYzvbtalmYSYtU3RVAF/vD5tzXtb2eA5vHB0brWmO5Kt+HeCRouA+wLC+Vl1kARciQx7mnQnrpsMq5ALa07dP1p1tWIT5pMwCJJjfU7wRw+ILc95dsX4m6L2q65KGE4p+MoB3XhHgGqT0dER0aN8ABsi103jsO5VvHaTZt/sxS2RoHa1F9XIC/cjaqzqBx1tAqNlkQ8kozvfjV9M4UZLhG8Lt4wP1rsPBF/7K9mZa3n4r+oiqSnC0wl6+ougY6nAELpRaxdYtFZJUG54/XVZPSPFnoB+ftpRDzmKPecPBM6X6RMXi8YKirMKuhQyT2KA3j95nS1DQU9Y52uQ81zOok/3c5mznd65bVXFW3lUnIBKf1WOGvB4aohGhsBdpVBTKjoLcbAoFD3AmOhQqg11PtNw9hEP9+qKDgXeQL+6oMg5ogW8LRN7aBQU1b4HsZnrSGXY98hLUZlmTrAOg='
)

table_name_resenas = "servicio-vuelos-r-dev-resenas"  
table_name_aerolineas = "servicio-vuelos-aero-dev-aerolineas"
table_name_vuelos = "servicio-vuelos-v-dev-vuelos"
table_name_usuarios = "servicio-vuelos-dev-usuario"
compras_table = "servicio-vuelos-compras-dev-compras"
table_name_destinos = "servicio-vuelos-destino-dev-destinos"


#----------------------------GENERAR AEROLINEAS------------------------------------------

# Función para generar aerolíneas ficticias
def crear_aerolineas():
    aerolineas = [
        {
            'tenant_id': str(uuid.uuid4()),
            'codigo': 'LATAM001',
            'nombre': 'LATAM Airlines',
            'pais_origen': 'Perú'
        },
        {
            'tenant_id': str(uuid.uuid4()),
            'codigo': 'AA002',
            'nombre': 'American Airlines',
            'pais_origen': 'Estados Unidos'
        },
        {
            'tenant_id': str(uuid.uuid4()),
            'codigo': 'AF003',
            'nombre': 'Air France',
            'pais_origen': 'Francia'
        }
    ]

    for aerolinea in aerolineas:
        item = {
            'tenant_id': aerolinea['tenant_id'],
            'codigo': aerolinea['codigo'],
            'nombre': aerolinea['nombre'],
            'pais_origen': aerolinea['pais_origen']
        }
        try:
            table_name_aero = dynamodb.Table(table_name_aerolineas)
            table_name_aero.put_item(Item=item)
            print(f"Aerolínea creada: {aerolinea['nombre']} ({aerolinea['codigo']})")
        except Exception as e:
            print(f"Error al crear aerolínea {aerolinea['nombre']}: {e}")

# Funciones existentes para reseñas



#----------------------------GENERAR VUELOS------------------------------------------

# Función para generar vuelos ficticios
def crear_vuelos(cantidad=10000, aerolineas=[]):

    if not aerolineas:
        print("No se crearon aerolíneas. No se pueden generar vuelos.")
        return

    
    destinos = ['Lima', 'Nueva York', 'París', 'Bogotá', 'Madrid', 'Buenos Aires', 'Tokio', 'Sídney']
    origenes = ['Lima', 'Miami', 'Los Ángeles', 'Sao Paulo', 'México DF', 'Londres', 'Dubai', 'Toronto']
    
    table_vuelos = dynamodb.Table(table_name_vuelos)
    for _ in range(cantidad):
        aerolinea = random.choice(aerolineas)  # Asociar vuelo a una aerolínea existente
        item = {
            'tenant_id': aerolinea['tenant_id'],
            'codigo': aerolinea['codigo'],
            'id_vuelo': str(uuid.uuid4()),
            'origen': random.choice(origenes),
            'destino': random.choice(destinos),
            'fecha_salida': (datetime.now() + timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d %H:%M:%S'),
            'fecha_llegada': (datetime.now() + timedelta(days=random.randint(31, 60))).strftime('%Y-%m-%d %H:%M:%S'),
            'capacidad': random.randint(50, 300)
        }
        try:
            table_vuelos.put_item(Item=item)
            print(f"Vuelo creado: {item['id_vuelo']['S']} para aerolínea {aerolinea['nombre']}")
        except Exception as e:
            print(f"Error al crear vuelo: {e}")




#----------------------------GENERAR USUARIOS------------------------------------------

# Hashear contraseña
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Generar datos ficticios para usuarios
def generar_usuarios(cantidad=10000):# Nombre de la tabla desde variable de entorno
    t_usuarios = dynamodb.Table(table_name_usuarios)

    nombres = ['Carlos', 'María', 'Juan', 'Ana', 'Luis', 'Sofía', 'Pedro', 'Camila', 'José', 'Lucía']
    dominios = ['example.com', 'mail.com', 'test.org', 'sample.net']

    for _ in range(cantidad):
        # Crear datos ficticios para el usuario
        user_id = f"{random.choice(nombres)}{random.randint(1, 9999)}@{random.choice(dominios)}"
        password = str(uuid.uuid4())[:8]  # Generar una contraseña aleatoria corta
        hashed_password = hash_password(password)  # Hashear la contraseña

        # Almacenar el usuario en DynamoDB
        try:
            t_usuarios.put_item(
                Item={
                    'user_id': user_id,
                    'password': hashed_password,
                }
            )
            print(f"Usuario registrado: {user_id} (Contraseña: {password})")
        except Exception as e:
            print(f"Error al registrar el usuario {user_id}: {e}")




#----------------------------GENERAR COMPRAS------------------------------------------

# Función para generar compras ficticias
def generar_compras(cantidad=10000, usuarios=[], vuelos=[]):
    print(f"Generando {cantidad} compras para {len(usuarios)} usuarios y {len(vuelos)} vuelos.")
    
    if not usuarios or not vuelos:
        print("Error: La lista de usuarios o la lista de vuelos está vacía.")
        return

    
    table_compras = dynamodb.Table(compras_table)
    """
    Genera `cantidad` de compras aleatorias.
    - `usuarios`: lista de user_id generados previamente.
    - `vuelos`: lista de id_vuelo generados previamente.
    """

    for _ in range(cantidad):
        try:
            # Crear datos aleatorios para la compra
            user_id = random.choice(usuarios)
            id_vuelo = random.choice(vuelos)
            fecha_compra = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cantidad_boletos = random.randint(1, 5)  # Entre 1 y 5 boletos por compra
            precio_total = random.randint(50, 500)  # Precio por boleto entre $50 y $500

            # Crear el ítem para DynamoDB
            item = {
                'user_id': user_id,
                'id_compra': str(uuid.uuid4()),  # ID único de la compra
                'id_vuelo': id_vuelo,
                'fecha_compra': fecha_compra,
                'cantidad_boletos': cantidad_boletos,
                'precio_total': precio_total
            }

            # Insertar en DynamoDB
            table_compras.put_item(Item=item)
            print(f"Compra registrada: {item['id_compra']} para usuario {user_id} y vuelo {id_vuelo}")
        except Exception as e:
            print(f"Error al registrar compra: {e}")









#----------------------------GENERAR RESEÑA------------------------------------------







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



# Crear reseñas en DynamoDB usando los user_id e id_vuelo de las compras
def crear_resenas(usuarios, vuelos):
    print(f"Generando reseñas para {len(usuarios)} usuarios y {len(vuelos)} vuelos.")
    if not usuarios or not vuelos:
        print("Error: La lista de usuarios o la lista de vuelos está vacía.")
        return
    table_resenas = dynamodb.Table(table_name_resenas)

    # Generamos reseñas basadas en las compras
    for _ in range(5000):  # Crear 100 reseñas
        user_id = random.choice(usuarios)  # Seleccionar un usuario de la lista de usuarios
        id_vuelo = random.choice(vuelos)  # Seleccionar un vuelo de la lista de vuelos
        
        # Si ya hay una compra para este usuario y vuelo, se genera la reseña
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
            table_resenas.put_item(Item=item)
            print(f'Reseña agregada: {item["id_resenia"]} para usuario {user_id} y vuelo {id_vuelo}')
        except Exception as e:
            print(f"Error al insertar la reseña: {e}")





#----------------------------GENERAR DESTINOS------------------------------------------


# Función para generar destinos ficticios
def generar_destinos(cantidad=5000):
    
    destinos_table = dynamodb.Table(table_name_destinos)
    """
    Genera destinos ficticios y los inserta en DynamoDB.
    """
    # Listas de ejemplo para ciudades y países
    ciudades = ['Lima', 'Nueva York', 'París', 'Bogotá', 'Madrid', 'Buenos Aires', 'Tokio', 'Sídney', 'Roma', 'Toronto']
    paises = ['Perú', 'Estados Unidos', 'Francia', 'Colombia', 'España', 'Argentina', 'Japón', 'Australia', 'Italia', 'Canadá']
    descripciones = [
        'Un destino lleno de historia y cultura.',
        'Perfecto para los amantes de la gastronomía.',
        'Paisajes increíbles para disfrutar.',
        'Un lugar lleno de aventuras y emociones.',
        'Ideal para una escapada romántica.',
        'Destacada por su vida nocturna.',
        'Conocido por su arquitectura impresionante.',
        'Un paraíso para los amantes de la naturaleza.',
        'Un destino que combina tradición y modernidad.',
        'Famoso por sus festivales y eventos.'
    ]

    for _ in range(cantidad):
        try:
            # Crear datos ficticios para el destino
            item = {
                'id_destino': str(uuid.uuid4()),  # ID único del destino
                'ciudad': random.choice(ciudades),
                'pais': random.choice(paises),
                'descripcion': random.choice(descripciones),
                'popularidad': random.randint(1, 100)  # Popularidad de 1 a 100
            }

            # Insertar en DynamoDB
            destinos_table.put_item(Item=item)
            print(f"Destino registrado: {item['ciudad']}, {item['pais']} (ID: {item['id_destino']})")
        except Exception as e:
            print(f"Error al registrar destino: {e}")



if __name__ == "__main__":
    try:
        print("Creando aerolíneas ficticias...")
        aerolineas = crear_aerolineas()
        if not aerolineas:  # Verifica si la lista de aerolíneas está vacía
            print("No se crearon aerolíneas. No se pueden generar vuelos.")
            return
        
        print("\nGenerando usuarios ficticios...")
        usuarios = generar_usuarios(cantidad=10000)  

        if aerolineas:  # Verifica si se crearon aerolíneas
            print("\nGenerando vuelos...")
            vuelos = crear_vuelos(cantidad=10000, aerolineas=aerolineas)  # Genera vuelos solo si hay aerolíneas

            if usuarios and vuelos:  # Verifica que haya usuarios y vuelos antes de generar reseñas y compras
                print("\nGenerando reseñas ficticias...")
                crear_resenas(usuarios=usuarios, vuelos=vuelos)  # Pasa los vuelos generados

                print("\nGenerando compras ficticias...")
                generar_compras(cantidad=10000, usuarios=usuarios, vuelos=vuelos)  # Pasa los vuelos generados

        print("\nGenerando destinos ficticios...")
        generar_destinos(cantidad=10000)
    
    except Exception as e:
        print(f"Error durante la ejecución: {e}")

