import boto3
from ..config.globals import settings
from .log import setup_logger

logger = setup_logger(__name__)
s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)


def get_model_last_update_time(model_name, config_file='model.json'):
    """
    获取模型model.json文件的上次更新时间:'Key': 'tfjs/model/rps/model.json'
    :param model_name: 模型名称
    :param config_file: 模型配置文件名称
    :return: "2024-04-28T06:14:21Z"
    """
    key = f'{settings.S3_WEBML_FOLDER}/model/{model_name}/{config_file}'
    logger.info(f"get model last update time -> {key}")
    try:
        objects = s3.list_objects_v2(Bucket=settings.S3_SIG_BUCKET_NAME)
        # Check if there are any objects in the bucket
        if 'Contents' in objects:
            obj = [content for content in objects['Contents'] if content['Key'] == key]
            return obj[0]['LastModified']
        else:
            logger.error(f"get model last update time error -> No objects in the bucket")
            return None
    except Exception as e:
        logger.error(f"get model last update time error -> {e}")
        return None
