import requests
import re

def proxyGet(num):
    header = {}
    header['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0'
    sumray = []
    cout = 0
    for x in range(1,100):
        url = 'https://www.kuaidaili.com/free/inha/' + str(x) +'/'
        response = requests.get(url,headers=header,proxies = {'http':"183.166.71.124"})
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
try:
    proxies = proxyGet(30)
except:
    proxies = [None]