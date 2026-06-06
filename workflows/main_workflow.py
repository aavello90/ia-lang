from typing import Dict, Any, AsyncGenerator
from langgraph.graph import StateGraph, START, END
from workflows.nodos.clasificacion import clasificacion_node
from workflows.nodos.consultar_ia_liviana import consultar_ia_liviana_node
from workflows.nodos.limpiar_string import limpiar_string_node
from workflows.nodos.consultar_ia import consultar_ia_node
from workflows.nodos.guardar_historial import guardar_historial_node

from typing import TypedDict

from workflows.nodos.obtener_sesion import obtener_sesion
from workflows.nodos.obtener_tools_disponibles import obtener_tools_disponibles

class WorkflowState(TypedDict, total=False):
    text: str
    cleaned_text: str
    respuesta_ia: str
    session_id: str
    id_usuario: int
    id_contexto: int
    session_data: Any
    file_data: Any
    tools: Any  # Combinar listas
    clasificacion: Any  # Resultado de clasificación
    
class MainWorkflow:

    def __init__(self):

        workflow = StateGraph(WorkflowState)

        workflow.add_node("limpiar_string",limpiar_string_node)
        workflow.add_node("consultar_ia",consultar_ia_node)
        workflow.add_node("guardar_historial",guardar_historial_node)
        workflow.add_node("obtener_sesion", obtener_sesion)
        workflow.add_node("obtener_tools_disponibles", obtener_tools_disponibles)
        workflow.add_node("clasificacion", clasificacion_node)  # Nodo de clasificación, se llenará con el resultado
        workflow.add_node("consultar_ia_liviana", consultar_ia_liviana_node)  # Nodo para IA Liviana

        workflow.add_edge(START,"limpiar_string")
        workflow.add_edge("limpiar_string","clasificacion")

        def route_clasificacion(state: WorkflowState) -> str:
            resultado = state.get("clasificacion", "")
            return "consultar_ia_liviana" if resultado == "casual" else "obtener_sesion"

        workflow.add_conditional_edges("clasificacion", route_clasificacion, {
            "consultar_ia_liviana": "consultar_ia_liviana",
            "obtener_sesion": "obtener_sesion",
        })

        workflow.add_edge("consultar_ia_liviana", "guardar_historial")

        workflow.add_edge("obtener_sesion","obtener_tools_disponibles")
        workflow.add_edge("obtener_tools_disponibles","consultar_ia")
        workflow.add_edge("consultar_ia","guardar_historial")
        
        workflow.add_edge("guardar_historial",END)

        self.app = workflow.compile()

    async def stream(
        self,
        state: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:

        tokens_yielded = False
        final_output = {}

        async for event in self.app.astream_events(state, version="v2"):
            if event["event"] == "on_chain_end" and event.get("name") == "LangGraph":
                final_output = event["data"].get("output", {})

            if event["event"] != "on_chat_model_stream":
                continue

            chunk = event["data"]["chunk"]
            if not chunk.content:
                continue

            tokens_yielded = True
            yield chunk.content

        # Respuesta cacheada: no hubo eventos de streaming del modelo
        if not tokens_yielded and final_output.get("respuesta_ia"):
            yield final_output["respuesta_ia"]