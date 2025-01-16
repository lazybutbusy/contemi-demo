from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import inspect
import json
from pydantic import BaseModel
from typing import Optional

import os
import logging
from lightrag import LightRAG, QueryParam
from lightrag.llm import gpt_4o_mini_complete, gpt_4o_complete
from lightrag.llm import ollama_model_complete, ollama_embedding
from lightrag.utils import EmbeddingFunc
import lightrag

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

print(lightrag.prompt.PROMPTS['rag_response'])

rag = LightRAG(
    working_dir="./contemi_openai",
    llm_model_max_async=8,
    llm_model_func=gpt_4o_mini_complete,  # Use gpt_4o_mini_complete LLM model
    # llm_model_func=gpt_4o_complete  # Optionally, use a stronger model
)

rag_opensrc = LightRAG(
    working_dir="./contemi_opensrc",
    llm_model_max_async=2,
    llm_model_func=ollama_model_complete,  # Use Ollama model for text generation
    llm_model_name='phi4', # Your model name
    llm_model_kwargs={"options": {"num_ctx": 30720}},
    # Use Ollama embedding function
    embedding_func=EmbeddingFunc(
        embedding_dim=768,
        max_token_size=8192,
        func=lambda texts: ollama_embedding(
            texts,
            embed_model="nomic-embed-text"
        )
    ),
)

app = FastAPI(title="LightRAG", description="LightRAG API open-webui")

# Data models
MODEL_NAME_1 = "Contemi_ChatBot (OpenAI):latest"
MODEL_NAME_2 = "Contemi_ChatBot (Phi4):latest"

class Message(BaseModel):
    role: Optional[str] = None
    content: str


class OpenWebUIRequest(BaseModel):
    stream: Optional[bool] = None
    model: Optional[str] = None
    messages: list[Message]


# API routes


@app.get("/")
async def index():
    return "Set Ollama link to http://ip:port/ollama in Open-WebUI Settings"


@app.get("/ollama/api/version")
async def ollama_version():
    return {"version": "0.4.7"}


@app.get("/ollama/api/tags")
async def ollama_tags():
    return {
        "models": [
            {
                "name": MODEL_NAME_1,
                "model": MODEL_NAME_1,
                "modified_at": "2024-11-12T20:22:37.561463923+08:00",
                "size": 0,
                "digest": "845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e",
                "details": {
                    "parent_model": "",
                    "format": "gguf",
                    "family": "gpt_4o_mini",
                    "families": [],
                    "parameter_size": "0B",
                    "quantization_level": "Q4_0",
                },
            },
            {
                "name": MODEL_NAME_2,
                "model": MODEL_NAME_2,
                "modified_at": "2024-11-12T20:22:37.561463923+08:00",
                "size": 14683087332,
                "digest": "f9e47b1699aa98213272843c90c04b872c04d7863f3dead8ac4821fc0acf4fd8",
                "details": {
                    "parent_model": "",
                    "format": "gguf",
                    "family": "phi3.5",
                    "families": ["phi3.5"],
                    "parameter_size": "3B",
                    "quantization_level": "Q8_0",
                },
            },
        ]
    }

@app.post("/ollama/api/chat")
async def ollama_chat(request: OpenWebUIRequest):
    # Gọi hàm aquery từ LightRAG
    if request.model == MODEL_NAME_1:
        model = rag
    elif request.model == MODEL_NAME_2:
        model = rag_opensrc
    else:
        model = None

    resp = await model.aquery(
        request.messages[-1].content, param=QueryParam(mode="hybrid", stream=True, top_k=100)
    )
    async def ollama_resp(chunks):
        if isinstance(chunks, str):
            async def string_to_async_iter(string):
                yield string

            chunks = string_to_async_iter(chunks)

        async for chunk in chunks:
            yield (
                json.dumps(
                    {
                        "model": request.model,
                        "created_at": datetime.now(timezone.utc).strftime(
                            "%Y-%m-%dT%H:%M:%S.%fZ"
                        ),
                        "message": {
                            "role": "assistant",
                            "content": chunk,
                        },
                        "done": False,
                    },
                    ensure_ascii=False,
                ).encode("utf-8")
                + b"\n"
            )  # the b"\n" is important

    return StreamingResponse(ollama_resp(resp), media_type="application/json")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8022)