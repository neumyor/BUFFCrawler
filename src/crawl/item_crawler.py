import re

from itertools import cycle
from src.config.definitions import *
from src.config.urls import *   #和url生成有关的所有函数来源,带_url后缀
from src.crawl import history_price_crawler
from src.data.item import Item
from src.util import requester, persist_util, http_util
from src.util.category_util import final_categories
from src.util.logger import log
from src.util.proxy_util import proxies

def collect_item(item):
    """
    将爬取到的数据转化为Item类的一个对象
    """
    buff_id = item['id']
    name = item['name']
    min_price = item['sell_min_price']
    sell_num = item['sell_num']
    steam_url = item['steam_market_url']
    steam_predict_price = item['goods_info']['steam_price_cny']
    buy_max_price = item['buy_max_price']

    # restrict price of a item
    if float(min_price) < CRAWL_MIN_PRICE_ITEM:
        #理论上,这种情况不会发生
        #因为获取item物品时,就已经经过了最高最低价的分界
        #仅在由于市场瞬间变化导致价格突然跨越界限时可能发生
        log.info("{} price is lower than {}. Drop it!".format(name, CRAWL_MIN_PRICE_ITEM))
        return None
    elif float(min_price) > CRAWL_MAX_PRICE_ITEM:
        log.info("{} price is higher than {}. Drop it!".format(name, CRAWL_MAX_PRICE_ITEM))
        return None
    else:
        log.info("GET ITEM {} , 已经解析到Item类对象.".format(name))
        return Item(buff_id, name, min_price, sell_num, steam_url, steam_predict_price, buy_max_price)
        #item是一个独立的类,其包括各种参数

def csgo_all_categories():
    """
    通过对html文件的解析获取buff下所有大类的名称
    """
    prefix = '<div class="h1z1-selType type_csgo" id="j_h1z1-selType">'
    suffix = '</ul> </div> </div> <div class="criteria">'
    # to match all csgo skin categories
    category_regex = re.compile(r'<li value="(.+?)"', re.DOTALL)
    #用于获取category下名称信息的正则表达式
    # entry page
    root_url = goods_root_url()
    #获取buff主页根url

    log.info("GET 主页在此!: " + root_url)
    root_html = http_util.open_url(root_url)
    #定义在src/util中,简单来说就是一个urllib的url爬取,具体参数自己看

    remove_prefix = root_html.split(prefix, 1)[1]
    #利用spilt函数获取prefix对应字符串后的内容
    core_html = remove_prefix.split(suffix, 1)[0]
    #再获取suffix对应字符串前的内容
    #这种利用split实现切割搜索实在是巧妙

    # all categories
    categories = category_regex.findall(core_html)
    #获取category的所有名称
    log.info("所有buff大类({}): {}".format(len(categories), categories))
    return categories


def enrich_item_with_price_history(csgo_items):
    # crawl price for all items
    history_price_crawler.crawl_history_price(csgo_items)
    return csgo_items


def crawl_website():
    """
    获取buff下所有大类的名称
    根据黑白名单进行修正
    根据价格进行搜索,将结果放在csgo_items中
    再爬取steam价格,修正到item的类参数中
    返回的是由csgo_items生成的pd下的table表格对象
    """
    csgo_items = []

    raw_categories = csgo_all_categories()
    #获取buff下所有枪械物品大类名称
    categories = final_categories(raw_categories)
    #定义在src/category_util下,用于利用白名单和黑名单进行目录的处理
    # crawl by categories and price section
    if len(raw_categories) != len(categories):
        for category in categories:
            csgo_items.extend(crawl_goods_by_price_section(category))
            #在csgo_items中连接上 所有满足价格区间的 category 类别的item
    else:
        # crawl by price section without category
        csgo_items.extend(crawl_goods_by_price_section(None))
        #由于黑白名单不在所获取的categories中,所以 面向全物品 进行搜索,故传入参数 None

    enrich_item_with_price_history(csgo_items)
    #为csgo_items中的所有物品爬取steam价格,并添加到其类的参数中
    return persist_util.tabulate(csgo_items)
    #将尚为列表的csgo_items作为列表输出


def crawl_goods_by_price_section(category=None):
    """
    针对category这一类商品进行价格搜索
    手段是通过buff自带的api接口返回的json
    如果catefory = None 则对全物品进行搜索
    """
    proxy = next(cycle(proxies))
    root_url = goods_section_root_url(category)
    #category对应物品名称
    #根据设置的最高最低价界限
    #获取搜索的根目录,即page = 0 的 api接口
    #由于buff的bug,总搜索结果需要用一个极大的数字去获取,故区分于goods_section_page_url
    log.info('GET: {}'.format(root_url))

    root_json = requester.get_json_dict(root_url,proxy)
    #从api接口中获取json
    """
    json的基本格式如下
    {
      "code": "OK", 
      "data": {
        "items": [], 
        "page_num": 6, 
        "page_size": 20, 
        "total_count": 0, 
        "total_page": 0
      }, 
      "msg": null
    }
    """

    category_items = []

    if root_json is not None:
        if 'data' not in root_json:
        #如果json中没有数据.报错
            log.info('Error happens!')
            log.info('网站返回信息：')
            log.info(root_json)
            if 'error' in root_json:
            #返回error情况
                log.info('错误为: ' + root_json['error'])
            log.info('如果是登录问题，请先在浏览器登录buff，再粘贴正确的cookie到程序中。当前粘贴的cookie为：' + COOKIE)
            sys.exit(1)

        total_page = root_json['data']['total_page']
        total_count = root_json['data']['total_count']
        if total_count == 0:
            log.info('{} 没有符合要求的item!'.format(category))
        else:
            log.info('共有{}件物品item满足爬取条件,一共{}页'.format(total_count, total_page))
        # get each page
        for page_num in range(1, total_page + 1):
            log.info('第 {} 页 / 共 {} 页'.format(page_num, total_page))
            page_url = goods_section_page_url(category, page_num)
            #获取 每页的搜索结果
            proxy = next(cycle(proxies))
            page_json = requester.get_json_dict(page_url,proxy)
            #获取 每页的json目录
            if page_json is not None:
                # items on this page
                items_json = page_json['data']['items']
                for item in items_json:
                    # get item
                    csgo_item = collect_item(item)
                    #从json目录中获取item的价格 名称 等数据
                    #csgo_item是一个特殊的类,其包含各种参数,价格名称等
                    if csgo_item is not None:
                        category_items.append(csgo_item)
                        #将满足条件的item添加到category_item中

    return category_items


def load_local():
    return persist_util.load()


def crawl():
    """
    对是否强制爬取以及是否已经存在爬取本地的文件进行判断
    对网页进行爬取,并返回结果为pd对象的table表格
    """
    log.info("是否强制爬取? {}".format(FORCE_CRAWL))
    #从config参数中判断是否开启FORCE_CRAWL
    if (not FORCE_CRAWL) and os.path.exists(DATABASE_FILE):
        #如果没有开启强制爬取 且 已经存在了爬取的文件数据库 database (每次爬取完成都会在原目录下建立)
        log.info('{} 本地数据库地址已经存在,将从本地进行处理'.format(DATABASE_FILE))
        table = load_local()
        #输出本地的数据库
    else:
        log.info('获取价格区间成功,将爬取{} 到 {} 区间内的物品item'.format(CRAWL_MIN_PRICE_ITEM, CRAWL_MAX_PRICE_ITEM))
        table = crawl_website()
        #从网页进行爬取
    return table
