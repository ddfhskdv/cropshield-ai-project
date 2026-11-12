from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = 'CropShield AI'
    API_V1_STR: str = '/api/v1'
    SECRET_KEY: str = 'dev-secret-key'
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    MONGODB_URI: str = 'mongodb://localhost:27017'
    MONGO_DB_NAME: str = 'cropshield'
    WEATHER_API_BASE: str = 'https://api.open-meteo.com/v1/forecast'
    GROQ_API_KEY: str = ''
    MODEL_ID: str = 'kimcomehome/plantvillage-vit-leaf-disease'
    FALLBACK_MODEL_IDS: list[str] = [
        'google/vit-base-patch16-224',
        'microsoft/beit-base-patch16-224',
    ]
    SUPPORTED_CROPS: list[str] = [
        'Tomato',
        'Potato',
        'Rice',
        'Wheat',
        'Maize',
        'Cotton',
        'Sugarcane',
        'Grape',
        'Apple',
        'Pepper',
    ]
    MODEL_CACHE_DIR: str = './model_cache'
    CORS_ORIGINS: str = 'http://localhost:5173,http://localhost:5174'

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()
