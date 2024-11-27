const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();
const lambda = new AWS.Lambda();
const { DateTime } = require('luxon');

const { randomUUID } = require('crypto');
//const uuid = require('uuid'); // Asegúrate de tener esta librería instalada

const REVIEWS_TABLE = process.env.REVIEWS_TABLE;

exports.handler = async (event) => {
    console.log(event);
    const data = JSON.parse(event.body);
    
    // Inicio - Proteger el Lambda
    const token = event.headers.Authorization;
    
    const payload = JSON.stringify({ token: token });
    
    try {
        const invokeResponse = await lambda.invoke({
            FunctionName: "ValidarTokenAcceso", 
            InvocationType: 'RequestResponse',
            Payload: payload
        }).promise();
        
        const response = JSON.parse(invokeResponse.Payload);
        console.log(response);
        
        if (response.statusCode === 403) {
            return {
                statusCode: 403,
                body: JSON.stringify({
                    status: 'Forbidden - Acceso No Autorizado'
                })
            };
        }

        // Aquí se obtiene el user_id de la respuesta de ValidarTokenAcceso
        const user_id = response.user_id; 


    } catch (error) {
        console.error("Error invocando la función Lambda: ", error);
        return {
            statusCode: 500,
            body: JSON.stringify({
                status: 'Internal Server Error',
                message: 'Hubo un problema al validar el token'
            })
        };
    }
    // Fin - Proteger el Lambda 


    // Proceso - Guardar el producto en DynamoDB
    
    try {
        


        // Procesar la solicitud de la reseña
        const item = {
            id_usuario: user_id,
            id_resenia: randomUUID(),
            id_vuelo: data.id_vuelo, //falta validar el id_vuelo
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

