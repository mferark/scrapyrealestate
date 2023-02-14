import scrapy, os, logging, time, re
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

        # Obtenim si es de lloguer o compra a partir de la url
        if self.start_urls.split('/')[3] == 'alquiler':
            type = 'rent'
        elif self.start_urls.split('/')[3] == 'venta':
            type = 'buy'

        # Iterem per cada numero d'habitatge de la pàgina i agafem les dades
        for nflat in range(len(flats)):
            # Validem i agafem l'enllaç (ha de ser el link del habitatge)
            # a --> class="item-link" --> href
            # href = flats[nflat].find("a", {"class": "item-link"})['href']

            href = flats[nflat].find(class_="ad-preview__title")['href']
            title = flats[nflat].find(class_="ad-preview__title").text.strip()
            # Intentem obtenir municipi, carrer i barri
            # Piso en Sant Pere Nord
            # Sant Pere Nord (Distrito Sant Pere Nord-Ègara. Terrassa)
            town = ''
            neighbour = ''
            street = ''
            number = ''
            if len(title.split(',')) == 2:
                street_ = title.split(',')[0]
                number = title.split(',')[-1]
            elif len(title.split(',')) == 1:
                street_ = flats[nflat].find(class_="ad-preview__title").text.strip().split(' en ')[-1]
            # busquem posibles noms de carrers
            if len(street_) > 0:
                if 'calle' in street_.lower():
                    street = street_
                elif 'carrer' in street_.lower():
                    street = street_
                elif 'c.' in street_.lower():
                    street = street_
                elif 'avenida' in street_.lower():
                    street = street_
                elif 'avinguda' in street_.lower():
                    street = street_
                elif 'av.' in street_.lower():
                    street = street_
                elif 'plaza' in street_.lower():
                    street = street_
                elif 'plaça' in street_.lower():
                    street = street_
                elif 'via' in street_.lower():
                    street = street_
                elif 'gran via' in street_.lower():
                    street = street_
                elif 'travessera' in street_.lower():
                    street = street_
                elif 'camino' in street_.lower():
                    street = street_
                elif 'cami' in street_.lower():
                    street = street_
                elif 'paseo' in street_.lower():
                    street = street_
                elif 'passeig' in street_.lower():
                    street = street_
                elif 'passaje' in street_.lower():
                    street = street_
                elif 'passatge' in street_.lower():
                    street = street_
                elif 'carretera' in street_.lower():
                    street = street_
                elif 'ctra.' in street_.lower():
                    street = street_
                else:
                    pass

            town_ = flats[nflat].find(class_="p-sm").text.strip()
            if '(' in town_:
                neighbour = town_.split('(')[0][:-1]
                town = town_[town_.find('(') + 1:town_.find(')')]
                if 'Distrito' in town:
                    if '.' in town:
                        town = town.split('.')[-1].split(' ')[1]
                    elif 'Capital' in town:
                        town = town.replace('Capital', '').replace(' ', '')
                elif 'Capital' in town:
                    town = town.replace('Capital', '').replace(' ', '')
            else:
                town = town_
            try:
                if ' - ' in town:
                    town = town.split(' - ')[0]
                elif '-' in town_:
                    town = town.split('-')[0]
            except:
                pass

            #print(f"MUNICIPI: {town}, STREET: {street}, BARRI: {neighbour}, NUMBER: {number}")

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
            # # Hi ha pisos sense m2, data o planta. Per evitar problemes assignem variable buida si hi ha error.
            # try:
            #     m2 = flats[nflat].find_all("p", {"class": "ad-preview__char p-sm"})[2].text.strip()
            # except IndexError:
            #     m2 = flats[nflat].find_all("p", {"class": "ad-preview__char p-sm"})[1].text.strip()
            # except:
            #     m2 = ""
            try:
                m2_elements = flats[nflat].find_all("p", {"class": "ad-preview__char p-sm"})
                if len(m2_elements) >= 3:
                    m2 = m2_elements[2].text.strip()
                else:
                    m2 = ""
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
                items['price'] = price
                items['m2'] = m2
                items['rooms'] = rooms
                items['floor'] = floor
                items['town'] = town
                items['neighbour'] = neighbour
                items['street'] = street
                items['number'] = number
                items['type'] = type
                items['title'] = title
                items['href'] = default_url + href
                items['site'] = 'pisoscom'
                ids.append(id)

                yield items

        # Mostrem log de total de pàgines i temps
        end_time = time.time()
        self.total_time += end_time  # Sumem el temps total
        # Notifiquem pagines total al log
        #logger.info(f'PAGES SCRAPED TIME ({str(end_time - start_time)[:4]}s)')

        self.total_urls_pass += 1  # Sumem 1 al total de pàgines

    # Overriding parse_start_url to get the first page
    parse_start_url = parse
