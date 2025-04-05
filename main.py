from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, AnyHttpUrl
from requests_html import HTMLSession
import trafilatura, httpx, os, logging, tiktoken
from openai import OpenAI, APIError
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
app = FastAPI()

class SummaryRequest(BaseModel):
    url: AnyHttpUrl  # Автоматическая валидация URL
    max_length: int = 300  # Ограничение длины суммаризации

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Конфигурация Deepseek API
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
MAX_TOKENS = 300  # Максимальное количество токенов для ответа
MAX_INPUT_TOKENS = 6000  # Максимальное количество токенов во входных данных

# Инициализация клиента и токенизатора
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
tokenizer = tiktoken.get_encoding("cl100k_base")


async def fetch_text(url: str) -> str:
    try:
        # Для JS-сайтов
        session = HTMLSession()
        resp = session.get(url)
        resp.html.render(timeout=20)  # Рендеринг JavaScript
        html = resp.html.html
        return trafilatura.extract(html, include_links=False, include_tables=False)
    except Exception as e:
        # Для простых сайтов без JS
        downloaded = trafilatura.fetch_url(url)
        return trafilatura.extract(downloaded)

def truncate_text(text, max_tokens):
    """Обрезка текста до максимального количества токенов"""
    tokens = tokenizer.encode(text)[:max_tokens]
    return tokenizer.decode(tokens)

async def summarize_with_deepseek(text: str, max_length: int) -> str:
    """Суммаризация с обработкой ошибок и ограничениями"""
    try:
        truncated_text = truncate_text(text, MAX_INPUT_TOKENS)
        logger.info(f"Truncated text length: {len(tokenizer.encode(truncated_text))} tokens")
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert summarizer. Create concise bullet-point summary in the language that matches the text provided."
                },
                {
                    "role": "user",
                    "content": f"Summarize this text:\n\n{truncated_text}"
                }
            ],
            temperature=0.3,
            max_tokens=MAX_TOKENS
        )
        
        if not response.choices:
            raise APIError("Empty response from API")
            
        return response.choices[0].message.content
    
    except APIError as e:
        logger.error(f"Deepseek API Error: {e}")
        raise Exception(f"API Error: {e.message}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise Exception("Summary generation failed")
    
@app.post("/summarize")
async def summarize(request: SummaryRequest):
    try:
        text = await fetch_text(str(request.url))
        if not text:
            raise HTTPException(status_code=400, detail="Не удалось извлечь текст")
        
        logger.info(f"text: {text}")
        summary = await summarize_with_deepseek(text, request.max_length)
        logger.info(f"summary: {summary}")
        return {"summary": summary}
    
    except httpx.ConnectError:
        raise HTTPException(status_code=504, detail="Таймаут подключения")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))