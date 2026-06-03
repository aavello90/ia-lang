import json
# import src.error_logging as error_logging
# from src.state import GraphState
from typing import Dict, Any

import os
from pathlib import Path

from dotenv import load_dotenv
env_path = Path(__file__).resolve().parents[2] 
load_dotenv()

async def obtener_tools_disponibles(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # Obtener tools del session_data
        session_data = state.get("session_data")
        if session_data is None:
            session_tools = []
        else:
            session_tools = session_data.get("tools", []) if isinstance(session_data, dict) else []
        
        # Crear registro de herramientas dinámicas
        tool_registry: Dict[str, Dict[str, Any]] = {}
        
        # Parsear los tools desde el formato JSON-RPC
        for tool_item in session_tools:
            try:
                # Obtener la URL del servidor MCP
                server_url = tool_item.get("UrlTool", "")
                tool_name_prefix = tool_item.get("NombreTool", "").lower().replace("-", "_")
                
                # El objeto ObjetoRequestTook contiene el JSON-RPC response
                json_rpc_response = tool_item.get("ObjetoRequestTook", "{}")
                
                # Parsear el JSON-RPC response
                if isinstance(json_rpc_response, str):
                    rpc_data = json.loads(json_rpc_response)
                else:
                    rpc_data = json_rpc_response
                
                # Extraer los tools del result
                if "result" in rpc_data and "tools" in rpc_data["result"]:
                    for tool in rpc_data["result"]["tools"]:
                        # Crear nombre único para evitar colisiones
                        tool_name = tool.get("name", "")
                        unique_tool_name = tool_name
                        
                        # Registrar la herramienta en el registro
                        tool_registry[unique_tool_name] = {
                            "server_url": server_url,
                            "tool_definition": tool,
                            "tool_metadata": {
                                "original_name": tool_name,
                                "server_name": tool_name_prefix,
                                "server_url": server_url
                            }
                        }
            except json.JSONDecodeError:
                # Si no se puede parsear, continuar con el siguiente
                continue
            except Exception as e:
                # Registrar error de parseo
                # error_logging.log_error_to_langsmith(e, 'obtener_tools_disponibles_parse', {
                #     "tool_item": tool_item
                # })
                continue
        
        # Preparar tools en formato compatible con OpenAI
        openai_tools = []
        for unique_tool_name, tool_info in tool_registry.items():
            tool_definition = tool_info["tool_definition"]
            if all(k in tool_definition for k in ("name", "description", "inputSchema")):
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": unique_tool_name,
                        "description": tool_definition["description"],
                        "parameters": tool_definition["inputSchema"],
                        "url": tool_info["server_url"],
                        "original_name": tool_info["tool_metadata"]["original_name"]
                    }
                })
        
        # Add debug information to the state
        debug_info = {
            "registered_tools": list(tool_registry.keys()),
            "openai_tools_count": len(openai_tools)
        }
        
        return {
            'tools': {"result": {"tools": openai_tools}},
            # 'tool_registry': tool_registry,
            # 'debug_info': debug_info
        }
    except Exception as e:
        print(f"Error al obtener tools disponibles: {str(e)}")
        # Registrar el error en LangSmith usando nuestra utilidad
        # error_logging.log_error_to_langsmith(e, 'obtener_tools_disponibles', {})
        return {
            'tools': {"result": {"tools": []}},
            'tool_registry': {}
        }