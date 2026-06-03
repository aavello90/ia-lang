import asyncio
from workflows.nodos.consultar_ia import consultar_ia_node

async def test_nodo_ia():
    """Función para probar el nodo de consultar IA directamente"""
    # Datos de prueba
    test_data = {
        "cleaned_text": "Hola, ¿cómo estás?",
        "session_id": "13_4",
        "id_usuario": 13,
        "id_contexto": 4
    }
    
    print("Ejecutando nodo de consultar IA con datos de prueba:")
    print(f"Datos de entrada: {test_data}")
    print("-" * 40)
    
    try:
        # Ejecutar el nodo y mostrar los chunks
        async for chunk in consultar_ia_node(test_data):
            print(f"Chunk recibido: {chunk}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_nodo_ia())