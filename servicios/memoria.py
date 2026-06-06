import os
import httpx
from typing import Any, Optional
from dotenv import load_dotenv

load_dotenv()

_BASE_URL = os.getenv("MEMORIA_URL", "http://localhost:4201")
_TIMEOUT = float(os.getenv("MCP_TIMEOUT", 30.0))


async def guardar_historial(id_sesion: int, tipo: str, texto: str) -> Optional[Any]:
    """
    Guarda un mensaje en el historial de la sesión.

    POST /redis/guardar-historial
    Body: { id_sesion, tipo, texto }
    """
    payload = {"id_sesion": id_sesion, "tipo": tipo, "texto": texto}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{_BASE_URL}/redis/guardar-historial",
                json=payload,
                timeout=_TIMEOUT,
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"[memoria] Error en guardar_historial: {e}")
        return None


async def leer_historial(id_sesion: int) -> Optional[Any]:
    """
    Lee el historial completo de una sesión.

    GET /redis/leer-historial/{id_sesion}
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{_BASE_URL}/redis/leer-historial/{id_sesion}",
                timeout=_TIMEOUT,
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"[memoria] Error en leer_historial: {e}")
        return None


async def cachear_respuesta_llm(clave: str, respuesta: str, ttl: int = 3600) -> Optional[Any]:
    """
    Almacena en caché la respuesta de un modelo LLM bajo una clave dada.

    POST /redis/cachear-llm
    Body: { clave, respuesta, ttl }
    """
    payload = {"clave": clave, "respuesta": respuesta, "ttl": ttl}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{_BASE_URL}/redis/cachear-llm",
                json=payload,
                timeout=_TIMEOUT,
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"[memoria] Error en cachear_respuesta_llm: {e}")
        return None


async def obtener_cache_llm(clave: str) -> Optional[Any]:
    """
    Obtiene la respuesta LLM cacheada para una clave.

    GET /redis/obtener-cache-llm/{clave}
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{_BASE_URL}/redis/obtener-cache-llm",
                json={"clave": clave},
                timeout=_TIMEOUT,
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"[memoria] Error en obtener_cache_llm: {e}")
        return None


async def validar_rate_limit(id_sesion: int, limite: int = 10, ventana: int = 60) -> Optional[Any]:
    """
    Valida si la sesión ha superado el límite de solicitudes en la ventana de tiempo dada.

    GET /redis/rate-limit/{id_sesion}?limite={limite}&ventana={ventana}
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{_BASE_URL}/redis/rate-limit/{id_sesion}",
                params={"limite": limite, "ventana": ventana},
                timeout=_TIMEOUT,
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"[memoria] Error en validar_rate_limit: {e}")
        return None
