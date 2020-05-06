from itertools import cycle

import requests
import urllib
import re
from src.test import proxy_pool

def proxyGet(num):
    header = {}
    header['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0'
    sumray = []
    cout = 0
    for x in range(1,100):
        url = 'https://www.kuaidaili.com/free/inha/' + str(x) +'/'
        response = requests.get(url,headers=header)
        html = response.text
        regex = r'<td data-title="IP">(.+)</td>'
        iplist = re.findall(regex, html)
        regex2 = r'<td data-title="PORT">(.+)</td>'
        portlist = re.findall(regex2, html)
        regex3 = r'<td data-title="类型">(.+)</td>'
        typelist = re.findall(regex3, html)
        for i,p,t in zip(iplist,portlist,typelist):
            a = i + ':' + p
            cout = cout + 1
            sumray.append(a)
            if cout == num:
                return sumray

if __name__ == '__main__':
    proxies = proxyGet(10)
    # proxies = proxy_pool.get()
    print(proxies)

    url = 'https://www.baidu.com/index.html'
    for i in range(1, 11):
        # Get a proxy from the pool
        proxy = next(cycle(proxies))
        print("Request #{} to proxy {}".format(i,proxy) )
        try:
            # 先创建代理ip对象
            proxy_support = urllib.request.ProxyHandler({'http': proxy})

            opener = urllib.request.build_opener(proxy_support)

            urllib.request.install_opener(opener)

            # 发出请求时，就是用到这个代理地址了
            html = urllib.request.urlopen(url).read()
            print(html)
        except:
            print("Skipping. Connnection error")
