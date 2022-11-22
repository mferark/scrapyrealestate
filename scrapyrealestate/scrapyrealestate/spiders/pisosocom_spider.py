import scrapy, os, logging, time
from scrapyrealestate.proxies import *
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
from bs4 import BeautifulSoup
#from items import ScrapyrealestateItem # ERROR (es confundeix amb items al 192.168.1.100)
from scrapyrealestate.items import ScrapyrealestateItem

class PisoscomSpider(CrawlSpider):
    name = "pisoscom"
    allowed_domains = ["pisos.com"]
    total_time = 0
    #start_urls = data['idealista_data']['urls']

    def start_requests(self):
        #start_urls = [url + '?ordenado-por=fecha-publicacion-desc' for url in self.start_urls]
        yield scrapy.Request(f'{self.start_urls}')

    total_urls_pass = 1  # Inicialitzem contador

    custom_settings = {
        #'ROTATING_PROXY_PAGE_RETRY_TIMES': 99999999999,  # TODO: is it possible to setup this parameter with no limit?
        #'ROTATING_PROXY_LIST': get_proxies(),
        #"FEEDS": {f"{data['data_path']}/{data['idealista_data']['db_name']}.json": {"format": "json"}},
        'DEFAULT_REQUEST_HEADERS': {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'es-ES,es;q=0.9,ca;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'sec-gpc': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
        }
    }

    # Si esta activat el mode rapid, NO agafem la seguent URL
    '''if not data['speed_mode']:
        rules = (
            # Filter all the flats paginated by the website following the pattern indicated
            Rule(LinkExtractor(restrict_xpaths=("//a[@class='icon-arrow-right-after']")),
                 callback='parse',  # cridem la funcio parse de nou
                 follow=True),  # Seguim l'enllaç
        )'''

    def parse(self, response):
        start_time = time.time()
        ids = []
        same_id = False
        # Import items
        items = ScrapyrealestateItem()

        # Necessary in order to create the whole link towards the website
        default_url = 'https://pisos.com'
        # Passem la resposta a text amb BeautifulSoup
        soup = BeautifulSoup(response.text, 'lxml')

        # Agafem els div de tots els habitatges de la pàgina
        # div --> class="ad-preview__info"
        flats = soup.find_all("div", {"class": "ad-preview__info"})

        # Iterem per cada numero d'habitatge de la pàgina i agafem les dades
        for nflat in range(len(flats)):
            # Validem i agafem l'enllaç (ha de ser el link del habitatge)
            # a --> class="item-link" --> href
            # href = flats[nflat].find("a", {"class": "item-link"})['href']

            href = flats[nflat].find(class_="ad-preview__title")['href']
            title = flats[nflat].find(class_="ad-preview__title").text.strip()
            try:
                id = href.split('-')[2].split('_')[0]
                # Si la id ja era a la llista, sortim
                for id_ in ids:
                    if id_ == id:
                        same_id = True
                        break
            except:
                id = ''

            # span --> class="item-price h2-simulated" --> span .text
            price = flats[nflat].find("span", {"class": "ad-preview__price"}).text.strip()
            # span --> class="item-detail" --> [nflat] --> span .text
            rooms = flats[nflat].find_all("p", {"class": "ad-preview__char p-sm"})[0].text.strip()
            # Hi ha pisos sense m2, data o planta. Per evitar problemes assignem variable buida si hi ha error.
            try:
                m2 = flats[nflat].find_all("p", {"class": "ad-preview__char p-sm"})[2].text.strip()
            except:
                m2 = ""
            try:
                floor = flats[nflat].find_all("p", {"class": "ad-preview__char p-sm"})[3].text.strip()
            except:
                floor = ""

            # Si esta activat, passem al seguent ja que repeteix ids
            if same_id:
                continue
            else:
                # Add items
                items['id'] = id
                items['title'] = title
                items['price'] = price.replace(' ', '')
                items['rooms'] = rooms
                items['m2'] = m2
                items['floor'] = floor
                items['href'] = default_url + href

                yield items

        # Mostrem log de total de pàgines i temps
        end_time = time.time()
        self.total_time += end_time  # Sumem el temps total
        # Notifiquem pagines total al log
        #logger.info(f'PAGES SCRAPED TIME ({str(end_time - start_time)[:4]}s)')

        self.total_urls_pass += 1  # Sumem 1 al total de pàgines

    # Overriding parse_start_url to get the first page
    parse_start_url = parse
