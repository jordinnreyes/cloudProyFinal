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
    aws_access_key_id='ASIAREVE542PTI5BBBRE',
    aws_secret_access_key='xbxXWjZGMUzlrCRD885GZOIEp5zY+PD00sycoTH1',
    aws_session_token='IQoJb3JpZ2luX2VjEFMaCXVzLXdlc3QtMiJGMEQCICtHH5g/Y3WX6+2ZRjjHjPqOMPUESuLf/P1YFPihqMOQAiAQGxkcPomrUgssAZPlJzdeEmirToG4CnPeA2ixeC5bZSrAAgj8//////////8BEAMaDDA3ODcyOTA0NTY2MyIMzXGXf5rmy/hvHHSbKpQCUp904O2Vp6xahKvAP298O7KfgIak1l+ZBPnn+MCJ4B+GRIF4ztWznxsjbuoNfonUyjZ0XtojJ8j4xjizAOWvYCTaqYVErZ6aEuPZUxC4ajd+NKoj113m3NjfELndMQKHRyjkGv5dJXr3GVt8CnWG4RHnGZsBbaaFhc6iw4mQ8u5uLDAbAv5Ho/wPa5wWYII4id4BfFP3rzto4eI2vanjrJGOD9Yv8DIsq8B7GRGDPr8btp7Y9YcsBiMabBzLgYpnO93ESArYOCYX1NzYWsWYEP5GGqSXlcttomk6QiFJ+ARQNYcKa8CClSwoZlsw8ohk6d1+fLhwL+qZGdgEshgnq9BFGxtGkWeO51xESilHrvxCU98lMJe2xLoGOp4Bwb6jGkGNM4SiHSimA4nexdarccTtMnoHhPHpKxq5Wtlb6bm67QQnORGpsYRKyDPnSdKUV5OaVVC9XyzP0k53LCDCeB8ygj3/j37dv9slrCHWtG8K+pMfIpMsVS7oy/Jv6BiPExVapjyfqEjZRNk/KXhlTWVVEuP4muXh3hLMC6b1Lw23r1RpibiGkra5todVHJ+Gg+ieqmixVyk0xmM='
)

table_name_resenas = "servicio-vuelos-r-test-resenas"  
table_name_aerolineas = "servicio-vuelos-aero-test-aerolineas"
table_name_vuelos = "servicio-vuelos-v-test-vuelos"
table_name_usuarios = "servicio-vuelos-test-usuario"
compras_table = "servicio-vuelos-compras-test-compras"
table_name_destinos = "servicio-vuelos-destino-test-destinos"


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
    return aerolineas  # Retorna la lista de aerolíneas creadas
# Funciones existentes para reseñas



#----------------------------GENERAR VUELOS------------------------------------------

# Función para generar vuelos ficticios
def crear_vuelos(cantidad=10000, aerolineas=[]):

    if not aerolineas:
        print("No se crearon aerolíneas. No se pueden generar vuelos.")
        return

    
    destinos = ['Lima', 'Nueva York', 'París', 'Bogotá', 'Madrid', 'Buenos Aires', 'Tokio', 'Sídney']
    origenes = ['Lima', 'Miami', 'Los Ángeles', 'Sao Paulo', 'México DF', 'Londres', 'Dubai', 'Toronto']

    vuelos = []
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
            'capacidad': str(random.randint(50, 300))  # Convertir a string
        }
        try:
            table_vuelos.put_item(Item=item)
            vuelos.append(item)
            print(f"Vuelo creado: {item['id_vuelo']} para aerolínea {aerolinea['nombre']}")
        except Exception as e:
            print(f"Error al crear vuelo: {e}")
    return vuelos  # Retornar la lista de vuelos generados



#----------------------------GENERAR USUARIOS------------------------------------------

# Hashear contraseña
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Generar datos ficticios para usuarios
def generar_usuarios(cantidad=10000):# Nombre de la tabla desde variable de entorno
    t_usuarios = dynamodb.Table(table_name_usuarios)

    nombres = ['Carla', 'Mario', 'Juana', 'Anabel', 'Luisa', 'Sofí', 'Pedrita', 'Camilo', 'Josesita', 'Lucio']
    dominios = ['example.com', 'mail.com', 'test.org', 'sample.net']
    usuarios = []  #

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
            usuarios.append(user_id)
        except Exception as e:
            print(f"Error al registrar el usuario {user_id}: {e}")

    return usuarios  # Retornar la lista de usuarios generados


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
            precio_total = str(random.randint(50, 700))  # Precio por boleto entre $50 y $500

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
        id_vuelo = random.choice(vuelos)['id_vuelo']  # Asegurarte de acceder solo al valor 'id_vuelo' dentro del diccionario  
        
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
def generar_destinos(cantidad=10000):
    
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
            exit()
        
        print("\nGenerando usuarios ficticios...")
        usuarios = generar_usuarios(cantidad=10000)  

        if aerolineas:  # Verifica si se crearon aerolíneas
            print("\nGenerando vuelos...")
            vuelos = crear_vuelos(cantidad=10000, aerolineas=aerolineas) 
            if not vuelos:  # Verifica si la lista de aerolíneas está vacía
                print("No se crearon vuelos. No se pueden generar .")
                exit()# Genera vuelos solo si hay aerolíneas

            if usuarios and vuelos:  # Verifica que haya usuarios y vuelos antes de generar reseñas y compras
                print("\nGenerando reseñas ficticias...")
                crear_resenas(usuarios=usuarios, vuelos=vuelos)  # Pasa los vuelos generados

                print("\nGenerando compras ficticias...")
                generar_compras(cantidad=10000, usuarios=usuarios, vuelos=vuelos)  # Pasa los vuelos generados

        #Comentado la generación de destinos, ya que ya se crearon muchos
        print("\nGenerando destinos ficticios...")
        generar_destinos(cantidad=10000)
    
    except Exception as e:
        print(f"Error durante la ejecución: {e}")

