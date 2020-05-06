import logging #logging模块使用方式https://www.cnblogs.com/liujiacai/p/7804848.html
import os
import sys

from src.config.definitions import NORMAL_LOGGER, SUGGESTION_LOGGER

formatter = logging.Formatter("%(asctime)s [%(levelname)s]  %(message)s")
#设置log日志文件记录时的格式

def get_logger(name, log_file, level=logging.DEBUG, format=True):
    """To setup as many loggers as you want"""

    # output to both console and file
    console_handler = logging.StreamHandler(sys.stdout)
    #采用StreamHandler，意图将输出日志信息发送到console控制台输出
    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    #采用FileHandler，意图将输出日志信息发送到本地文件上
    if format:#如果开启格式模式
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        #为每个handler配置格式format

    logger = logging.getLogger(name)
    #创建日志记录logger对象，name对应一个参数，一般是程序名称，本程序中仅一个标记参数“normal”或“suggestion”
    #分别对应NORMAL_LOGGER和SUGGESTION_LOGGER对应的地址
    logger.setLevel(level)
    #为logger对象设置日志记录等级level参数，DEBUG对应调试等级输出
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    #为logger对象设置handler对象，可以理解为logger对象处理输入，handler对象处理输出

    return logger


# mkdir if not exist
if not os.path.exists(os.path.dirname(NORMAL_LOGGER)):
    os.mkdir(os.path.dirname(NORMAL_LOGGER))
if not os.path.exists(os.path.dirname(SUGGESTION_LOGGER)):
    os.mkdir(os.path.dirname(SUGGESTION_LOGGER))

log = get_logger('normal', os.path.abspath(NORMAL_LOGGER))
#log向NORMAL_LOGGER输出日志
suggestion_log = get_logger('suggestion', os.path.abspath(SUGGESTION_LOGGER), format=False)
#suggestion_log向SUGGESTION_LOGGER输出日志