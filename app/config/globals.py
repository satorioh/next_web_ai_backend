import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # -------------路由配置----------------- #
    API_PREFIX: str = "/api/v1/webml"
    # -------------AWS配置----------------- #
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY")
    S3_SIG_BUCKET_NAME: str = os.getenv("S3_SIG_BUCKET_NAME")
    S3_WEBML_FOLDER: str = os.getenv("S3_WEBML_FOLDER")
    S3_WEBML_MODEL_URL_PREFIX: str = f"https://{S3_SIG_BUCKET_NAME}.s3.amazonaws.com/{S3_WEBML_FOLDER}/model"
    # -------------日志----------------- #
    LOG_SERVICE_TOKEN: str = os.getenv('LOG_SERVICE_TOKEN')


settings = Settings()
