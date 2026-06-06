from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from pathlib import Path
from dotenv import load_dotenv
import os

from servicios.memoria import obtener_cache_llm, cachear_respuesta_llm

env_path = Path(__file__).resolve().parents[2]
load_dotenv()

modelo_ia_liviana = ChatOpenAI(
    model=os.getenv("IA_LIVIANA_MODEL", ""),
    base_url=os.getenv("IA_LIVIANA_URL", ""),
    api_key=os.getenv("IA_LIVIANA_API_KEY", ""),
    temperature=0.0,
    streaming=True
)


async def consultar_ia_liviana_node(state: Dict[str, Any]) -> Dict[str, Any]:

    cache_key = f"ia_liviana:{state.get('session_id')}:{state.get('cleaned_text')}"

    cached_response = await obtener_cache_llm(cache_key)
    if cached_response:
        print(f"Respuesta obtenida de caché para clave: {cache_key} // {cached_response.get('respuesta', '')}")
        return {
            **state,
            "respuesta_ia": cached_response.get("respuesta", "")
        }

    session_data = state.get("session_data") or {}
    instrucciones = session_data.get("Instrucciones") or "Eres un asistente útil. Conversa con el usuario de manera clara y concisa."

    messages = [SystemMessage(content=instrucciones)]

    messages.append(HumanMessage(content=state.get("cleaned_text", "")))

    response = await modelo_ia_liviana.ainvoke(messages)

    print(f"Respuesta IA Liviana: {response.content if response else 'No response'}")

    if response and response.content:
        await cachear_respuesta_llm(cache_key, response.content)
    
    return {
        **state,
        "respuesta_ia": response.content if response else ""
    }
