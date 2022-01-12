import requests
import requests_html
from lxml.html import fromstring

def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:250]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            #Grabbing IP and corresponding PORT
            # Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies

def get_proxies_json():
    url = 'https://proxylist.geonode.com/api/proxy-list?limit=150&page=1&sort_by=speed&sort_type=asc'
    response = requests.get(url)
    response.json()
    proxies = set()
    for p in response.json()['data']:
        proxy = f"{p['ip']}:{p['port']}"
        proxies.add(proxy)
    return proxies

def get_proxies_txt():
    file = open('proxies/proxies.txt', "r")
    proxies = set()
    for proxy in file:
        #proxy = f"{p['ip']}:{p['port']}"
        proxies.add(proxy.replace('\n', ''))
    return proxies

def get_allproxies():
    proxies = set()
    proxies = get_proxies()
    proxie_json = get_proxies_json()
    #proxies = proxie_txt.update(proxie_json)
    proxies |= proxie_json
    return proxies