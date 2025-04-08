from urllib.parse import urlparse
import trafilatura
from services.dzen_parser import dzen_parser

# Функция для извлечения текста с указанного URL
def fetch_text(url: str) -> str:
    # Проверка принадлежности домена к Dzen
    parsed = urlparse(url)
    if "dzen.ru" in parsed.netloc:
        # Use dzen_parser for Dzen URLs
        return dzen_parser(url)
    else:
        # Для обычных сайтов (без поддержки JS)
        downloaded = trafilatura.fetch_url(url)
        return trafilatura.extract(downloaded)
