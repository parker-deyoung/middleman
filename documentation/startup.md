# Startup Instuctions

# Step 1
- Start ollama - ollama

- Start Open webui - open-webui serve

- Start middleman startup server - uvicorn src.middleman:app --reload


# Step 2 
Go to Openwebui. **(Admin only)** 

Click on user profile in bottom left corner -> Click on admin panel -> click on Settings -> Click on connections -> Disable Ollama API -> Switch link for OpenAI API to http://localhost:8000/v1 to point it towards the API.