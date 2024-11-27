const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();
const lambda = new AWS.Lambda();

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

    // Proceso - Eliminar la reseña en DynamoDB
    const resenia_id = data.resenia_id;  // El ID de la reseña que se desea eliminar
    
    try {
        // Verificar si la reseña existe en la base de datos
        const params = {
            TableName: REVIEWS_TABLE,
            Key: {
                id_usuario: user_id,    // Clave de partición
                id_resenia: resenia_id  // Clave de ordenación
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
                body: JSON.stringify({ message: 'No tienes permiso para eliminar esta reseña' })
            };
        }

        // Proceder con la eliminación de la reseña
        const deleteParams = {
            TableName: REVIEWS_TABLE,
            Key: {
                id_usuario: user_id,
                id_resenia: resenia_id
            }
        };

        await dynamodb.delete(deleteParams).promise();

        return {
            statusCode: 200,
            body: JSON.stringify({
                message: 'Reseña eliminada con éxito'
            })
        };

    } catch (error) {
        console.error(error);
        return {
            statusCode: 500,
            body: JSON.stringify({ message: 'Ocurrió un error al eliminar la reseña' })
        };
    }
};
