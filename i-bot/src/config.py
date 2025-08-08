from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://ibot:ibot@localhost:5432/ibot"
    OPENAI_API_KEY: str = ""
    TURN_THRESHOLD: int = 5
    SERVICENOW_URL: str = ""
    SERVICENOW_API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()

llm = ChatOpenAI()