from typing import Dict, Any
import re

def limpiar_string_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Nodo para limpiar el texto de entrada.
    """
    # Adaptar al nuevo formato de entrada (acepta tanto minúsculas como mayúsculas)
    texto = state.get("text", "")
    id_usuario = state.get("id_usuario") or state.get("IdUsuario", "")
    id_contexto = state.get("id_contexto") or state.get("IdContexto", "")
    
    # Eliminar espacios extra al inicio y al final
    texto_limpio = texto.strip()
    
    # Eliminar múltiples espacios consecutivos
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio)
    
    # Eliminar caracteres especiales no deseados (manteniendo letras, números y puntuación básica)
    texto_limpio = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\/]', '', texto_limpio)
    
    # Crear un session_id basado en id_usuario e id_contexto
    session_id = f"{id_usuario}_{id_contexto}"
    
    return {
        "cleaned_text": texto_limpio,
        "session_id": session_id,
        "id_usuario": id_usuario,
        "id_contexto": id_contexto
    }