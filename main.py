from fastapi import FastAPI, HTTPException
import httpx
import logging

from models import SummaryRequest
from services.text_fetcher import fetch_text
from services.deepseek_summarizer import summarize_with_deepseek

# Инициализация FastAPI приложения
app = FastAPI()

# Эндпоинт для суммаризации текста
@app.post("/summarize")
def summarize(request: SummaryRequest):
    try:
        text = fetch_text(str(request.url))
        if not text:
            raise HTTPException(status_code=400, detail="Failed to extract text")
        
        logging.info(f"Text length: {len(text)}")
        summary = summarize_with_deepseek(text, request.max_length)
        logging.info(f"Summary: {summary}")
        return {"summary": summary}
    
    except httpx.ConnectError:
        raise HTTPException(status_code=504, detail="Connection timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
