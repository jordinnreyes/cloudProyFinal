const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();
const lambda = new AWS.Lambda();

const REVIEWS_TABLE = process.env.REVIEWS_TABLE;

exports.handler = async (event) => {
    console.log(event);
    

    let data;
    try {
        data = typeof event.body === "string" ? JSON.parse(event.body) : event.body;
    } catch (error) {
        return {
            statusCode: 400,
            body: JSON.stringify({
                message: "Body no es un JSON válido"
            })
        };
    }
    
    const id_vuelo = data.id_vuelo;  // El id_vuelo que se desea consultar
    // Verificar que el id_vuelo sea válido
    if (!id_vuelo) {
        return {
            statusCode: 400,
            body: JSON.stringify({
                message: 'El id_vuelo es obligatorio'
            })
        };
    }

    try {
        

        
        // Realizar la consulta para obtener las reseñas de un vuelo usando el GSI VueloIndex
        const params = {
            TableName: REVIEWS_TABLE,
            IndexName: 'VueloIndex', // Especifica el nombre del índice secundario global
            KeyConditionExpression: "id_vuelo = :id_vuelo", // Filtra por el id_vuelo
            ExpressionAttributeValues: {
                ":id_vuelo": id_vuelo
            }
        };


        const result = await dynamodb.query(params).promise();

        if (!result.Items || result.Items.length === 0) {
            return {
                statusCode: 404,
                body: JSON.stringify({ message: 'No se encontraron reseñas para este vuelo' })
            };
        }

        return {
            statusCode: 200,
            body: JSON.stringify({
                message: 'Reseñas obtenidas con éxito',
                reseñas: result.Items
            })
        };

    } catch (error) {
        console.error(error);
        return {
            statusCode: 500,
            body: JSON.stringify({
                message: 'Ocurrió un error al obtener las reseñas'
            })
        };
    }
};
