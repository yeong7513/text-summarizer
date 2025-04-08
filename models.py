from pydantic import BaseModel, AnyHttpUrl

# Модель запроса для суммаризации
class SummaryRequest(BaseModel):
    url: AnyHttpUrl   # Автоматическая валидация URL
    max_length: int = 300  # Ограничение длины суммаризации
