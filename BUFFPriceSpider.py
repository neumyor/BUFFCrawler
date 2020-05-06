import datetime

from src.crawl import item_crawler
from src.util import suggestion
from src.util.logger import log

if __name__ == '__main__':
    start = datetime.datetime.now()
    log.info("开始时间: {}".format(start))
    #log 是 程序/log目录下的记录日志对象，对应config中的NORMLAL_LOGGER

    table = item_crawler.crawl()
    if table is not None:
        # suggestion
        suggestion.suggest(table)
        #根据table进行suggest,建议结果放在suggest文件夹中
    else:
        log.error('没有符合条件的物品item,你tmd是不是参数写错了?')

    # endr
    end = datetime.datetime.now()
    log.info("结束时间: {}. 共用时: {}.".format(end, end - start))