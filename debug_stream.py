import asyncio
import os
from dotenv import load_dotenv
from langgraph_sdk.client import get_client

load_dotenv()

AGENT_ID = "ff438ec0-4d6c-43e6-a01e-3cceb304e14d"
AGENT_URL = "https://prod-deepagents-agent-build-d4c1479ed8ce53fbb8c3eefc91f0aa7d.us.langgraph.app"

client = get_client(
    url=AGENT_URL,
    api_key=os.getenv("LANGSMITH_API_KEY"),
    headers={"X-Auth-Scheme": "langsmith-api-key"},
)

async def debug_stream():
    thread = await client.threads.create()
    thread_id = thread["thread_id"]
    print(f"Thread: {thread_id}\n")

    async for chunk in client.runs.stream(
        thread_id,
        AGENT_ID,
        input={
            "messages": [
                {"type": "human", "content": "Hola, ¿cómo estás?"},
            ]
        },
        stream_mode="messages",
    ):
        print(f"EVENT: {chunk.event!r}")
        print(f"DATA:  {chunk.data!r}")
        print("-" * 60)

if __name__ == "__main__":
    asyncio.run(debug_stream())
