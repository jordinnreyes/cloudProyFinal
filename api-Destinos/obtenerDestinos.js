const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();
const lambda = new AWS.Lambda();

const DESTINOS_TABLE = process.env.DESTINOS_TABLE;

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

    const id_destino = data.id_destino;  // El id_destino que se desea consultar
    const ciudad = data.ciudad; 
    // Verificar que el id_destino sea válido
    if (!id_destino) {
        return {
            statusCode: 400,
            body: JSON.stringify({
                message: 'El id_destino es obligatorio'
            })
        };
    }


    try {
        // Parámetros de escaneo de la tabla
        const params = {
            TableName: DESTINOS_TABLE,
            Key: {
                id_destino: id_destino, 
                ciudad: ciudad,
            },
        };

        // Realizar el escaneo para obtener todos los destinos
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
                message: 'Destinos obtenidos con éxito',
                destinos: result.Item,
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
