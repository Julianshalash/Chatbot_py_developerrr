import openai
from fastapi import FastAPI, WebSocket
import uvicorn
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

app = FastAPI()

# Initialize the chat log with a system message
chat_log = [{"role": "system", "content": "You are a Python developer. Help users with Python-related queries."}]

# Function to generate response from OpenAI with streaming
async def generate_response(prompt, websocket: WebSocket):
    chat_log.append({"role": "user", "content": prompt})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_log,
        stream=True
    )

    full_response = ""
    for chunk in response:
        chunk_content = chunk['choices'][0]['delta'].get('content', '')
        if chunk_content:
            full_response += chunk_content
            await websocket.send_text(chunk_content)

    chat_log.append({"role": "assistant", "content": full_response})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await generate_response(data, websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
