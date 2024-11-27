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

    // Intentamos parsear el cuerpo de la solicitud
    let data;
    try {
        data = typeof event.body === "string" ? JSON.parse(event.body) : event.body;
    } catch (error) {
        console.error("Error al parsear event.body:", error);
        return {
            statusCode: 400,
            body: JSON.stringify({ message: "Body no es un JSON válido" })
        };
    }

    // Inicio - Proteger el Lambda con la validación del token
    const token = event.headers.Authorization;
    
    // Invocar el Lambda de Python para validar el token
    const validationResponse = await lambda.invoke({
        FunctionName: 'servicio-vuelos-r-dev-validarToken', // Nombre del Lambda Python
        Payload: JSON.stringify({ token }), // Pasa el token en el evento
    }).promise();

    const parsedResponse = JSON.parse(validationResponse.Payload);
    
    if (parsedResponse.statusCode !== 200) {
        return {
            statusCode: parsedResponse.statusCode,
            body: JSON.stringify({
                message: parsedResponse.body.message || 'Token inválido o error en la validación'
            })
        };
    }

    // Aquí obtenemos el `user_id` de la respuesta de `validarTokenAcceso`
    const user_id = parsedResponse.body.user_id;
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
            id_usuario: user_id,
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
        console.error(error);
        return {
            statusCode: 500,
            body: JSON.stringify({ message: 'Ocurrió un error al crear la reseña' })
        };
    }
};
