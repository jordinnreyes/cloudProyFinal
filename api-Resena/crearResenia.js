const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();
// const lambda = new AWS.Lambda(); // Eliminar, ya no es necesario
// const { DateTime } = require('luxon'); // Si no lo necesitas, elimínalo
const { randomUUID } = require('crypto');

const REVIEWS_TABLE = process.env.REVIEWS_TABLE;
if (!REVIEWS_TABLE) {
    throw new Error("La variable de entorno REVIEWS_TABLE no está configurada.");
}

// Incluir la función de validación de token directamente aquí
const validarTokenAcceso = require('./Lambda_ValidarTokenAcceso'); // Ruta al archivo de la función

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
    
    // Usar la función `validarTokenAcceso` directamente
    const validationResponse = await validarTokenAcceso({ token });
    
    if (validationResponse.statusCode !== 200) {
        return validationResponse; // Devuelve el error directamente
    }

    // Aquí obtenemos el `user_id` de la respuesta de `validarTokenAcceso`
    const user_id = validationResponse.body.user_id; 
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
