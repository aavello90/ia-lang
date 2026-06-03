import asyncio
from workflows.main_workflow import MainWorkflow

async def test_workflow():
    workflow = MainWorkflow()
    
    state = {
        "text": "Hola, ¿cómo estás?",
        "id_usuario": 13,
        "id_contexto": 4
    }
    
    print(f"Input: {state}")
    print("-" * 40)
    
    try:
        async for token in workflow.stream(state):
            print(token, end="", flush=True)
        print("\n" + "-" * 40)
        print("Completado")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_workflow())
