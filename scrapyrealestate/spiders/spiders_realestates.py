import json
from urllib.request import urlopen
import time, re
from scrapyrealestate.proxies import *
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from bs4 import BeautifulSoup
from scrapyrealestate.items import ScrapyrealestateItem  # ERROR (es confundeix amb items al 192.168.1.100)
# from scrapyrealestate.items import ScrapyrealestateItem
from main import get_urls


class IdealistaSpider(CrawlSpider):
    name = "idealista"
    allowed_domains = ["idealista.com"]
    total_time = 0

    urls = get_urls()
    start_urls = urls['start_urls_idealista']

    # Guardem el numero total de pàgines per fer scrap
    total_urls_pass = 1  # Inicialitzem contador

    custom_settings = {
        'ROTATING_PROXY_PAGE_RETRY_TIMES': 99999999999,  # TODO: is it possible to setup this parameter with no limit?
        'ROTATING_PROXY_LIST': get_proxies(),
        # 'DOWNLOAD_FAIL_ON_DATALOSS': False,
        # 'DOWNLOAD_DELAY': 1.25,
        "FEEDS": {"data/idealista.json": {"format": "json"}},
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

        # Iterem per cada numero d'habitatge de la pàgina i agafem les dades
        for nflat in range(len(flats)):
            # Agafem href, title, price, details
            href = flats[nflat].find(class_="item-link")['href']
            title = flats[nflat].find(class_="item-link").text.strip()
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
                items['title'] = title
                items['price'] = price
                items['rooms'] = rooms
                items['m2'] = m2
                items['floor'] = floor
                items['href'] = default_url + href
                ids.append(id)

                yield items

        # Mostrem log de total de pàgines i temps
        end_time = time.time()
        self.total_time += end_time  # Sumem el temps total
        # Notifiquem pagines total al log
        # logging.info(f'PAGES SCRAPED [{self.total_urls_pass}/{self.total_urls}] ({str(end_time - start_time)[:4]}s)')

        self.total_urls_pass += 1  # Sumem 1 al total de pàgines

    # Overriding parse_start_url to get the first page
    parse_start_url = parse


class PisoscomSpider(CrawlSpider):
    #  Si existeix json anterior, l'eliminem
    # if os.path.exists(f"{'data'}/{data['pisoscom_data']['db_name']}.json"):
    #    os.remove(f"{'data'}/{data['pisoscom_data']['db_name']}.json")

    name = "pisoscom"
    allowed_domains = ["pisos.com"]
    total_time = 0

    urls = get_urls()
    start_urls = urls['start_urls_pisoscom']

    total_urls_pass = 1  # Inicialitzem contador

    custom_settings = {
        "FEEDS": {"data/pisoscom.json": {"format": "json"}},
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
            try:
                rooms = flats[nflat].find_all("p", {"class": "ad-preview__char p-sm"})[0].text.strip()
            except:
                rooms = ""
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
                items['price'] = price
                items['rooms'] = rooms
                items['m2'] = m2
                items['floor'] = floor
                items['href'] = default_url + href

                yield items

        # Mostrem log de total de pàgines i temps
        end_time = time.time()
        self.total_time += end_time  # Sumem el temps total
        # Notifiquem pagines total al log
        # logging.info(f'PAGES SCRAPED [{self.total_urls_pass}/{self.total_urls}] ({str(end_time - start_time)[:4]}s)')
        # if self.total_urls_pass % 5 == 0:
        # Notifiquem al grup de logs de telegram cada 5
        # tb.send_message(data['telegram'][''1001647968081''], f'PAGES SCRAPED [{self.total_urls_pass}/{self.total_urls}] ({str(end_time - start_time)[:4]}s)')

        self.total_urls_pass += 1  # Sumem 1 al total de pàgines

    # logging.info(f'TOTAL SCRAP TIME: {str(total_time)[:4]}s')  # Mostrem temps total

    # Overriding parse_start_url to get the first page
    parse_start_url = parse


class FotocasaSpider(CrawlSpider):
    name = "fotocasa"
    allowed_domains = ["fotocasa"]

    urls = get_urls()
    start_urls = urls['start_urls_fotocasa']

    custom_settings = {
        # 'DOWNLOAD_DELAY': 2,
        # 'ITEM_PIPELINES': {
        #    'freedom.pipelines.IndexPipeline': 300
        # },
        "FEEDS": {"data/fotocasa.json": {"format": "json"}},
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

    def parse(self, response):
        # Import items
        items = ScrapyrealestateItem()

        # Necessary in order to create the whole link towards the website
        default_url = 'https://fotocasa.es'
        # Passem la resposta a text amb BeautifulSoup
        soup = BeautifulSoup(response.text, 'lxml')

        # Agafem els div de tots els habitatges de la pàgina
        # <div class="item-info-container"><a aria-level="2" class="item-link" href="/inmueble/95416252/?xtmc=2_1_08030&amp;xtcr=0" role="heading" title="Piso en calle de Concepción Arenal, Sant Andreu, Barcelona">Piso en calle de Concepción Arenal, Sant Andreu, Barcelona</a><div class="price-row"><span class="item-price h2-simulated">800<span class="txt-big">€/mes</span></span></div><span class="item-detail">3 <small>hab.</small></span><span class="item-detail">60 <small>m²</small></span><span class="item-detail">Planta 3ª <small>exterior con ascensor</small></span><span class="item-detail"><small class="txt-highlight-red">5 horas</small></span><div class="item-description description"><p class="ellipsis">Piso con salón luminoso y habitación doble soleada. Dispone de tres habitaciones: una doble y dos individuales. Baño y cocina en perfecto...</p></div><div class="item-toolbar"><span class="icon-phone item-not-clickable-phone">935 437 953</span><a class="icon-phone phone-btn item-clickable-phone" href="tel:+34 935437953" target="_blank"><span>Llamar</span></a><button class="icon-chat email-btn action-email fake-anchor"><span>Contactar</span></button><button class="favorite-btn action-fav fake-anchor" data-role="add" data-text-add="Guardar" data-text-remove="Favorito" title="Guardar"><i class="icon-heart" role="image"></i><span>Guardar</span></button><button class="icon-delete trash-btn action-discard fake-anchor" data-role="add" data-text-remove="Descartar" rel="nofollow" title="Descartar"></button></div></div>
        # flats = response.css('div.item-info-container')
        # div --> class="item-info-container"
        # flats = soup.find_all("div", {"class": "re-Searchresult-itemRow"})
        flats = soup.find_all("div", {"class": "re-CardPackMinimal-info"})  # Canvi de div - 10/11/2021

        # div --> class="pagination" --> ul --> li --> class="next"
        try:
            next_page = soup.find("div", {"class": "pagination"}).find("a", {"class": "icon-arrow-right-after"})['href']
        except:
            next_page = ""
        # Iterem per cada numero d'habitatge de la pàgina i agafem les dades
        for nflat in range(len(flats)):
            # Validem i agafem l'enllaç (ha de ser el link del habitatge)
            # a --> class="item-link" --> href
            # href = flats[nflat].find("a", {"class": "item-link"})['href']
            try:
                # href = flats[nflat].find("a", {"class": "re-CardPackMinimal-slider"}, href=True)['href']
                href = flats[nflat].find("a", {"class": "re-CardPackMinimal-info-container"}, href=True)[
                    'href']  # Canvi de div - 10/11/2021

            except:
                break;  # Si no troba res sortim del bucle

            try:
                title = flats[nflat].find("span", {"class": "re-CardTitle"}).text.strip()
            except:
                title = ''

            try:
                id = href.split('/')[6]
            except:
                id = ''

            # span --> class="item-price h2-simulated" --> span .text
            try:
                price = flats[nflat].find("span", {"class": "re-CardPrice"}).text.strip()
            except:
                price = ''

            # span --> class="item-detail" --> [nflat] --> span .text
            try:
                rooms = flats[nflat].find_all("span", {"class": "re-CardFeatures-feature"})[0].text.strip()
            except:
                rooms = ''

            try:
                m2 = flats[nflat].find_all("span", {"class": "re-CardFeatures-feature"})[2].text.strip()
            except:
                m2 = ''

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


class FotocasaSpider_json(CrawlSpider):
    name = "fotocasa_json"
    allowed_domains = ["fotocasa"]
    total_time = 0

    urls = get_urls()
    start_urls = urls['start_urls_fotocasa']

    # Guardem el numero total de pàgines per fer scrap
    total_urls_pass = 1  # Inicialitzem contador

    custom_settings = {
        # 'DOWNLOAD_DELAY': 2,
        # 'ITEM_PIPELINES': {
        #    'freedom.pipelines.IndexPipeline': 300
        # },
        "FEEDS": {"data/fotocasa.json": {"format": "json"}},
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
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
        }
    }

    rules = (
        # Filter all the flats paginated by the website following the pattern indicated
        Rule(LinkExtractor(restrict_xpaths=(
            "//a[@class='sui-LinkBasic sui-AtomButton sui-AtomButton--primary sui-AtomButton--outline sui-AtomButton--center sui-AtomButton--small sui-AtomButton--link sui-AtomButton--empty']")),
            callback='parse',  # cridem la funcio parse de nou
            follow=True),  # Seguim l'enllaç
    )

    def parse(self, response):
        start_time = time.time()
        ids = []
        same_id = False

        # Import items
        items = ScrapyrealestateItem()

        # Necessary in order to create the whole link towards the website
        default_url = 'https://fotocasa.es'
        response = urlopen(self.start_urls[0])

        # storing the JSON response
        # from url in data
        data_json = json.loads(response.read())
        flats = data_json.get('realEstates')
        '''try:
            next_page = soup.find("div", {"class": "pagination"}).find("a", {"class": "icon-arrow-right-after"})['href']
        except:
            next_page = ""'''
        # Iterem per cada numero d'habitatge de la pàgina i agafem les dades
        for nflat in range(len(flats)):
            # Validem i agafem l'enllaç (ha de ser el link del habitatge)
            try:
                href = flats[nflat].get('detail').get('es')
            except:
                break;  # Si no troba res sortim del bucle

            try:
                title = flats[nflat].find("span", {"class": "re-CardTitle"}).text.strip()
            except:
                title = ''

            try:
                id = flats[nflat].get('id')
            except:
                id = ''

            try:
                price = flats[nflat].get('transactions')[0].get('value')[0]
            except:
                price = ''

            try:
                for n in range(len(flats[nflat].get('features'))):
                    if flats[nflat].get('features')[n].get('key') == 'rooms':
                        rooms = flats[nflat].get('features')[n].get('value')[0]
            except:
                rooms = ''

            try:
                for n in range(len(flats[nflat].get('features'))):
                    if flats[nflat].get('features')[n].get('key') == 'surface':
                        m2 = flats[nflat].get('features')[n].get('value')[0]
            except:
                m2 = ''

            # Hi ha pisos sense data o planta. Per evitar problemes assignem variable buida si hi ha error.
            try:
                floor = flats[nflat].find_all("span", {"class": "re-CardFeatures-feature"})[5].text.strip()
            except:
                floor = ""

            # Si esta activat, passem al seguent ja que repeteix ids
            if same_id:
                continue
            else:
                # Add items
                items['id'] = id
                items['title'] = title
                items['price'] = price
                items['rooms'] = rooms
                items['m2'] = m2
                items['floor'] = floor
                items['href'] = default_url + href
                ids.append(id)

                yield items

    # Overriding parse_start_url to get the first page
    parse_start_url = parse


class HabitacliaSpider(CrawlSpider):
    name = "habitaclia"
    allowed_domains = ["habitaclia.com"]

    urls = get_urls()
    start_urls = urls['start_urls_habitaclia']

    total_time = 0
    # Guardem el numero total de pàgines per fer scrap
    total_urls_pass = 1  # Inicialitzem contador
    custom_settings = {
        # 'DOWNLOAD_DELAY': 2,
        # 'ITEM_PIPELINES': {
        #    'freedom.pipelines.IndexPipeline': 300
        # },
        "FEEDS": {"data/habitaclia.json": {"format": "json"}},
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

    '''
    def start_requests(self):
        urls = [
            'https://www.idealista.com/buscar/alquiler-viviendas/08030/'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
            '''

    def parse(self, response):
        start_time = time.time()
        ids = []
        same_id = False
        # Import items
        items = ScrapyrealestateItem()

        # Necessary in order to create the whole link towards the website
        default_url = 'https://habitaclia.com'
        # Passem la resposta a text amb BeautifulSoup
        soup = BeautifulSoup(response.text, 'lxml')

        # Agafem els div de tots els habitatges de la pàgina
        # <div class="item-info-container"><a aria-level="2" class="item-link" href="/inmueble/95416252/?xtmc=2_1_08030&amp;xtcr=0" role="heading" title="Piso en calle de Concepción Arenal, Sant Andreu, Barcelona">Piso en calle de Concepción Arenal, Sant Andreu, Barcelona</a><div class="price-row"><span class="item-price h2-simulated">800<span class="txt-big">€/mes</span></span></div><span class="item-detail">3 <small>hab.</small></span><span class="item-detail">60 <small>m²</small></span><span class="item-detail">Planta 3ª <small>exterior con ascensor</small></span><span class="item-detail"><small class="txt-highlight-red">5 horas</small></span><div class="item-description description"><p class="ellipsis">Piso con salón luminoso y habitación doble soleada. Dispone de tres habitaciones: una doble y dos individuales. Baño y cocina en perfecto...</p></div><div class="item-toolbar"><span class="icon-phone item-not-clickable-phone">935 437 953</span><a class="icon-phone phone-btn item-clickable-phone" href="tel:+34 935437953" target="_blank"><span>Llamar</span></a><button class="icon-chat email-btn action-email fake-anchor"><span>Contactar</span></button><button class="favorite-btn action-fav fake-anchor" data-role="add" data-text-add="Guardar" data-text-remove="Favorito" title="Guardar"><i class="icon-heart" role="image"></i><span>Guardar</span></button><button class="icon-delete trash-btn action-discard fake-anchor" data-role="add" data-text-remove="Descartar" rel="nofollow" title="Descartar"></button></div></div>
        # flats = response.css('div.item-info-container')
        # div --> class="item-info-container"
        flats = soup.find_all("div", {"class": "list-item"})
        # div --> class="pagination" --> ul --> li --> class="next"
        try:
            next_page = soup.find("li", {"class": "next"}).find("a")['href']
        except:
            next_page = ""
            # Si veiem que no hi ha mes links, sortim sense agafar els pisos
            # de l'ultima pàgina ja que dona molts problemes
            # return

        # Iterem per cada numero d'habitatge de la pàgina i agafem les dades
        for nflat in range(len(flats)):
            # Validem i agafem l'enllaç (ha de ser el link del habitatge)
            # a --> class="item-link" --> href
            try:
                over_flat = flats[nflat].find("span", {"class": "ady-relationship"}).text.strip()
            except:
                over_flat = ''

            # Si over_flat conte alguna cosa, sortim del bucle
            if over_flat != '':
                break

            href = flats[nflat].find("h3", {"class": "list-item-title"}).find("a", href=True)['href']

            try:
                title = flats[nflat].find("h3", {"class": "list-item-title"}).find("a").text.strip()
            except:
                title = ''

            # span --> class="item-price h2-simulated" --> span .text
            try:
                price = flats[nflat].find("span", {"class": "font-2"}).text.strip()
            except:
                price = ''

            # span --> class="item-detail" --> [nflat] --> span .text
            try:
                rooms = flats[nflat].find("p", {"class": "list-item-feature"}).text.strip().split('-')[1][1:6]
            except:
                rooms = ''

            try:
                m2 = flats[nflat].find("p", {"class": "list-item-feature"}).text.strip().split('-')[0][:4]
            except:
                m2 = ''

            # Hi ha pisos sense data o planta. Per evitar problemes assignem variable buida si hi ha error.
            try:
                floor = flats[nflat].find_all("span", {"class": "re-CardFeatures-feature"})[5].text.strip()
            except:
                floor = ""
            try:
                post_time = flats[nflat].find_all("span", {"class": "re-CardFeatures-feature"})[5].text.strip()
            except:
                post_time = ""

            # Posem els numeros de la href a una llista. Mirem de la llista qui te +10 len(), aquest es el id.
            # id = ""
            for n in re.findall(r"\d+", href):
                if len(n) > 6:
                    id = n

            # Si esta activat, passem al seguent ja que repeteix ids
            if same_id:
                continue
            else:
                # Add items
                items['id'] = id
                items['title'] = title
                items['price'] = price
                items['rooms'] = rooms
                items['m2'] = m2
                items['floor'] = floor
                items['post_time'] = post_time
                items['href'] = href

                yield items

        # Mostrem log de total de pàgines i temps
        end_time = time.time()
        self.total_time += end_time  # Sumem el temps total
        # Notifiquem pagines total al log
        # logging.info(f'PAGES SCRAPED [{self.total_urls_pass}/{self.total_urls}] ({str(end_time - start_time)[:4]}s)')
        # if self.total_urls_pass % 5 == 0:
        # Notifiquem al grup de logs de telegram cada 5
        # tb.send_message(data['telegram'][''1001647968081''], f'PAGES SCRAPED [{self.total_urls_pass}/{self.total_urls}] ({str(end_time - start_time)[:4]}s)')

        self.total_urls_pass += 1  # Sumem 1 al total de pàgines

    # logging.info(f'TOTAL SCRAP TIME: {str(total_time)[:4]}s')  # Mostrem temps total

    # Overriding parse_start_url to get the first page
    parse_start_url = parse