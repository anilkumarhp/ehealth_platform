from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App settings
    PROJECT_NAME: str = "User Management Service"
    API_V1_STR: str = "/api/v1"

    # Database settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_S3_BUCKET_NAME: str
    AWS_REGION: str
    
    # Constructed database URL
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def TEST_DATABASE_URL(self) -> str:
        return f"{self.DATABASE_URL}_test"
    
    # JWT Settings
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"
    
    # Refresh token settings
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    @property
    def REFRESH_TOKEN_EXPIRE_TIMEDELTA(self):
        from datetime import timedelta
        return timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)

    # STRIPE Settings
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str

    # Remember me token expire
    EXPIRE: int = 21600 # 15 days

    # MFA Settings
    MFA_ISSUER_NAME: str = "eHealthPlatform"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

settings = Settings()