import requests
from requests import Timeout
import urllib
from src.config.definitions import COOKIE, RETRY_TIMES
from src.util import timer
from src.util.logger import log

cookie_str = COOKIE
cookies = {}
for line in cookie_str.split(';'):
    k, v = line.split('=', 1)
    cookies[k] = v

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36'
}


def get_json_dict(url, proxy = None,times=1):
    if times > RETRY_TIMES:
        log.error('Timeout for {} beyond the maximum({}) retry times. SKIP!'.format(url, RETRY_TIMES))
        return None

    timer.sleep_awhile()
    #随机睡眠1~2秒
    try:
        if proxy is not None:
            log.info("使用代理{}".format(proxy))
            return requests.get(url, headers=headers, cookies=cookies, timeout=5,proxies = {'http':proxy}).json()
        else:
            log.info("无代理".format(proxy))
            return requests.get(url, headers=headers, cookies=cookies, timeout=5).json()
        #获取JSON文件
    except Timeout:
        #获取json时出现超时问题
        log.warn("timeout for {}. Try again.".format(url))
        return get_json_dict(url, times + 1)
