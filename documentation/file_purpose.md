# File purpose

## middleman.py
This is where all API logic lives. It send what models are avialible as well as chat compeltions.

- @app.get("/v1/models") async def list_models(): This allows openwebui to see what models are availibe in Ollama.

- @app.post("/v1/chat/completions") async def chat_completions(request: Request): THis is where chats are streamed.

## safety.py
This is where all current safety features live right now. Currentley just supports system prompt injedction with safety rules.

- def inject_system_prompt(payload: dict) -> dict: This injects the system prompt in.

- SAFETY_SYSTEM_PROMPT is the Safety Sytem Prompt. This should handle most issues.