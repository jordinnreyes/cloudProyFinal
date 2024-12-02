const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

const DESTINOS_TABLE = process.env.DESTINOS_TABLE;

exports.handler = async (event) => {
    console.log(event);

    let data;
    try {
        data = event.body ? (typeof event.body === "string" ? JSON.parse(event.body) : event.body) : null;
    } catch (error) {
        return {
            statusCode: 400,
            body: JSON.stringify({
                message: "Body no es un JSON válido"
            }),
        };
    }

    try {
        // Si no se proporcionan datos en el cuerpo, realizar un escaneo completo
        if (!data || !data.id_destino) {
            const params = {
                TableName: DESTINOS_TABLE,
            };

            const result = await dynamodb.scan(params).promise();

            return {
                statusCode: 200,
                body: JSON.stringify({
                    message: 'Destinos obtenidos con éxito',
                    destinos: result.Items,
                }),
            };
        }

        // Si se proporciona un id_destino, obtener un destino específico
        const { id_destino, ciudad } = data;
        const params = {
            TableName: DESTINOS_TABLE,
            Key: {
                id_destino: id_destino,
                ciudad: ciudad,
            },
        };

        const result = await dynamodb.get(params).promise();

        if (!result.Item) {
            return {
                statusCode: 404,
                body: JSON.stringify({ message: 'Destino no encontrado' }),
            };
        }

        return {
            statusCode: 200,
            body: JSON.stringify({
                message: 'Destino obtenido con éxito',
                destino: result.Item,
            }),
        };
    } catch (error) {
        console.error(error);
        return {
            statusCode: 500,
            body: JSON.stringify({ message: 'Ocurrió un error al obtener los destinos' }),
        };
    }
};
