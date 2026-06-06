from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
import httpx
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from workflows.utils.mcp_client import mcp_invoke_tool_dynamic

env_path = Path(__file__).resolve().parents[2]
load_dotenv()

modelo_ia = ChatOpenAI(
    model=os.getenv("IA_MODEL", ""),
    base_url=os.getenv("IA_URL", ""),
    api_key=os.getenv("IA_API_KEY", ""),
    temperature=0.0,
    streaming=True
)


async def consultar_ia_node(state: Dict[str, Any]) -> Dict[str, Any]:
    # Obtener tools del state (construidas por obtener_tools_disponibles)
    raw_tools = state.get("tools", {}).get("result", {}).get("tools", [])

    # Separar tools limpias (para bind al modelo) y mapas de URL/nombre original (para ejecución)
    clean_tools = []
    url_map = {}
    original_name_map = {}

    for tool_def in raw_tools:
        func = tool_def.get("function", {})
        name = func.get("name", "")
        if not name:
            continue

        url_map[name] = func.get("url", "")
        original_name_map[name] = func.get("original_name", name)

        clean_tools.append({
            "type": "function",
            "function": {
                "name": name,
                "description": func.get("description", ""),
                "parameters": func.get("parameters", {})
            }
        })

    # Usar instrucciones del session_data si están disponibles
    session_data = state.get("session_data") or {}
    instrucciones = session_data.get("Instrucciones") or "Eres un asistente útil. Conversa con el usuario de manera clara y concisa."

    messages = [SystemMessage(content=instrucciones)]

    # Construir el mensaje del usuario: texto + archivo si existe
    file_data = state.get("file_data")
    if file_data and file_data.get("base64"):
        content_type = file_data.get("content_type", "application/octet-stream")
        filename = file_data.get("filename", "archivo")

        if content_type.startswith("image/"):
            # Imagen: enviar inline como image_url
            user_content = [
                {"type": "text", "text": state.get("cleaned_text", "")},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{content_type};base64,{file_data['base64']}"
                    },
                },
            ]
            messages.append(HumanMessage(content=user_content))
        else:
            # PDF / Word: invocar la tool de conversión primero y usar el resultado como contexto
            tool_name_map = {
                "application/pdf": "convert_pdf",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "convert_word",
                "application/msword": "convert_word",
            }
            convert_tool_original = tool_name_map.get(content_type, "convert_pdf")

            print(f"[PDF DEBUG] content_type={content_type} buscando tool={convert_tool_original}")
            print(f"[PDF DEBUG] original_name_map={original_name_map}")
            print(f"[PDF DEBUG] url_map={url_map}")

            # Buscar la URL de la tool de conversión en url_map (por nombre original)
            convert_url = ""
            convert_unique_name = ""
            for unique_name, orig in original_name_map.items():
                if orig == convert_tool_original:
                    convert_url = url_map.get(unique_name, "")
                    convert_unique_name = unique_name
                    break

            print(f"[PDF DEBUG] convert_url={convert_url} convert_unique_name={convert_unique_name}")

            file_content_text = ""
            if convert_url:
                try:
                    file_content_text = await mcp_invoke_tool_dynamic(
                        convert_url,
                        convert_tool_original,
                        {"file_content": file_data["base64"]}
                    )
                except Exception as e:
                    file_content_text = f"[Error al procesar {filename}: {str(e)}]"
            else:
                file_content_text = f"[Tool de conversión para {content_type} no disponible]"

            user_text = (
                f"{state.get('cleaned_text', '')}\n\n"
                f"[Contenido extraído de {filename}]:\n{file_content_text}"
            )
            messages.append(HumanMessage(content=user_text))
    else:
        messages.append(HumanMessage(content=state.get("cleaned_text", "")))

    # Bindear tools al modelo si hay disponibles
    model = modelo_ia.bind_tools(clean_tools) if clean_tools else modelo_ia

    # Agent loop: invocar → revisar tool calls → ejecutar → repetir
    response = None
    max_iterations = 5

    for _ in range(max_iterations):
        response = await model.ainvoke(messages)
        messages.append(response)

        if not response.tool_calls:
            break

        # Ejecutar cada tool call
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_call_id = tool_call["id"]
            url = url_map.get(tool_name, "")
            original_name = original_name_map.get(tool_name, tool_name)

            print(f"Ejecutando tool: {tool_name} (original: {original_name}) con args: {tool_args} en URL: {url}")

            try:
                tool_result = await mcp_invoke_tool_dynamic(url, original_name, tool_args)
            except Exception as e:
                tool_result = f"Error al ejecutar la herramienta '{tool_name}': {str(e)}"

            messages.append(ToolMessage(
                content=tool_result,
                tool_call_id=tool_call_id
            ))

    return {
        **state,
        "respuesta_ia": response.content if response else ""
    }