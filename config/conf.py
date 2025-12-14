from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_file_encoding="utf-8",
        extra="ignore",
    )
    MONGO_URL:str
    POSTGRES_DB_URL:str
    PINECONE_API_KEY:str
    KB_INDEX:str
    PINECONE_CLOUD:str
    PINECONE_REGION:str
    GROQ_API_KEY:str
    LLAMA_MODEL:str
    TEMPERATURE:float
    MAX_TOKENS:int
    HUGGINGFACE_EMBED_MODEL:str
    EMAIL_HOST:str
    EMAIL_PORT:int
    EMAIL_USER:str
    EMAIL_PASSWORD:str
    EMAIL_FROM:str
    EMAIL_TO:str
    EMAIL_PORT_SSL:int
    # TWILIO_ACCOUNT_SID:str
    # TWILIO_AUTH_TOKEN:str
    # TWILIO_PHONE_NUMBER:str
    ENDPOINT_AUTH_KEY:str

settings = Settings()
