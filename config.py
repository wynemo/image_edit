from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # OpenAI 配置
    OPENAI_API_KEY: str = ""
    OPENAI_API_URL: str = "https://openrouter.ai/api/v1"
    OPENAI_MODEL: str = "google/gemini-2.5-flash-image-preview:free"


settings = Settings()
