
# 📝 URL-based Article Summarizer API

A FastAPI-based web service that extracts and summarizes text content from a given URL. Supports dynamic content extraction (e.g., [dzen.ru](https://dzen.ru)) using Selenium, and summarization using the **Deepseek Chat API**.

---

## 🚀 Features

- 🌐 **URL-based Text Extraction**  
  Automatically extracts readable article content from a given webpage.

- 🤖 **AI-powered Summarization**  
  Uses Deepseek’s language model API to summarize long articles into concise bullet points.

- 📰 **Smart Parsing for Dzen Articles**  
  Custom parser to handle JavaScript-heavy pages like Dzen (Яндекс Дзен) using Selenium + BeautifulSoup.

- ⚙️ **Configurable Summary Length**  
  Control the desired summary length via `max_length` parameter.

---

## 🛠️ Tech Stack

- **FastAPI** - REST API framework  
- **Selenium + BeautifulSoup** - Dynamic web page scraping  
- **trafilatura** - General-purpose web text extraction  
- **Deepseek Chat API** - Summarization model  
- **Pydantic** - Request validation  
- **tiktoken** - Token counting for truncation  
- **httpx** - Robust HTTP client

---

## 📦 Installation

### 1. Clone the repo

```bash
git clone https://github.com/yeong7513/text-summarizer.git
cd text-summarizer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file in the root directory:

```
DEEPSEEK_API_KEY=your_deepseek_api_key
```

---

## ▶️ Running the Service

```bash
uvicorn main:app --reload
```

Access the interactive API docs at:  
📍 `http://localhost:8000/docs`

---

## 📤 API Usage

### **POST /summarize**

Summarize content from a URL.

#### Request body:

```json
{
  "url": "https://dzen.ru/a/your-article-id",
  "max_length": 300
}
```

#### Response:

```json
{
  "summary": "- Main point 1\n- Main point 2\n..."
}
```

---

## 🧠 How It Works

1. **Text Extraction**  
   - If URL domain is `dzen.ru`: Uses `Selenium` to load the page and parse the content with BeautifulSoup.
   - Else: Falls back to `trafilatura` for general-purpose scraping.

2. **Truncation**  
   The extracted content is truncated based on token count (`MAX_INPUT_TOKENS`) using `tiktoken`.

3. **Summarization**  
   The trimmed text is passed to Deepseek’s API which returns a bullet-point summary.

---

## 🧪 Sample CURL

```bash
curl -X POST http://localhost:8000/summarize \
-H "Content-Type: application/json" \
-d '{"url": "https://dzen.ru/a/some-article", "max_length": 300}'
```

---

## 📁 Project Structure

```
.
├── main.py                  # FastAPI app with /summarize endpoint
├── models.py                # Request schema using Pydantic
├── services/
│   ├── text_fetcher.py      # Chooses correct parsing method based on domain
│   ├── dzen_parser.py       # Custom parser for Dzen articles
│   └── deepseek_summarizer.py  # Summarization logic using Deepseek API
├── config.py                # Logging, tokenizer, API key loading
├── .env                     # Contains DEEPSEEK_API_KEY
└── requirements.txt
```

---

## 🛡️ Error Handling

- `400 Bad Request` – Failed to extract text
- `504 Gateway Timeout` – Network error to external URL
- `500 Internal Server Error` – Unexpected server-side issues

---

## 📄 License

MIT License © 2025

