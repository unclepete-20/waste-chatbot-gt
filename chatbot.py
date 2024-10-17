import time
import asyncio
from dotenv import load_dotenv
import os
from openai import OpenAI
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from typing import Annotated
import logging

load_dotenv()  # Cargar las variables de entorno desde .env

app = FastAPI()

openai = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Limitar el chat_log a los últimos 20 mensajes
MAX_LOG_LENGTH = 20

chat_log = [{
    'role': 'system',
    'content': """
    Eres un asistente especializado en el manejo de residuos en la Ciudad de Guatemala. Tu objetivo es ayudar a los usuarios a clasificar sus residuos correctamente según las normas establecidas por la Municipalidad de Guatemala.

    A partir del 1 de agosto de 2023, la clasificación secundaria de residuos es obligatoria según el Acuerdo Gubernativo 164-2021. Los residuos deben clasificarse en tres categorías:

    1. Orgánicos (Verde): Residuos de origen animal o vegetal que se descomponen naturalmente, como restos de comida, cáscaras de frutas y verduras, hojas secas y restos de jardinería.
       
    2. Reciclables (Blanco): Residuos inorgánicos que pueden ser reciclados, como vidrio, plástico, metal, papel y cartón. Los reciclables deben estar limpios, secos y sin restos de aceite.

    3. No reciclables (Negro): Residuos que no pueden ser reciclados, como plásticos de un solo uso, envolturas de alimentos, desechos sanitarios y materiales no reciclables como duroport.

    Proporciona información sobre la clasificación correcta de residuos, según su tipo y color de identificación. También puedes sugerir cómo manejar residuos específicos y ofrecer recomendaciones adicionales según las normativas locales. Si los usuarios necesitan más detalles o tienen preguntas específicas sobre la disposición de residuos en grandes cantidades o especiales, oriéntalos al contacto adecuado.
    """
}]

# Configuración básica del logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Endpoint para el mensaje de bienvenida o "¿Quién eres?"
@app.post("/whoami")
async def whoami():
    # Añadir el mensaje de introducción al chat_log para iniciar la conversación
    bienvenida_log = chat_log.copy()
    bienvenida_log.append({'role': 'user', 'content': "¿Quién eres?"})

    try:
        # Capturar el tiempo de inicio
        start_time = time.time()

        # Llamada asincrónica a la API de OpenAI para generar el mensaje de bienvenida
        response = await asyncio.to_thread(openai.chat.completions.create, 
                                           model='gpt-3.5-turbo',
                                           messages=bienvenida_log,
                                           temperature=0.7, 
                                           max_tokens=200)
        
        # Capturar el tiempo de finalización
        end_time = time.time()

        # Calcular el tiempo de respuesta
        response_time = end_time - start_time

        # Extraer la respuesta del asistente
        bot_response = response.choices[0].message.content

        # Devolver la respuesta en formato estructurado
        return {
            "status": "success",
            "bot_response": bot_response,
            "response_time": f"{response_time:.2f} segundos"
        }

    except Exception as e:
        logger.error(f"Error en la API: {e}")
        error_message = "Lo siento, ocurrió un problema al procesar tu solicitud. Por favor intenta de nuevo más tarde."
        return JSONResponse(content={"error": str(e), "message": error_message}, status_code=500)

# Endpoint para el flujo normal del chatbot
@app.post("/chat")
async def chat(user_input: Annotated[str, Form()]):
    logger.info(f"Solicitud recibida: {user_input}")

    # Validar que el input no esté vacío
    if not user_input.strip():
        logger.warning("Se intentó enviar un mensaje vacío")
        return JSONResponse(content={"message": "Por favor, ingresa un mensaje válido."}, status_code=400)

    # Agregar el mensaje del usuario al chat_log
    chat_log.append({'role': 'user', 'content': user_input})
    
    # Limitar el chat_log a los últimos mensajes para evitar que crezca indefinidamente
    if len(chat_log) > MAX_LOG_LENGTH:
        chat_log.pop(1)  # Mantener el primer mensaje del sistema y eliminar el mensaje más antiguo del usuario
    
    try:
        # Capturar el tiempo de inicio
        start_time = time.time()

        # Llamada asincrónica a la API de OpenAI
        response = await asyncio.to_thread(openai.chat.completions.create, 
                                           model='gpt-3.5-turbo',
                                           messages=chat_log,
                                           temperature=0.7, 
                                           max_tokens=200)
        
        # Capturar el tiempo de finalización
        end_time = time.time()

        # Calcular el tiempo de respuesta
        response_time = end_time - start_time

        # Extraer la respuesta del asistente
        bot_response = response.choices[0].message.content

        # Agregar la respuesta al chat_log
        chat_log.append({'role': 'assistant', 'content': bot_response})

        logger.info(f"Respuesta del bot: {bot_response}")
        logger.info(f"Tiempo de respuesta: {response_time:.2f} segundos")

        # Devolver la respuesta en formato estructurado
        return {
            "status": "success",
            "user_message": user_input,
            "bot_response": bot_response,
            "response_time": f"{response_time:.2f} segundos"
        }

    except Exception as e:
        logger.error(f"Error en la API: {e}")
        error_message = "Lo siento, ocurrió un problema al procesar tu solicitud. Por favor intenta de nuevo más tarde."
        return JSONResponse(content={"error": str(e), "message": error_message}, status_code=500)
