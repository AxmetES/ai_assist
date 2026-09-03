from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from anthropic_client import AnthropicError, ask_claude, check_api_key
from database import get_db, init_db
from schemas import ApiKeyHealth, AskRequest, AskResponse, HistoryItem


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="AI Assistant Dashboard", lifespan=lifespan)


@app.post("/ask", response_model=AskResponse)
async def ask(payload: AskRequest, db: AsyncSession = Depends(get_db)):
    try:
        result = await ask_claude(payload.question)
    except AnthropicError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    message = models.Message(
        question=payload.question,
        answer=result.answer,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)

    return message


@app.get("/history", response_model=list[HistoryItem])
async def history(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Message).order_by(models.Message.created_at.desc()).limit(5)
    )
    return result.scalars().all()


@app.get("/health/api-key", response_model=ApiKeyHealth)
async def health_api_key():
    return await check_api_key()


app.mount("/", StaticFiles(directory="static", html=True), name="static")
