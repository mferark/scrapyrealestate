import scrapy, os
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
from bs4 import BeautifulSoup
#from items import ScrapyrealestateItem # ERROR (es confundeix amb items al 192.168.1.100)
from scrapyrealestate.items import ScrapyrealestateItem

class FotocasaSpider(CrawlSpider):
    name = "yaencontre"
    allowed_domains = ["yaencontre"]
    start_urls = ['https://www.yaencontre.com/alquiler/pisos/barcelona/o-recientes']

    '''def start_requests(self):
        #start_urls = [url + '?ordenado-por=fecha-publicacion-desc' for url in self.start_urls]
        yield scrapy.Request(f'{self.start_urls}')'''

    custom_settings = {
        # 'ROTATING_PROXY_PAGE_RETRY_TIMES': 99999999999,  # TODO: is it possible to setup this parameter with no limit?
        # 'ROTATING_PROXY_LIST': get_proxies(),
        # 'DOWNLOAD_FAIL_ON_DATALOSS': False,
        # 'DOWNLOAD_DELAY': 1.25,
        # "FEEDS": {"data/idealista.json": {"format": "json"}},
        'DEFAULT_REQUEST_HEADERS': {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
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

    rules = (
        # Filter all the flats paginated by the website following the pattern indicated
        Rule(LinkExtractor(restrict_xpaths=("//a[@class='sui-LinkBasic sui-AtomButton sui-AtomButton--primary sui-AtomButton--outline sui-AtomButton--center sui-AtomButton--small sui-AtomButton--link sui-AtomButton--empty']")),
             callback='parse',  # cridem la funcio parse de nou
             follow=True),  # Seguim l'enllaç
    )

    def parse(self, response):
        # Import items
        items = ScrapyrealestateItem()

        # Necessary in order to create the whole link towards the website
        default_url = 'https://yaencontre.es'
        # Passem la resposta a text amb BeautifulSoup
        soup = BeautifulSoup(response.text, 'lxml')
        print(soup.decode("utf8"))

        flats = soup.find_all("div", {"class": "content"})
        print(flats)

        # div --> class="pagination" --> ul --> li --> class="next"
        try:
            next_page = soup.find("div", {"class": "pagination"}).find("a", {"class": "icon-arrow-right-after"})['href']
        except:
            next_page = ""
        # Iterem per cada numero d'habitatge de la pàgina i agafem les dades
        for nflat in range(len(flats)):
            #print(flats[nflat])
            # Validem i agafem l'enllaç (ha de ser el link del habitatge)
            # a --> class="item-link" --> href
            # href = flats[nflat].find("a", {"class": "item-link"})['href']

            try:
                href = flats[nflat].find("h2", {"class": "title d-ellipsis logo-aside"}).find("a", href=True)['href']
                print(href)
            except:
                break; # Si no troba res sortim del bucle

            try:
                title = flats[nflat].find("h2", {"class": "title d-ellipsis logo-aside"}).text.strip()
            except:
                title = ''

            try:
                id = href.split('-')[1]
            except:
                id = ''

            # span --> class="item-price h2-simulated" --> span .text
            try:
                price = flats[nflat].find("div", {"class": "price-wrapper inline-flex logo-aside"}).text.strip()
            except:
                price = ''

            # span --> class="item-detail" --> [nflat] --> span .text
            try:
                rooms = flats[nflat].find_all("div", {"class": "iconGroup"})[nflat].find("div", {"class": "icon-room"}).text.strip()
                print(rooms)
            except:
                rooms = ''

            try:
                m2 = flats[nflat].find_all("div", {"class": "iconGroup"})[nflat].find("div", {"class": "icon-meter"}).text.strip()
            except:
                m2 = ''

            '''try:
                bath = flats[nflat].find_all("div", {"class": "iconGroup"})[nflat].find("div", {"class": "icon-bath"}).text.strip()
            except:
                bath = '''''

            # Hi ha pisos sense data o planta. Per evitar problemes assignem variable buida si hi ha error.
            try:
                floor = flats[nflat].find_all("span", {"class": "re-CardFeatures-feature"})[5].text.strip()
            except:
                floor = ""
            try:
                post_time = flats[nflat].find_all("span", {"class": "re-CardFeatures-feature"})[5].text.strip()
            except:
                post_time = ""

            # Add items
            items['id'] = id
            items['title'] = title
            items['price'] = price
            items['rooms'] = rooms
            items['m2'] = m2
            items['floor'] = floor
            items['post_time'] = post_time
            items['href'] = default_url + href

            yield items

    # Overriding parse_start_url to get the first page
    parse_start_url = parse
