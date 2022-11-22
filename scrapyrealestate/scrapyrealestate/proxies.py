import requests, json
import requests_html
from lxml.html import fromstring

# from main import args

'''def get_proxyscrape():
    proxies = set()
    collector = proxyscrape.create_collector('default', 'http')  # Create a collector for http resources
    proxies_ = collector.get_proxies()

    for proxy_ in proxies_:
        host = getattr(proxy_, 'host')
        port = getattr(proxy_, 'port')
        proxy = f"{host}:{port}"
        proxies.add(proxy)
    return proxies'''

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

def get_proxies_geonode():
    proxies = set()
    # mirem si esta activada l'entrada de proxies per fixer
    makeservice, proxyfile = args()  # Carreguem arguments.
    if proxyfile:
        print('Entrada proxies per fitxer activada')
        print("Enter the file name with proxies (example: proxies.txt): ")
        proxies_path = input()
        # open text file in read mode
        text_file = open(proxies_path, "r")
        # read whole file to a string
        proxies = text_file.read()

    else:
        url = 'https://proxylist.geonode.com/api/proxy-list?limit=150&page=1&sort_by=lastChecked&sort_type=desc'
        response = requests.get(url)
        response_str = response.text
        response_dict = res = json.loads(response_str)
        for proxy in response_dict["data"]:
            proxy_ = f"{proxy['ip']}:{proxy['port']}"
            proxies.add(proxy_)

    return proxies

'''def get_proxies():
    proxies = set()
    url = 'https://proxylist.geonode.com/api/proxy-list?limit=150&page=1&sort_by=lastChecked&sort_type=desc'
    response = requests.get(url)
    response_str = response.text
    response_dict = res = json.loads(response_str)
    for proxy in response_dict["data"]:
        proxy_ = f"{proxy['ip']}:{proxy['port']}"
        proxies.add(proxy_)

    return proxies'''

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
