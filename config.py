import os
import logging
from datetime import datetime, date
from flask.json.provider import DefaultJSONProvider


class Config(object):
    # DEBUG = True
    # SERVER_NAME = "10.21.0.13:8889"
    SECRET_KEY = "DxY3z7jndzYaiY1ndZh+OJOv800zHpRZiWwwNBjC5PAQ1IEMMcWqiyQ8xn2lviMg"
    # SECRET_KEY = "secret"
    PERMANENT_SESSION_LIFETIME = 12
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_DATABASE_URI = "oracle://quotation_user:123456@10.0.27.42:1521/orcl" 用于连接默认pdb
    # SQLALCHEMY_DATABASE_URI = "oracle://quotation_user:12345678@10.0.27.42:1521/?service_name=orclpdb"  # 用于连接指定pdb
    SQLALCHEMY_DATABASE_URI = "oracle://quotation_user:12345678@10.0.27.71:1521/?service_name=orclpdb"  # 用于连接指定pdb
    # Redis相关配置
    REDIS_HOST = "10.0.27.73"  # redis的ip
    REDIS_PORT = 16379  # redis的端口
    REDIS_PWD = "123456"
    REDIS_DB = 1  # 测试环境1
    REDIS_URL = "redis://default:123456@10.0.27.73:16379/1"
    # SESSION_TYPE = "redis"  # session存储的数据库类型
    # SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 设置session存储使用的redis连接对象
    SESSION_USE_SIGNER = True  # 对cookie中保存的sessionid进行加密(需要使用app的秘钥)
    # 异步任务Celery
    BROKER_URL = f'redis://:{REDIS_PWD}@{REDIS_HOST}:{REDIS_PORT}/0'
    RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/1'

    # Pristima相关设置
    PRISTIMA_URL_SITE = 'PTSPSaAPI'
    PRISTIMA_URL = 'http://PTSPSaAPI/hubeipro_api/servlet/PtsAPIServlet'
    PRISTIMA_USERID = 'liumingli'
    PRISTIMA_PASSWORD = 'qWe123456'
    PRISTIMA_SITE_ID = '21'
    PRISTIMA_DEVICENAME = 'dcadmin'
    PRISTIMA_DEVICELOCATION = 'dcadmin'

    SMB_HOST = '10.0.26.13'
    SMB_USERNAME = 'chengchao@topgenexs.com'
    SMB_PASSWORD = 'cc@240203'
    SMB_DIR = 'CorpShare'
    SMB_BASE_PATH = r'\\10.0.26.13\corpshare'
    # SMB_OUTPUT_PATH = '/SEND/SEND_OUTPUT'
    # SMB_DEFINE_CONF_PATH = '/SEND/SEND_DEFINE_CONF'

    ORDER_DICT = {
        0: 'CSV',
        1: 'Perm',
        2: 'Exp',
        3: 'Req', }
    DIR_PATH = 'info/files'
    RESULT_PATH = 'info/files/send_result'
    TERMINOLOGY_PATH = 'info/files/ct'
    SEND_BA_TERMINOLOGY_PATH = r'\\10.0.26.13\deptshare\信息管理部\31.SEND\SEND\CT'
    PARAMETERS_CSV_FILE_PATH = r'\\Ptspseserver\3.1 - Copy'
    SAVANTE_XPT_DIR_PATH = r'\\PTSPSESERVER\temp'
    STATA_XPT_DIR_PATH = r'\\10.0.26.13\deptshare\信息管理部\31.SEND\SEND\SEND_Project\DATA'
    SEND_OUTPUT_DIR = r'SEND\SEND_OUTPUT'
    SEND_DEFINE_DIR = r'SEND\SEND_DEFINE_CONF'

    LOGS_DIR = r'D:\SendProject\server_logs'
    FILE_LOGS_DIR = os.path.join(LOGS_DIR, 'file_handler')
    TIME_LOGS_DIR = os.path.join(LOGS_DIR, 'time_handler')

    CHROMA_HOST = "10.0.27.59"
    CHROMA_PORT = 8000
    PERSIST_DIR = '/data/coding/storage'
    COLLECTION_NAME = "chinese_sops"
    TOP_K = 10
    RERANK_TOP_K = 3


class CeleryConfig(object):
    # Redis相关配置
    REDIS_HOST = "10.0.27.73"  # redis的ip
    REDIS_PORT = 16379  # redis的端口
    REDIS_PWD = "123456"
    SESSION_USE_SIGNER = True  # 对cookie中保存的sessionid进行加密(需要使用app的秘钥)
    # 异步任务Celery
    BROKER_URL = f'redis://:{REDIS_PWD}@{REDIS_HOST}:{REDIS_PORT}/0'
    RESULT_BACKEND = f'redis://:{REDIS_PWD}@{REDIS_HOST}:{REDIS_PORT}/1'
    TASK_MODULE = ['info.modules.send_project']


class CustomJSONProvider(DefaultJSONProvider):
    # jsonify返回datetime格式时默认为GMT时区，故自定义JSON格式化datetime方式
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return DefaultJSONProvider.default(self, obj)


class DevelopConfig(Config):
    DEBUG = True
    LOGLEVEL = logging.WARNING


class ProductConfig(Config):
    DEBUG = True
    LOGLEVEL = logging.ERROR


config_dict = {
    "dev": DevelopConfig,
    "pro": ProductConfig
}
