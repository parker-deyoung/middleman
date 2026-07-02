from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from starlette.background import BackgroundTask
import httpx
import asyncio

from .safety import inject_system_prompt

#Switch to your own OLLAMA_BASE if you are not running ollama locally.
OLLAMA_BASE = "http://localhost:11434/v1"
#Max concurrent requests to ollama.  Ollama is single threaded, so this is a way to limit the number of concurrent requests to it.
MAX_CONCURRENT = 4  
#Timeout for acquiring a semaphore to limit concurrent requests.  If this is exceeded, the request will fail with a 503.
ACQUIRE_TIMEOUT = 30 

sem = asyncio.Semaphore(MAX_CONCURRENT)
app = FastAPI()
client = httpx.AsyncClient(base_url=OLLAMA_BASE, timeout=None)

#Openwebui needs to send mdoels back and forth
@app.get("/v1/models")
async def list_models():
    r = await client.get("/models")
    return JSONResponse(content=r.json(), status_code=r.status_code)

#Chat completions for chat pass through to ollama.  This is where RAG / safety filtering will hook in later.
# Path must be in openai format to work with openwebui.
@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    payload = await request.json()

    #   RAGwill hook in here later.
    #   For now, pass the payload through unchanged.
    
    #Safety and prompt injection filtering.  This will inject a system prompt into the request to ensure that the model is always aware of the safety rules.
    payload = inject_system_prompt(payload)

    try:
        await asyncio.wait_for(sem.acquire(), timeout=ACQUIRE_TIMEOUT)
    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=429,
            content={"error": {"message": "Server at capacity, please retry.",
                               "type": "rate_limit_exceeded"}},
        )
    
    try:
        req = client.build_request("POST", "/chat/completions", json=payload)
        upstream = await client.send(req, stream=True)
    except Exception:
        sem.release()
        raise

    async def stream_and_release():
        try:
            async for chunk in upstream.aiter_raw():
                yield chunk
        finally:
            await upstream.aclose()
            sem.release() 

    return StreamingResponse(
        stream_and_release(),
        status_code=upstream.status_code,
        headers={"Content-Type": upstream.headers.get("content-type", "application/json")},
    )