import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, AsyncGenerator

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY and not DEMO_MODE else None

app = FastAPI(title="Portfolio AI Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Role = Literal["system", "user", "assistant"]

class Message(BaseModel):
    role: Role
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = Field(default="gpt-4o-mini")
    temperature: Optional[float] = Field(default=0.4, ge=0, le=2)
    stream: Optional[bool] = Field(default=True)

@app.get("/")
def root():
    return {"message": "AI agent backend is running!", "demo": DEMO_MODE}

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.post("/chat-json")
def chat_json(req: ChatRequest):
    if DEMO_MODE:
        # Echo the last user message for now
        user_msg = next((m.content for m in req.messages if m.role == "user"), "Hello")
        return JSONResponse({"content": f"(demo) You said: {user_msg}"})

    if not client:
        raise HTTPException(status_code=500, detail="No OpenAI client configured")

    resp = client.chat.completions.create(
        model=req.model,
        temperature=req.temperature,
        messages=[m.model_dump() for m in req.messages],
    )
    return JSONResponse({"content": resp.choices[0].message.content or ""})

@app.post("/chat")
def chat(req: ChatRequest):
    if DEMO_MODE:
        async def demo_stream():
            # Build a fake streaming reply based on the last user message
            user_msg = next((m.content for m in req.messages if m.role == "user"), "Hello")
            text = "(demo) Streaming reply: " + user_msg
            # Stream one word at a time
            for word in text.split():
                yield f"data: {word}\n\n".encode()
                # small pause makes it feel real (optional)
                import asyncio
                await asyncio.sleep(0.3)
            yield b"data: [DONE]\n\n"

        return StreamingResponse(demo_stream(), media_type="text/event-stream")

    if not client:
        raise HTTPException(status_code=500, detail="No OpenAI client configured")

    async def event_gen():
        stream = client.chat.completions.create(
            model=req.model,
            temperature=req.temperature,
            messages=[m.model_dump() for m in req.messages],
            stream=True,
        )
        for chunk in stream:
            delta = getattr(chunk.choices[0].delta, "content", None)
            if delta:
                yield f"data: {delta}\n\n".encode()
        yield b"data: [DONE]\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream")

