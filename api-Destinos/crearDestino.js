const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();
const { randomUUID } = require('crypto');

// Crea una instancia del cliente Lambda
const lambda = new AWS.Lambda();

const DESTINOS_TABLE = process.env.DESTINOS_TABLE;

exports.handler = async (event) => {
    console.log("Contenido de event.body:", event.body);

    // Intentamos parsear el cuerpo de la solicitud

    let data;
    if (!event.body) {
        console.error("Body no existe en el evento");
        return {
            statusCode: 400,
            body: JSON.stringify({ message: "Body no existe en el evento" })
        };
    }
    
    // Si `event.body` es un string, intenta parsearlo
    if (typeof event.body === "string") {
        data = JSON.parse(event.body);
    } else if (typeof event.body === "object") {
        data = event.body;
    } else {
        console.error("Body no es un JSON válido ni un objeto:", event.body);
        return {
            statusCode: 400,
            body: JSON.stringify({ message: "Body no es un JSON válido ni un objeto" })
        };
    }
    
    // Verifica que `data` sea un objeto válido
    if (!data || typeof data !== "object") {
        console.error("Body parseado no es un objeto válido:", data);
        return {
            statusCode: 400,
            body: JSON.stringify({ message: "Body parseado no es un objeto válido" })
        };
    }
    
    console.log("Cuerpo de la solicitud parseado con éxito:", data);
    // Continúa con el procesamiento de `data`



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
        

        // Procesar la solicitud del destino
        const item = {
            //tenant_id: data.tenant_id, // Faltaría validar el tenant_id
            id_destino: randomUUID(),
            ciudad: data.ciudad,
            pais: data.pais,
            descripcion: data.descripcion,
            popularidad: data.popularidad
        };

        // Guardar el destino en DynamoDB
        await dynamodb.put({
            TableName: DESTINOS_TABLE,
            Item: item
        }).promise();

        return {
            statusCode: 201,
            body: JSON.stringify({ 
                message: 'destino creada con éxito',
                id_destino: item.id_destino
             })
        };
    } catch (error) {
        console.error("Error al guardar la destino en DynamoDB:",error);
        return {
            statusCode: 500,
            body: JSON.stringify({ message: 'Ocurrió un error al crear el destino' })
        };
    }
};

