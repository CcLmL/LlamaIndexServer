from flask import Flask
# from flask_socketio import SocketIO
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import date, datetime
import os
from config import CustomJSONProvider, config_dict
from info.utils.model_extension import init_embedding_model, init_reranker_model
from llama_index.postprocessor.xinference_rerank import XinferenceRerank

# 模型对象全局化
embedding_model = None
reranker_model = None  # type: XinferenceRerank|None


# 配置日志文件
def setup_log(config_class):
    level = config_class.LOGLEVEL
    logging.basicConfig(level=level)
    formatter = logging.Formatter(
        '[%(asctime)s][%(levelname)s][%(pathname)s: %(funcName)s function: %(lineno)s line]: %(message)s')

    # 创建基于文件大小切割的日志处理器
    file_logs_dir = config_class.FILE_LOGS_DIR
    file_log_file_name = date.today().strftime('%Y-%m-%d.log')
    file_logs_file_path = os.path.join(file_logs_dir, file_log_file_name)
    file_log_handler = RotatingFileHandler(filename=file_logs_file_path,
                                           maxBytes=1024 * 2024 * 100,
                                           backupCount=10)
    file_log_handler.setFormatter(formatter)

    # 创建基于时间切割的日志处理器
    time_logs_dir = config_class.TIME_LOGS_DIR
    time_log_file_name = datetime.today().strftime('%Y-%m-%d-%H-%M.log')
    time_logs_file_path = os.path.join(time_logs_dir, time_log_file_name)
    time_log_handler = TimedRotatingFileHandler(filename=time_logs_file_path,  # 日志文件的路径
                                                when='midnight',  # 凌晨零点进行文件分割
                                                backupCount=0,  # 保留旧文件数0
                                                interval=1,  # 分割一次
                                                encoding='utf-8')
    time_log_handler.setFormatter(formatter)

    logging.getLogger().addHandler(file_log_handler)
    logging.getLogger().addHandler(time_log_handler)


def create_app(config_type):
    config_class = config_dict[config_type]
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.json = CustomJSONProvider(app)  # flask2.3中修改传统使用方式

    global embedding_model, reranker_model
    embedding_model = init_embedding_model()
    reranker_model = init_reranker_model()
    from info.modules.llama_index import llama_index_blu
    app.register_blueprint(llama_index_blu)

    # socketio.init_app(app, cors_allowed_origins='*')
    # setup_log(config_class)
    # from info.utils import common
    # 开启csrf保护
    # CSRFProtect(app)
    return app
