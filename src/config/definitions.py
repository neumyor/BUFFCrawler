import configparser
import json
import os
from datetime import datetime
import sys
"""
用于读取config.INI的参数，具有学习意义
"""

def restart_program():
  python = sys.executable
  os.execl(python, python, * sys.argv)
def config_changer():
    config = configparser.RawConfigParser()

    CONFIG_DIR = 'config'
    CONFIG_FILE_NAME = 'config.ini'
    CONFIG_PATH = os.path.join(os.getcwd(), CONFIG_DIR, CONFIG_FILE_NAME)

    try:
        config.read(CONFIG_PATH, encoding='utf-8')
    except IOError:
        print('File {} does not exist. Exit!'.format(CONFIG_PATH))
        exit(1)

    min = input("输入最低价：")
    max = input("输入最高价：")
    gap = input("输入最大差率：")
    sold = input("输入最低每日交易量：")
    for value,name in zip(enumerate([min,max,gap,sold]),enumerate(['crawl_min_price_item','crawl_max_price_item','max_gap_percentage','min_sold_threshold'])):
        config.set("FILTER",name[1],value[1])
    config.write(open(CONFIG_PATH,"w"))
def config_shower():
    config = configparser.RawConfigParser()

    CONFIG_DIR = 'config'
    CONFIG_FILE_NAME = 'config.ini'
    CONFIG_PATH = os.path.join(os.getcwd(), CONFIG_DIR, CONFIG_FILE_NAME)

    try:
        config.read(CONFIG_PATH, encoding='utf-8')
    except IOError:
        print('File {} does not exist. Exit!'.format(CONFIG_PATH))
        exit(1)

    config_filter = config['FILTER']
    # 最低价不小于0
    CRAWL_MIN_PRICE_ITEM = max(0.01, float(config_filter['crawl_min_price_item']))
    # 最低价 <= 最高价 <= 系统最高限价
    CRAWL_MAX_PRICE_ITEM = min(max(CRAWL_MIN_PRICE_ITEM, float(config_filter['crawl_max_price_item'])),150000)
    # steam该饰品7天最低销售数
    MAX_GAP_PERCENTAGE = int(config_filter['max_gap_percentage'])
    MIN_SOLD_THRESHOLD = int(config_filter['min_sold_threshold'])
    print("\n最低价:{}\n最高价:{}\n最大差率:{}\n最小单日成交量:{}\n".format(CRAWL_MIN_PRICE_ITEM,CRAWL_MAX_PRICE_ITEM,MAX_GAP_PERCENTAGE,MIN_SOLD_THRESHOLD))

config_shower()
confirm = input("请问 是否需要修改参数？ （y/n）： ")
if confirm.lower() == 'y':
    config_changer()

config = configparser.RawConfigParser()

# config
CONFIG_DIR = 'config'
CONFIG_FILE_NAME = 'config.ini'
CONFIG_PATH = os.path.join(os.getcwd(), CONFIG_DIR, CONFIG_FILE_NAME)

try:
    config.read(CONFIG_PATH, encoding='utf-8')
except IOError:
    print('File {} does not exist. Exit!'.format(CONFIG_PATH))
    exit(1)

# `__file__` is relative to the current working directory
# `os.chdir()` can change current working directory, but don't change `__file__`
# so if `os.chdir()` is used, this method fails to get current directory
# current_dir = os.path.dirname(os.path.realpath(__file__))
# COOKIES = open(os.path.join(current_dir, 'cookie.txt'), 'r').readline().strip()

# cookie
COOKIE = config['BASIC']['cookie']

# behavior
config_behavior = config['BEHAVIOR']
GRANULARITY_HOUR = config_behavior.getboolean('granularity_hour')
FORCE_CRAWL = config_behavior.getboolean('force_crawl')
RETRY_TIMES = int(config_behavior['retry_times'])

# common
config_common = config['COMMON']
DOLLAR_TO_CNY = float(config_common['dollar_to_cny'])
STEAM_SELL_TAX = float(config_common['steam_sell_tax'])
TIMESTAMP = str(datetime.now().strftime('%Y-%m-%d-%H:%M:%S'))
BUFF_GOODS_LIMITED_MIN_PRICE = 0.0
# buff系统设定的最高售价，价格查询时不得高于此价格
BUFF_GOODS_LIMITED_MAX_PRICE = 150000.0

# filter
# 爬取历史价格的话，每个都要单独爬一次，爬取量翻了好几十倍，所以扔掉一些，只爬取某个价格区间内的饰品……
# 大致价格分位点：0 - 10000; 20 - 5000; 50 - 4000; 100 - 3400; 200 - 3000; 500 - 2200; 1000 - 1200
config_filter = config['FILTER']
# 最低价不小于0
CRAWL_MIN_PRICE_ITEM = max(BUFF_GOODS_LIMITED_MIN_PRICE, float(config_filter['crawl_min_price_item']))
# 最低价 <= 最高价 <= 系统最高限价
CRAWL_MAX_PRICE_ITEM = min(max(CRAWL_MIN_PRICE_ITEM, float(config_filter['crawl_max_price_item'])), BUFF_GOODS_LIMITED_MAX_PRICE)
# steam该饰品7天最低销售数
MAX_GAP_PERCENTAGE = int(config_filter['max_gap_percentage'])
MIN_SOLD_THRESHOLD = int(config_filter['min_sold_threshold'])

# 黑白名单
CATEGORY_BLACK_LIST = json.loads(config_filter['category_black_list'])
CATEGORY_WHITE_LIST = json.loads(config_filter['category_white_list'])

# result
TOP_N = int(config['RESULT']['top_n'])

# 文件
DATE_DAY = str(datetime.now().strftime('%Y-%m-%d'))
DATE_HOUR = str(datetime.now().strftime('%Y-%m-%d-%H'))
DATE_TIME = DATE_HOUR if GRANULARITY_HOUR else DATE_DAY
PRICE_SECTION = '_{}_{}'.format(CRAWL_MIN_PRICE_ITEM, CRAWL_MAX_PRICE_ITEM)

# data file
DATABASE_PATH = "database"
DATABASE_FILE = os.path.join(DATABASE_PATH, "csgo_skins_" + DATE_TIME + PRICE_SECTION + ".csv")
DATABASE_FILE_DAY = os.path.join(DATABASE_PATH, "csgo_skins_" + DATE_DAY + PRICE_SECTION + ".csv")

# log file
LOG_PATH = "log"
NORMAL_LOGGER = os.path.join(LOG_PATH, '运行日志_' + DATE_TIME + PRICE_SECTION + '.log')

# suggestion file
SUGGESTION_PATH = "suggestion"
SUGGESTION_LOGGER = os.path.join(SUGGESTION_PATH, '生成结果_' + DATE_TIME + PRICE_SECTION + '.txt')
