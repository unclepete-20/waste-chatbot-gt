# FastAPI Chatbot for Waste Management in Guatemala City

Este proyecto implementa un chatbot basado en **FastAPI** que ayuda a los usuarios a clasificar sus residuos en la Ciudad de Guatemala, proporcionando información basada en las normativas municipales. El chatbot utiliza el modelo GPT-3.5 de OpenAI para generar respuestas dinámicas a las preguntas de los usuarios.

## Características

- **Generación dinámica de respuestas**: Usa la API de OpenAI para generar respuestas inteligentes basadas en las normas de clasificación de residuos.
- **Mensaje de bienvenida**: Un endpoint dedicado (`/whoami`) proporciona una respuesta dinámica cuando los usuarios preguntan "¿Quién eres?" o requieren una introducción.
- **Interfaz de chatbot**: Un endpoint general (`/chat`) permite a los usuarios hacer preguntas sobre la clasificación de residuos, y el chatbot responde según las normativas locales.
- **Registro de actividad**: Se registra cada solicitud y respuesta, así como cualquier error, para facilitar la depuración y el monitoreo.

## Estructura del Proyecto

- `main.py`: El archivo principal de la aplicación FastAPI donde se definen los endpoints.
- `requirements.txt`: Las dependencias del proyecto.
- `Procfile`: Instrucciones para ejecutar la aplicación con servidores como Uvicorn.

## Endpoints

### `/whoami` (POST)

Este endpoint genera una respuesta dinámica cuando el usuario solicita una introducción o pregunta "¿Quién eres?".

**Ejemplo de Solicitud:**

```bash
curl -X POST http://127.0.0.1:8000/whoami
```

**Ejemplo de Respuesta:**

```json
{
  "status": "success",
  "bot_response": "Soy un asistente virtual especializado en el manejo de residuos en la Ciudad de Guatemala...",
  "response_time": "1.23 segundos"
}
```

### `/chat` (POST)

Este endpoint permite a los usuarios enviar preguntas generales sobre la gestión de residuos, y el chatbot genera una respuesta basada en las normativas.

**Ejemplo de Solicitud:**

```bash
curl -X POST http://127.0.0.1:8000/chat      -H "Content-Type: application/x-www-form-urlencoded"      -d "user_input=¿Cómo debo clasificar los residuos orgánicos?"
```

**Ejemplo de Respuesta:**

```json
{
  "status": "success",
  "user_message": "¿Cómo debo clasificar los residuos orgánicos?",
  "bot_response": "Los residuos orgánicos se clasifican en la categoría verde y comprenden restos de comida...",
  "response_time": "1.45 segundos"
}
```

## Instalación

### Requisitos Previos

- **Python 3.7+**
- **Clave API de OpenAI** (Regístrate en [OpenAI](https://beta.openai.com/signup/))

### Instrucciones de Instalación

1. Clona el repositorio:

   ```bash
   git clone https://github.com/tuusuario/fastapi-waste-management-chatbot.git
   cd fastapi-waste-management-chatbot
   ```

2. Crea y activa un entorno virtual:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Para Windows: .\venv\Scripts\activate
   ```

3. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Configura tu clave API de OpenAI:

   Crea un archivo `.env` en la raíz del proyecto y añade tu clave API de OpenAI:

   ```plaintext
   OPENAI_API_KEY=tu-clave-api-aqui
   ```

### Ejecución de la Aplicación

Puedes ejecutar el servidor FastAPI localmente utilizando Uvicorn:

```bash
uvicorn main:app --reload
```

La API estará disponible en `http://127.0.0.1:8000`.

### Pruebas de los Endpoints

- **Probar el mensaje de bienvenida**:
  
  ```bash
  curl -X POST http://127.0.0.1:8000/whoami
  ```

- **Probar la funcionalidad del chatbot**:

  ```bash
  curl -X POST http://127.0.0.1:8000/chat        -H "Content-Type: application/x-www-form-urlencoded"        -d "user_input=¿Cómo debo clasificar los residuos orgánicos?"
  ```

### Registro de Actividades

La aplicación utiliza el módulo `logging` de Python para registrar información sobre las solicitudes y respuestas. Los registros se mostrarán en la salida de la consola cuando ejecutes la aplicación localmente.

### Manejo de Errores

Si ocurre algún error durante el procesamiento de la solicitud o respuesta, la aplicación devolverá un código de estado `500` con un mensaje de error en formato JSON.

## Licencia

Este proyecto está licenciado bajo la Licencia GPL 3.0. Consulta el archivo [LICENSE](LICENSE) para más detalles.

## Contribuciones

Las contribuciones son bienvenidas. Para cambios importantes, abre primero un issue para discutir lo que te gustaría cambiar.

---

