import os
import json
import httpx
from typing import Optional

from langsmith.run_helpers import trace

MCP_URL = os.getenv(
    "MCP_URL",
    "http://localhost:65089/api/mcp"
)

# Configurar timeout por defecto (en segundos)
DEFAULT_TIMEOUT = float(os.getenv("MCP_TIMEOUT", "30.0"))


async def mcp_discover_tools(timeout: Optional[float] = None):

    payload = {
        "jsonrpc": "2.0",
        "id": "discovery",
        "method": "tools/list",
        "params": {}
    }

    # Usar timeout proporcionado o el valor por defecto
    request_timeout = timeout if timeout is not None else DEFAULT_TIMEOUT

    async with httpx.AsyncClient(timeout=request_timeout) as client:
        try:
            resp = await client.post(
                MCP_URL,
                json=payload
            )

             # Debug: Imprimir la URL a la que se está conectando
            resp.raise_for_status()

            return resp.json()
        except httpx.TimeoutException:
            # Manejar timeout específicamente
            raise Exception(f"Timeout al conectar con el servicio MCP después de {request_timeout} segundos")
        except httpx.RequestError as req_error:
            # Manejar otros errores de red
            raise Exception(f"Error de red al conectar con el servicio MCP: {req_error}")
        except Exception as ex:
            # Manejar cualquier otro error
            raise Exception(f"Error inesperado al obtener las herramientas: {ex}")

async def mcp_invoke_tool_dynamic(
    server_url: str,
    original_tool_name: str,
    params: dict,
    timeout: Optional[float] = None
):
    """
    Invoca una herramienta MCP en un servidor específico
    
    Args:
        server_url: URL del servidor MCP
        original_tool_name: Nombre original de la herramienta
        params: Parámetros para la herramienta
        timeout: Timeout para la solicitud
    """
    # # Manejar herramientas internas de procesamiento de archivos
    # if server_url.startswith("internal://"):
    #     return await _invoke_internal_tool(original_tool_name, params)
    
    # Usar timeout proporcionado o el valor por defecto
    request_timeout = timeout if timeout is not None else DEFAULT_TIMEOUT

    with trace(
        name=original_tool_name,
        run_type="tool",
        inputs=params,
        metadata={
            "tool_type": "mcp_dynamic",
            "transport": "http",
            "mcp_url": server_url,
            "timeout": request_timeout
        }
    ) as run:

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": original_tool_name,
                "arguments": params
            }
        }

        try:
            async with httpx.AsyncClient(timeout=request_timeout) as client:

                resp = await client.post(
                    server_url,
                    json=payload
                )

                resp.raise_for_status()

                result = resp.json()
                print(f"[MCP DEBUG] tool={original_tool_name} raw_response={json.dumps(result)[:2000]}")

                # Extraer el contenido textual de la respuesta JSON-RPC de MCP
                if "error" in result:
                    error_msg = f"Error MCP: {result['error']}"
                    run.end(error=error_msg)
                    raise Exception(error_msg)

                content_blocks = result.get("result", {}).get("content", [])
                text_parts = [
                    block.get("text", "")
                    for block in content_blocks
                    if block.get("type") == "text"
                ]
                extracted = "\n".join(text_parts) if text_parts else str(result)

                run.end(outputs={"result": extracted})

                return extracted

        except httpx.TimeoutException:
            error_msg = f"Timeout al invocar la herramienta '{original_tool_name}' después de {request_timeout} segundos"
            run.end(
                error=error_msg
            )
            raise Exception(error_msg)
        except httpx.HTTPStatusError as http_error:
            error_msg = f"Error HTTP {http_error.response.status_code} al invocar la herramienta '{original_tool_name}': {http_error.response.text}"
            run.end(
                error=error_msg
            )
            raise Exception(error_msg)
        except httpx.RequestError as req_error:
            error_msg = f"Error de red al invocar la herramienta '{original_tool_name}': {req_error}"
            run.end(
                error=error_msg
            )
            raise Exception(error_msg)
        except Exception as ex:
            error_msg = f"Error inesperado al invocar la herramienta '{original_tool_name}': {ex}"
            run.end(
                error=error_msg
            )
            raise Exception(error_msg)