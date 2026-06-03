import httpx
import os
from typing import Dict, Any
# from src.state import GraphState
# from src.error_logging import log_error_to_langsmith

import os
from pathlib import Path

from dotenv import load_dotenv
env_path = Path(__file__).resolve().parents[2] 
load_dotenv()


async def obtener_sesion(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node que obtiene la sesión del usuario llamando al endpoint externo
    """
    try:
        # URL del endpoint desde variables de entorno
        url = os.getenv("USER_FLOW_URL")
        
        # Datos a enviar en el request
        payload = {
            "IdUsuario": state["id_usuario"],  # Obtener del state
            "IdContexto": state["id_contexto"]  # Obtener del state
        }
        
        # Realizar la llamada HTTP
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )
            
            # Verificar si la respuesta es exitosa
            response.raise_for_status()
            
            # Parsear la respuesta JSON
            session_data = response.json()
            
            # Retornar el estado actualizado con la información de la sesión
            return {
                "session_data": session_data[0]
            }
            
    except Exception as e:
        print(f"Error al obtener sesión: {e}", state["id_usuario"], state["id_contexto"])
        # Registrar el error en LangSmith
        # log_error_to_langsmith(e, "obtener_sesion", {
        #     "IdUsuario": state.get("id_usuario", 1),
        #     "IdContexto": state.get("id_contexto", 3)
        # })
        
        # Retornar el estado sin modificar en caso de error
        return {
            "session_data": None
        }