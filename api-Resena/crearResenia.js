const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();
const { randomUUID } = require('crypto');

// Crea una instancia del cliente Lambda
const lambda = new AWS.Lambda();

const REVIEWS_TABLE = process.env.REVIEWS_TABLE;
if (!REVIEWS_TABLE) {
    throw new Error("La variable de entorno REVIEWS_TABLE no está configurada.");
}

exports.handler = async (event) => {

    console.log("Contenido de event.body:", event.body);
    const stage = process.env.STAGE; // Valor por defecto: 'dev'
    // Construir el nombre de la función Lambda de validación
    const functionName = `servicio-vuelos-aero-${stage}-validarToken`;

    // Intentamos parsear el cuerpo de la solicitud
    // Bloque 1: Verificar si el cuerpo está vacío
    let data;
    try {
        const body = event.body || null;

        if (!body) {
            console.error("El cuerpo del JSON está vacío");
            return {
                statusCode: 400,
                body: JSON.stringify({ message: 'El cuerpo del JSON está vacío' })
            };
        }

        // Verificar si body es una cadena antes de intentar parsearla
        if (typeof body === "string") {
            if (body.trim() === "") {
                console.error("El cuerpo del JSON está vacío después de recortar espacios");
                return {
                    statusCode: 400,
                    body: JSON.stringify({ message: 'El cuerpo del JSON está vacío después de recortar espacios' })
                };
            }
            try {
                data = JSON.parse(body);
            } catch (e) {
                console.error("Error de decodificación JSON:", e);
                return {
                    statusCode: 400,
                    body: JSON.stringify({ message: 'Error de decodificación JSON: ' + e.message })
                };
            }
        } else if (typeof body === "object") {
            // Si es un objeto ya, no es necesario parsear
            data = body;
        } else {
            console.error("Formato de cuerpo no válido:", typeof body);
            return {
                statusCode: 400,
                body: JSON.stringify({ message: 'Formato del cuerpo no válido' })
            };
        }

        console.log("JSON parseado correctamente:", data);

    } catch (error) {
        console.error("Error al procesar el cuerpo de la solicitud:", error);
        return {
            statusCode: 500,
            body: JSON.stringify({ message: 'Error interno al procesar el cuerpo' })
        };
    }


    // Inicio - Proteger el Lambda con la validación del token
    const token = event.headers.Authorization?.split(' ')[1];

    console.log("Token recibido:", event.headers.Authorization); 
    
    console.log("Token recibido2 :", token);  
    
    if (!token) {
        return {
            statusCode: 400,
            body: JSON.stringify({ message: "Token no proporcionado" })
        };
    }
    
    // Invocar el Lambda de Python para validar el token
    let validationResponse;
    try {

        console.log("Payload enviado al servicio de validación:", JSON.stringify({ token: token })); // Log de lo enviado
        
        validationResponse = await lambda.invoke({
            FunctionName: functionName, // Nombre del Lambda Python
            Payload: JSON.stringify({ body: JSON.stringify({ token: token }) }), // Pasa el token en el evento
        }).promise();
        
        console.log("Respuesta de validación del token:", validationResponse.Payload); // Log de la respuesta recibida
    } catch (error) {
        console.error("Error al invocar la función Lambda de validación:", error);
        return {
            statusCode: 500,
            body: JSON.stringify({ message: "Error al invocar la validación de token" })
        };
    }

    // Manejo de la respuesta de validación
    let parsedResponse;
    try {
        parsedResponse = JSON.parse(validationResponse.Payload); // Parsea el Payload principal
        
        if (typeof parsedResponse.body === "string") {
            parsedResponse.body = JSON.parse(parsedResponse.body); // Parsea el body si es un string
        } else if (typeof parsedResponse.body !== "object") {
            throw new Error("El body tiene un formato inesperado");
        }

    } catch (error) {
        console.error("Error al procesar la respuesta de validación:", error);
        return {
            statusCode: 500,
            body: JSON.stringify({ message: "Error al procesar la respuesta de validación" })
        };
    }

    // Verificar si la respuesta contiene el código de estado esperado
    if (!parsedResponse || parsedResponse.statusCode !== 200) {
        const message = parsedResponse?.body?.message || 'Token inválido o error en la validación';
        return {
            statusCode: parsedResponse?.statusCode || 400,
            body: JSON.stringify({
                message: message
            })
        };
    }

    // Aquí obtenemos el `user_id` de la respuesta de `validarTokenAcceso`
    const user_id = parsedResponse.body?.user_id;
    if (!user_id) {
        return {
            statusCode: 403,
            body: JSON.stringify({
                status: 'Token inválido o usuario no autorizado'
            })
        };
    }

    // Fin - Proteger el Lambda  - El token ha sido validado

    // Proceso - Guardar la reseña en DynamoDB
    try {
        const item = {
            user_id: user_id,
            id_resenia: randomUUID(),
            id_vuelo: data.id_vuelo, // Faltaría validar el id_vuelo
            calificacion: data.calificacion,
            comentario: data.comentario,
            fecha_resena: data.fecha_resena
        };

        // Guardar la reseña en DynamoDB
        await dynamodb.put({
            TableName: REVIEWS_TABLE,
            Item: item
        }).promise();

        return {
            statusCode: 201,
            body: JSON.stringify({ 
                message: 'Reseña creada con éxito',
                id_resenia: item.id_resenia
             })
        };
    } catch (error) {
        console.error("Error al guardar la reseña en DynamoDB:", error);
        return {
            statusCode: 500,
            body: JSON.stringify({ message: 'Ocurrió un error al crear la reseña' })
        };
    }
};
