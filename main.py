from fastapi import FastAPI, HTTPException, Response, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from typing import Dict, Any, AsyncGenerator, Optional
from workflows.main_workflow import MainWorkflow
import os
import json
import base64

# Cargar variables de entorno
load_dotenv()

# Configurar LangSmith
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "TEST-ML")

# Inicializar FastAPI app
app = FastAPI(title="LangGraph API", description="API con LangGraph, LangChain y LangSmith")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "API con LangGraph, LangChain y LangSmith"}

@app.post("/invoke")
async def invoke_workflow(request: Dict[str, Any]):
    """
    Endpoint para invocar el workflow y devolver la respuesta mediante streaming.
    """
    # Inicializar el workflow para cada solicitud
    async def generate():
        workflow = MainWorkflow()
        workflow_state = {
            "text": request.get("text", ""),
            "id_usuario": request.get("IdUsuario", 1),
            "id_contexto": request.get("IdContexto", 3)
        }

        async for token in workflow.stream(workflow_state):

            yield (
                f"data: {json.dumps({'token': token})}\n\n"
            )

        yield (
            f"data: {json.dumps({'done': True})}\n\n"
        )

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )


@app.post("/invoke-form")
async def invoke_workflow_form(
    text: str = Form(...),
    IdUsuario: int = Form(...),
    IdContexto: int = Form(...),
    file: Optional[UploadFile] = File(default=None),
):
    """
    Endpoint multipart/form-data: acepta texto + archivo opcional.
    El archivo se convierte a base64 y se incluye en el state para
    que consultar_ia_node lo pase al modelo como contenido adjunto.
    """
    # Leer el archivo aquí, dentro del handler, antes de que FastAPI lo cierre
    file_data = None
    if file is not None:
        raw_bytes = await file.read()
        file_data = {
            "filename": file.filename,
            "content_type": file.content_type,
            "base64": base64.b64encode(raw_bytes).decode("utf-8"),
        }

    async def generate():
        workflow = MainWorkflow()

        workflow_state = {
            "text": text,
            "id_usuario": IdUsuario,
            "id_contexto": IdContexto,
            "file_data": file_data,
        }

        async for token in workflow.stream(workflow_state):
            yield f"data: {json.dumps({'token': token})}\n\n"

        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)