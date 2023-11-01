from pydantic_settings import BaseSettings, SettingsConfigDict

default_redis_url = 'redis://redis:6379/0'

class Settings(BaseSettings):
    app_name: str = "Bookodo"
    in_cloud: bool = False
    s3_bucket_name_media: str = ''
    openai_api_key: str = None
    secret_key: str
    db_connection: str
    celery_broker_url: str = default_redis_url
    celery_result_backend: str = default_redis_url
    redis_url: str = default_redis_url
    model_config = SettingsConfigDict(env_file=".env")
    postgres_user: str
    postgres_db: str

settings = Settings()
