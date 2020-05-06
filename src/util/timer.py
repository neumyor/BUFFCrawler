import datetime
import random
import time

from src.util.logger import log
from src.util.proxy_util import proxies

def sleep_awhile():
    if proxies[0] is not None:
        interval = random.uniform(0.1,0.3)
    else:
        interval = random.randint(1,2)
    log.info("sleep {}s at {}".format(interval, datetime.datetime.now()))
    #随机睡眠1~2秒
    time.sleep(interval)
