from src.config.definitions import DOLLAR_TO_CNY
from src.config.urls import *
from src.util import requester
from src.util.logger import log
from src.util.proxy_util import proxyGet
from itertools import cycle

def crawl_item_history_price(index, item, total_price_number,proxy):
    history_prices = []

    item_id = item.id
    steam_price_url = steam_price_history_url(item_id)
    #从item.id获取对应的steam价格接口api
    log.info('GET {} 的steam价格信息 处理序列 第{}个/共{}个 : steam对应价格api接口 {}'.format(item.name, index, total_price_number,  steam_price_url))
    steam_history_prices = requester.get_json_dict(steam_price_url,proxy)
    """
    json格式如下:
    {
      "code": "OK", 
      "data": {
        "currency": "\u4eba\u6c11\u5e01", 
        "currency_symbol": "\u00a5", 
        "days": 7, 
        "price_history": [
                            [
                                1587834000000, 
                                180.94
                            ], 
                         ], 
        "price_type": "Steam\u4ef7\u683c", 
        "steam_price_currency": "\u5143"
      }, 
      "msg": null
    }
    """
    if steam_history_prices is not None:
        days = steam_history_prices['data']['days']
        raw_price_history = steam_history_prices['data']['price_history']
        for pair in raw_price_history:
            if len(pair) == 2:
                history_prices.append(float(pair[1]) * DOLLAR_TO_CNY)
                #获取历史记录列表

        # set history price if exist
        if len(history_prices) != 0:
            item.set_history_prices(history_prices, days)
            #为item设置历史价格,在其item类定义中,还会计算其他如 平均价格等参数

        log.info('{} 在最近 {} 天里有共 {} 件交易记录 \n'.format(item.name,days,len(history_prices)))


def crawl_history_price(csgo_items):
    total_price_number = len(csgo_items)
    log.info('从buff爬取共 {} 物品item满足爬取条件.'.format(total_price_number))

    proxies = proxyGet(30)
    proxies_cycle = cycle(proxies)

    for index, item in enumerate(csgo_items, start=1):
        #枚举类型,从1开始,index记录的就是序号
        #针对csgo_items中的所有物品进行爬取,并赋予序号
        proxy = next(proxies_cycle)
        crawl_item_history_price(index, item, total_price_number,proxy)
