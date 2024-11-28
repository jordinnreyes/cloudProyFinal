const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();
const lambda = new AWS.Lambda();
//const { DateTime } = require('luxon');


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

    // Aquí obtenemos el `user_id` de la respuesta de `validarTokenAcceso`
    const user_id = parsedResponse.body?.user_id;
    if (!user_id) {
        return {
            statusCode: 403,
            body: JSON.stringify({
                status: 'Token inválido o usuario no autorizado'
            })
        };
    }

    // Fin - Proteger el Lambda  - El token ha sido validado


    


    // Proceso - Modificar la reseña en DynamoDB
    const resenia_id = data.resenia_id;  // El ID de la reseña que se desea modificar
    const { calificacion, comentario } = data;  // Nuevos valores de calificación y comentario
    
    try {
        // Verificar si la reseña existe en la base de datos
        const params = {
            TableName: REVIEWS_TABLE,
            Key: {
                user_id: user_id,
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
        if (existingReview.Item.user_id !== user_id) {
            return {
                statusCode: 403,
                body: JSON.stringify({ message: 'No tienes permiso para modificar esta reseña' })
            };
        }

        // Proceder con la actualización de la reseña
        const updateParams = {
            TableName: REVIEWS_TABLE,
            Key: {
                user_id: user_id,
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
        console.error("Error en DynamoDB:", error);
        return {
            statusCode: 500,
            body: JSON.stringify({ message: 'Ocurrió un error al modificar la reseña' })
        };
    }
};



    
