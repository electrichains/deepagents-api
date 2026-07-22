import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel

from deepagents import create_deep_agent

agent = None


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


class ChatResponse(BaseModel):
    response: str


def _build_model():
    model = os.environ.get("DEEPAGENTS_MODEL", "openai:openai/gpt-4o")
    openai_base_url = os.environ.get("OPENAI_BASE_URL")
    if openai_base_url:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model.removeprefix("openai:"),
            base_url=openai_base_url,
        )
    return model


@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent
    agent = create_deep_agent(model=_build_model())
    yield


app = FastAPI(
    title="Deep Agents API",
    version="0.1.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="server/static"), name="static")


@app.get("/")
async def root():
    return FileResponse("server/static/index.html")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> dict[str, Any]:
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    config = {}
    if request.thread_id:
        config["configurable"] = {"thread_id": request.thread_id}

    result = agent.invoke(
        {"messages": [HumanMessage(content=request.message)]},
        config=config,
    )

    ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
    if not ai_messages:
        raise HTTPException(status_code=500, detail="No response from agent")

    return {"response": ai_messages[-1].content}
