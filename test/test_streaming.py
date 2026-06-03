import asyncio
import httpx
import json

async def test_streaming():
    """Función para probar el streaming de la API"""
    url = "http://localhost:8006/invoke"
    data = {
        "text": "Hola, ¿cómo estás?",
        "IdUsuario": 13,
        "IdContexto": 4
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # Hacer la solicitud POST
            async with client.stream("POST", url, json=data) as response:
                print(f"Status code: {response.status_code}")
                print("Recibiendo chunks en tiempo real:")
                print("-" * 40)
                
                buffer = ""
                async for chunk in response.aiter_bytes():
                    # Decodificar el chunk
                    text = chunk.decode('utf-8')
                    buffer += text
                    
                    # Procesar líneas completas
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        if line.startswith("data: "):
                            # Extraer los datos JSON del chunk
                            json_data = line[6:]  # Eliminar "data: " del inicio
                            if json_data.strip():
                                try:
                                    data = json.loads(json_data)
                                    print(f"Chunk recibido: {data}")
                                except json.JSONDecodeError:
                                    print(f"Datos sin procesar: {json_data}")
                        elif line.strip():
                            print(f"Línea sin procesar: {line}")
                print("-" * 40)
                print("Streaming completado")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_streaming())