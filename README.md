# API con FastAPI, LangGraph, LangChain y LangSmith

Esta es una API construida con FastAPI que integra LangGraph, LangChain y LangSmith para crear workflows de procesamiento de lenguaje natural.

## Características

- API REST construida con FastAPI
- Workflows definidos con LangGraph
- Integración con modelos de IA (xAI Grok)
- Seguimiento con LangSmith
- Streaming de respuestas en tiempo real
- Guardado de historial de chat

## Estructura del proyecto

```
├── main.py                 # Punto de entrada de la API
├── .env                    # Variables de entorno
├── requirements.txt        # Dependencias del proyecto
├── workflows/              # Directorio de workflows
│   ├── main_workflow.py    # Workflow principal
│   └── nodos/              # Nodos del workflow
│       ├── limpiar_string.py
│       ├── consultar_ia.py
│       └── guardar_historial.py
```

## Configuración

1. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Configurar las variables de entorno en el archivo `.env`

## Variables de entorno

```
MCP_TIMEOUT="30.0"
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGSMITH_API_KEY="tu-api-key-aqui"
LANGSMITH_PROJECT="TEST-ML"
USER_FLOW_URL="http://apipy:8000/user-flow"
CHAT_HISTORY_URL="http://apipy:8000/chat-history"
SAVE_CHAT_URL="http://apipy:8000/save-chat"
IA_API_KEY="tu-api-key-de-xai"
IA_MODEL="grok-4.20-0309-reasoning"
IA_URL="https://api.x.ai/v1"
IA_REQUEST_TIMEOUT=90
IA_MAX_TOKENS=180
```

## Workflow

El workflow principal consta de 3 nodos:

1. **limpiar_string**: Limpia el texto de entrada
2. **consultar_ia**: Consulta al modelo de IA y devuelve la respuesta mediante streaming
3. **guardar_historial**: Guarda el mensaje en el historial

## Endpoints

- `GET /` - Verifica que la API esté funcionando
- `POST /invoke` - Ejecuta el workflow y devuelve la respuesta de la IA mediante streaming

## Ejemplo de uso

### En Linux/Mac:
```bash
curl -N -X POST http://localhost:8006/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "text": "hola",
    "IdUsuario": 13,
    "IdContexto": 4
  }'
```

### En Windows (PowerShell):
```powershell
Invoke-WebRequest -Uri "http://localhost:8006/invoke" -Method POST -ContentType "application/json" -Body '{"text": "hola", "IdUsuario": 13, "IdContexto": 4}'
```

### En Python:
```python
import requests
import json

url = "http://localhost:8006/invoke"
data = {
    "text": "hola",
    "IdUsuario": 13,
    "IdContexto": 4
}

response = requests.post(url, json=data, stream=True)
for chunk in response.iter_lines():
    if chunk:
        print(chunk.decode('utf-8'))
```

## Ejecutar la aplicación

```bash
uvicorn main:app --reload --port 8006
```

## Scripts de prueba

El proyecto incluye varios scripts de prueba:

- `test_nodo_ia.py`: Prueba el nodo de consultar IA directamente
- `test_workflow.py`: Prueba el workflow completo
- `test_streaming.py`: Prueba el streaming de la API

Para ejecutarlos:
```bash
python test_nodo_ia.py
python test_workflow.py
python test_streaming.py
```