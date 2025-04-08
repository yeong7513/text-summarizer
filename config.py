import os
import logging
import tiktoken
from dotenv import load_dotenv
from openai import OpenAI

# Загрузка переменных окружения
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Конфигурация Deepseek API и токенизатор
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
MAX_TOKENS = 300         # Максимальное количество токенов для ответа
MAX_INPUT_TOKENS = 6000  # Максимальное количество токенов во входных данных

# Инициализация клиента Deepseek и токенизатора
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
tokenizer = tiktoken.get_encoding("cl100k_base")
