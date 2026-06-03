from typing import Dict, Any
from datetime import datetime
import httpx
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

async def guardar_historial_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Nodo para guardar el mensaje en el historial.
    """
    session_id = state.get("session_id", "")
    texto_limpio = state.get("cleaned_text", "")
    
    # Preparar los datos para guardar el mensaje del usuario
    datos_usuario = {
        "IdSesion": session_id,
        "Tipo": "usuario",
        "TextoSistema": "",  # El texto del sistema no aplica para mensajes de usuario
        "Texto": texto_limpio,
        "Fecha": datetime.now().isoformat()
    }
    
    # Guardar el mensaje del usuario
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                os.getenv("SAVE_CHAT_URL", "http://apipy:8000/save-chat"),
                json=datos_usuario,
                timeout=float(os.getenv("MCP_TIMEOUT", 30.0))
            )
    except Exception as e:
        print(f"Error al guardar mensaje de usuario: {e}")
    
    # Guardar la respuesta de la IA (esto se hará después de obtener la respuesta)
    # Por ahora solo retornamos el estado
    return {
        "session_id": session_id,
        "texto_limpio": texto_limpio,
        "respuesta_ia": state.get("respuesta_ia", "")
    }