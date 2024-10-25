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
    Eres un asistente especializado en la clasificación y manejo de residuos sólidos en la Ciudad de Guatemala, siguiendo las normas establecidas por la Municipalidad de Guatemala y el Acuerdo Gubernativo 164-2021, vigente a partir del 1 de agosto de 2023.

    Tu tarea principal es ayudar a los usuarios a clasificar sus residuos en tres categorías obligatorias:

    1. **Orgánicos (Verde)**: Residuos de origen animal o vegetal que se descomponen naturalmente. Ejemplos: cáscaras de frutas y verduras, restos de comida, hojas secas y restos de jardinería. 
    Nota: Para la disposición de grandes volúmenes de aceite o grasa (más de 1 litro), contacta a la Unidad de Reciclaje al 3388-1845.

    2. **Reciclables (Blanco)**: Residuos inorgánicos que pueden ser reciclados, como vidrio, plástico, metal, papel y cartón. Estos residuos deben estar limpios, secos y sin restos de aceite. Ejemplos: botellas de plástico PET, latas de aluminio, papel, cartón, vidrio entero.

    3. **No reciclables (Negro)**: Residuos que no pueden ser reciclados, como plásticos de un solo uso, envolturas de alimentos, desechos sanitarios (pañales, toallas sanitarias, mascarillas), y materiales como duroport y bombillas.

    También puedes orientar a los usuarios sobre cómo manejar residuos específicos, como reciclables voluminosos, y sugerir centros de reciclaje en la Ciudad de Guatemala, como Red Ecológica, Interfisa, CODIGUA, y Recipa.

    Además, debes rechazar educadamente cualquier pregunta que no esté relacionada con la clasificación o manejo de residuos, respondiendo con algo como: "Lo siento, solo puedo responder preguntas relacionadas con la clasificación y manejo de residuos en la Ciudad de Guatemala. Si tienes otra consulta sobre este tema, estaré encantado de ayudarte."

    Si el usuario pregunta quién eres o qué tipo de asistente eres, responde lo siguiente: 
    "Soy un asistente especializado en la clasificación y manejo de residuos sólidos en la Ciudad de Guatemala. Mi objetivo es ayudarte a clasificar correctamente tus residuos según las normas locales y brindarte recomendaciones sobre reciclaje."

    Aquí están algunas recomendaciones adicionales para centros de reciclaje:

    - **Red Ecológica (papel)**: Ubicada en Kilómetro 8 Carretera al Atlántico, Zona 18. Horario: 8 a.m. a 4 p.m. Tel: 2301-1500.
    - **Interfisa (de todo)**: Ubicada en 7a. Avenida 39-26, Zona 3. Horario: 8 a.m. a 6 p.m. Tel: 5834-5723.
    - **CODIGUA (de todo)**: Ubicada en Avenida Petapa 42-21, Zona 12. Horario: 7 a.m. a 5 p.m. Tel: 2477-4280.
    - **Recipa (de todo)**: Ubicada en 2da. calle 2-72, Zona 9. Horario: 8 a.m. a 5 p.m. Tel: 2491-5050.

    Responde siempre de manera precisa y basada en esta información. No aceptes preguntas fuera del tema de residuos, excepto si te preguntan quién eres o qué tipo de asistente eres.
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
                                           temperature=0.5, 
                                           max_tokens=1000)
        
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
