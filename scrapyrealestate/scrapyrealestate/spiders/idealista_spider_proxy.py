import scrapy, os, logging, time
from scrapyrealestate.proxies import *
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
from bs4 import BeautifulSoup
#from items import ScrapyrealestateItem # ERROR (es confundeix amb items al 192.168.1.100)
from scrapyrealestate.items import ScrapyrealestateItem

class IdealistaSpider(CrawlSpider):
    name = "idealista_proxy"
    allowed_domains = ["idealista.com"]
    total_time = 0
    #start_urls = data['idealista_data']['urls']

    def start_requests(self):
        #start_urls = [url + '?ordenado-por=fecha-publicacion-desc' for url in self.start_urls]
        yield scrapy.Request(f'{self.start_urls}')

    total_urls_pass = 1  # Inicialitzem contador

    custom_settings = {
        'ROTATING_PROXY_PAGE_RETRY_TIMES': 99999999999,  # TODO: is it possible to setup this parameter with no limit?
        'ROTATING_PROXY_LIST': get_proxies(),
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
            #'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'

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
        default_url = 'https://idealista.com'
        # Passem la resposta a text amb BeautifulSoup
        soup = BeautifulSoup(response.text, 'lxml')

        # Agafem els div de tots els habitatges de la pàgina
        flats = soup.find_all("div", {"class": "item-info-container"})

        # Obtenim si es de lloguer o compra a partir de la url
        if self.start_urls.split('/')[3].split('-')[0] == 'alquiler':
            type = 'rent'
        elif self.start_urls.split('/')[3].split('-')[0] == 'venta':
            type = 'buy'

        # Iterem per cada numero d'habitatge de la pàgina i agafem les dades
        for nflat in range(len(flats)):
            # Agafem href, title, price, details
            href = flats[nflat].find(class_="item-link")['href']
            title = flats[nflat].find(class_="item-link").text.strip()
            #print(title)
            # Intentem agafar ciutat, barri i carrer
            # A idealista pot haver 4 tipus de titol, d'ob obtindrem aquestes dades
            neighbour = ''
            street = ''
            number = ''
            town = ''
            # Piso en Passatge de I'Olivera, 12, La Maurina, Terrassa (4)
            if len(title.split(',')) == 4:
                town = title.split(',')[-1]
                number = title.split(',')[1]
                neighbour = title.split(',')[2]
                street = title.split(',')[0].split(' en ')[-1]
            # Piso en Passatge de I'Olivera, La Maurina, Terrassa (3)
            elif len(title.split(',')) == 3:
                town = title.split(',')[-1]
                neighbour = title.split(',')[1]
                street = title.split(',')[0].split(' en ')[-1]
            # Ático en Centre, Terrassa (2)
            elif len(title.split(',')) == 2:
                town = title.split(',')[-1]
                neighbour = title.split(',')[0].split(' en ')[-1]
            else:
                street = ''
                neighbour = ''
                if len(town) > 12:
                    town = town.split(' en ')[-1]
                if town[:1] == ' ':
                    town = town[1:]
            try:
                if town[0] == ' ':
                    town = town[1:]
            except:
                pass
            try:
                if ' / ' in town:
                    town = town.split(' / ')[1]
            except:
                pass
            try:
                if neighbour[0] == ' ':
                    neighbour = neighbour[1:]
            except:
                pass
            try:
                if number[0] == ' ':
                    number = number[1:]
            except:
                pass

            # busquem posibles noms de carrers
            if len(street) > 0:
                if 'calle' in street.lower():
                    street = street
                elif 'c.' in street.lower():
                    street = street
                elif 'avenida' in street.lower():
                    street = street
                elif 'av.' in street.lower():
                    street = street
                elif 'plaza' in street.lower():
                    street = street.replace('plaza', 'plaça')
                elif 'via' in street.lower():
                    street = street
                elif 'gran via' in street.lower():
                    street = street
                elif 'camino' in street.lower():
                    street = street
                elif 'paseo' in street.lower():
                    street = street
                elif 'passaje' in street.lower():
                    street = street
                elif 'carretera' in street.lower():
                    street = street
                elif 'ctra.' in street.lower():
                    street = street
                else:
                    street = street

            #print(f"MUNICIPI: {town}, STREET: {street}, BARRI: {neighbour}, NUMBER: {number}")
            price = flats[nflat].find("span", {"class": "item-price h2-simulated"}).text.strip()

            details = flats[nflat].find_all("span", {"class": "item-detail"})
            # Agafem id
            try:
                id = href.split('/')[2]
                # Si la id ja era a la llista, sortim
                for id_ in ids:
                    if id_ == id:
                        same_id = True
                        break
            except:
                id = ''

            # Iterem els elements de details per identificar cada un (hab, m², planta, hora)
            for d in details[0:3]:
                # print(d.text.strip()[1:])
                if d.text.strip()[-4:] == 'hab.':
                    rooms = d.text.strip()
                    continue
                elif d.text.strip()[-2:] == 'm²':
                    m2 = d.text.strip()
                    continue
                elif 'Planta' in d.text.strip() or 'Bajo' in d.text.strip() or 'Sótano' in d.text.strip() or 'Entreplanta' in d.text.strip():
                    floor = d.text.strip()
                    continue
                # Si alguna de les variables no existeixen, les creem buides
                # Hi ha pisos sense data o planta. Per evitar problemes assignem variable buida.
                else:
                    if not 'rooms' in locals(): rooms = ''
                    if not 'm2' in locals(): m2 = ''
                    if not 'floor' in locals(): floor = ''

            # Si esta activat, passem al seguent ja que repeteix ids
            if same_id:
                continue
            else:
                # Add items
                items['id'] = id
                items['price'] = price
                items['m2'] = m2
                items['rooms'] = rooms
                try:
                    items['floor'] = floor  # sino peta llocs sense pisos (pe. cerdanya francesa)
                except:
                    items['floor'] = ''
                items['town'] = town
                items['neighbour'] = neighbour
                items['street'] = street
                items['number'] = number
                items['type'] = type
                items['title'] = title
                items['href'] = default_url + href
                items['site'] = 'idealista'
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
