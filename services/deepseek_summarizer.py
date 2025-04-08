import logging
from config import MAX_INPUT_TOKENS, MAX_TOKENS, client, tokenizer
from openai import APIError

# Функция для обрезки текста до указанного количества токенов
def truncate_text(text: str, max_tokens: int) -> str:
    tokens = tokenizer.encode(text)[:max_tokens]
    return tokenizer.decode(tokens)

# Функция суммаризации текста с использованием Deepseek API
def summarize_with_deepseek(text: str, max_length: int) -> str:
    try:
        truncated_text = truncate_text(text, MAX_INPUT_TOKENS)
        logging.info(f"Truncated text length: {len(tokenizer.encode(truncated_text))} tokens")
        
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
        logging.error(f"Deepseek API Error: {e}")
        raise Exception(f"API Error: {e.message}")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise Exception("Summary generation failed")
