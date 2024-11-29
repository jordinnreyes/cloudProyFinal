const AWS = require('aws-sdk');
const lambda = new AWS.Lambda();
const dynamodb = new AWS.DynamoDB.DocumentClient();

const DESTINOS_TABLE = process.env.DESTINOS_TABLE;

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
            FunctionName: 'servicio-vuelos-r-dev-validarToken', // Nombre del Lambda Python
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

    let parsedResponse;
    try {
        parsedResponse = JSON.parse(validationResponse.Payload); // Parsea el Payload principal
        parsedResponse.body = JSON.parse(parsedResponse.body);  // Parsea el body interno
    } catch (error) {
        console.error("Error al parsear la respuesta de validación:", error);
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

    // Fin - Proteger el Lambda  - El token ha sido validado




    

    try {
        

        const params = {
            TableName: DESTINOS_TABLE,
            Key: {
                id_destino: data.id_destino,
                ciudad: data.ciudad
            }
        };

        const existingDestino = await dynamodb.get(params).promise();

        if (!existingDestino.Item) {
            return {
                statusCode: 404,
                body: JSON.stringify({ message: 'Destino no encontrada' })
            };
        }

        // Proceder con la eliminación de la Destino
        const deleteParams = {
            TableName: DESTINOS_TABLE,
            Key: {
                id_destino: data.id_destino,
                ciudad: data.ciudad
            }
        };

        await dynamodb.delete(deleteParams).promise();

        return {
            statusCode: 200,
            body: JSON.stringify({ message: 'Destino eliminado con éxito' })
        };
    } catch (error) {
        console.error(error);
        return {
            statusCode: 500,
            body: JSON.stringify({ message: 'Ocurrió un error al eliminar Destinoa', error: error.message })
        };
    }
};

