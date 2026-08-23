from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    llm_api_key: str = ''
    llm_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"  # Default to OpenAI, but .env overrides this!
    llm_model_name: str = "gemini-2.5-flash"
    embedding_model_name: str = "all-MiniLM-L6-v2"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # 2. SettingsConfigDict is correctly applied
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# 3. Instantiate the config
config = Settings()