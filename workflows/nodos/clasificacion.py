from typing import Dict, Any
from modelos.clasificador import router

def clasificacion_node(state: Dict[str, Any]) -> Dict[str, Any]:
    texto_limpio = state.get("cleaned_text", "")
    resultado = router.predict(texto_limpio)
    print(f"Texto a clasificar: {texto_limpio}")
    print(f"Resultado de clasificación: {resultado}")
    return {
        "clasificacion": resultado.get("route")
    }
