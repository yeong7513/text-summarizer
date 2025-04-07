from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging
import traceback

# Настройка логирования
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

def get_page(url: str) -> BeautifulSoup:
    """Получение и парсинг страницы"""
    driver = None
    try:
        logger.info(f"Инициализация драйвера для URL: {url}")
        
        # Настройка опций Chrome
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Инициализация сервиса и драйвера
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        logger.debug("Драйвер успешно инициализирован")

        # Загрузка страницы
        logger.info(f"Загрузка страницы: {url}")
        driver.get(url)
        time.sleep(3)
        
        # Проверка на блокировку
        if "Доступ ограничен" in driver.title:
            error_msg = "Обнаружена блокировка доступа"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
            
        logger.info("Страница успешно загружена")
        return BeautifulSoup(driver.page_source, 'html.parser')

    except WebDriverException as e:
        error_msg = f"Ошибка WebDriver: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {traceback.format_exc()}")
        raise RuntimeError(f"Ошибка получения страницы: {str(e)}") from e
    finally:
        if driver:
            logger.info("Завершение работы драйвера")
            driver.quit()

def dzen_parser(url: str) -> str:
    """Парсер статей для Dzen"""
    content = []
    try:
        logger.info(f"Начало обработки статьи: {url}")
        
        # Получение и парсинг страницы
        soup = get_page(url)
        if not soup:
            error_msg = "Не удалось получить содержимое страницы"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Извлечение заголовка
        title_element = soup.find('h1', {'itemprop': 'headline'}) or \
                        soup.find('h1', class_='content--article-render__title-1g')

        if not title_element:
            error_msg = "Заголовок статьи не найден"
            logger.error(error_msg)
            with open('debug.html', 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            logger.info("Сохранен debug.html для анализа")
            raise ValueError(error_msg)

        title = title_element.get_text(strip=True)
        content.append(title)
        logger.info(f"Заголовок найден: {title[:50]}...")

        # Поиск тела статьи
        article_body = soup.find('div', {'itemprop': 'articleBody'}) or \
                    soup.find('div', class_='content--article-render__container-1k')

        if not article_body:
            error_msg = "Тело статьи не найдено"
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info("Обработка содержимого статьи")
        elements_processed = 0
        for element in article_body.find_all(['h2', 'p']):
            try:
                if element.name == 'h2':
                    spans = element.find_all('span')
                    current_text = ' '.join(span.get_text(strip=True) for span in spans) if spans else element.get_text(strip=True)
                    content.append(current_text)
                    logger.debug(f"Обработан подзаголовок: {current_text[:50]}...")
                elif element.name == 'p':
                    current_text = element.get_text(' ', strip=True)
                    content.append(current_text)
                    logger.debug(f"Обработан абзац: {current_text[:50]}...")
                elements_processed += 1
            except Exception as e:
                logger.warning(f"Ошибка обработки элемента: {str(e)}")

        logger.info(f"Обработано элементов: {elements_processed}")
        full_text = ' '.join(content)
        logger.info(f"Успешно сгенерирован текст длиной {len(full_text)} символов")
        return full_text

    except Exception as e:
        logger.error(f"Ошибка парсера: {traceback.format_exc()}")
        raise RuntimeError(f"Ошибка парсинга статьи: {str(e)}") from e
    