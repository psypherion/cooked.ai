from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    CHROMA_DB_PATH: str = "./roast_db"
    
    class Config:
        env_file = ".env"

settings = Settings()
