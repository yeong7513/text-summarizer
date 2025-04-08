from urllib.parse import urlparse
import httpx
import asyncio
import trafilatura
from services.dzen_parser import dzen_parser_async

# Функция для извлечения текста с указанного URL
async def fetch_text_async(url: str) -> str:
    # Разбираем URL для определения домена
    parsed = urlparse(url)
    if "dzen.ru" in parsed.netloc:
        # Для Dzen.ru используем dzen_parser
        return await dzen_parser_async(url)
    else:
        # Для обычных сайтов (без поддержки JS)
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            downloaded = response.text
            return await asyncio.to_thread(trafilatura.extract, downloaded)

