from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from starlette.background import BackgroundTask
import httpx

#Switch to your own OLLAMA_BASE if you are not running ollama locally.
OLLAMA_BASE = "http://localhost:11434/v1"

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

    #   RAG / safety filtering will hook in here later.
    #   For now, pass the payload through unchanged.

    req = client.build_request("POST", "/chat/completions", json=payload)
    upstream = await client.send(req, stream=True)

    return StreamingResponse(
        upstream.aiter_raw(),
        status_code=upstream.status_code,
        headers={"Content-Type": upstream.headers.get("content-type", "application/json")},
        background=BackgroundTask(upstream.aclose),
    )