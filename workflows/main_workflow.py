from typing import Dict, Any, AsyncGenerator
from langgraph.graph import StateGraph, START, END
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
    
class MainWorkflow:

    def __init__(self):

        workflow = StateGraph(WorkflowState)

        workflow.add_node("limpiar_string",limpiar_string_node)
        workflow.add_node("consultar_ia",consultar_ia_node)
        workflow.add_node("guardar_historial",guardar_historial_node)
        workflow.add_node("obtener_sesion", obtener_sesion)
        workflow.add_node("obtener_tools_disponibles", obtener_tools_disponibles)


        workflow.add_edge(START,"limpiar_string")
        workflow.add_edge("limpiar_string","obtener_sesion")
        workflow.add_edge("obtener_sesion","obtener_tools_disponibles")
        workflow.add_edge("obtener_tools_disponibles","consultar_ia")
        workflow.add_edge("consultar_ia","guardar_historial")
        workflow.add_edge("guardar_historial",END)

        self.app = workflow.compile()

    async def stream(
        self,
        state: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:

        async for event in self.app.astream_events(state,version="v2"):
            if event["event"] != "on_chat_model_stream":
                continue

            chunk = event["data"]["chunk"]
            if not chunk.content:
                continue

            yield chunk.content