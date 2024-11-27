const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();
const lambda = new AWS.Lambda();
const { DateTime } = require('luxon');


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

        // Obtener el user_id de la respuesta de ValidarTokenAcceso
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


    // Proceso - Modificar la reseña en DynamoDB
    const resenia_id = data.resenia_id;  // El ID de la reseña que se desea modificar
    const { calificacion, comentario } = data;  // Nuevos valores de calificación y comentario
    
    try {
        // Verificar si la reseña existe en la base de datos
        const params = {
            TableName: REVIEWS_TABLE,
            Key: {
                id_usuario: user_id,
                id_resenia: resenia_id
            }
        };
        
        const existingReview = await dynamodb.get(params).promise();
        
        if (!existingReview.Item) {
            return {
                statusCode: 404,
                body: JSON.stringify({ message: 'Reseña no encontrada' })
            };
        }
        
        // Verificar que el usuario autenticado sea el propietario de la reseña
        if (existingReview.Item.id_usuario !== user_id) {
            return {
                statusCode: 403,
                body: JSON.stringify({ message: 'No tienes permiso para modificar esta reseña' })
            };
        }

        // Proceder con la actualización de la reseña
        const updateParams = {
            TableName: REVIEWS_TABLE,
            Key: {
                id_usuario: user_id,
                id_resenia: resenia_id
            },
            UpdateExpression: 'set calificacion = :calificacion, comentario = :comentario',
            ExpressionAttributeValues: {
                ':calificacion': calificacion,
                ':comentario': comentario
            },
            ReturnValues: 'ALL_NEW'
        };

        const updatedReview = await dynamodb.update(updateParams).promise();
        
        return {
            statusCode: 200,
            body: JSON.stringify({
                message: 'Reseña actualizada con éxito',
                updated_resenia: updatedReview.Attributes
            })
        };
        
    } catch (error) {
        console.error(error);
        return {
            statusCode: 500,
            body: JSON.stringify({ message: 'Ocurrió un error al modificar la reseña' })
        };
    }
};



    