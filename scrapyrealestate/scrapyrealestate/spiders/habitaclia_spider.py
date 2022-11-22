import scrapy, os, logging, time
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
from bs4 import BeautifulSoup
#from items import ScrapyrealestateItem # ERROR (es confundeix amb items al 192.168.1.100)
from scrapyrealestate.items import ScrapyrealestateItem

class HabitacliaSpider(CrawlSpider):
    name = "habitaclia"
    allowed_domains = ["habitaclia.com"]
    total_time = 0

    def start_requests(self):
        # start_urls = [url + '?ordenado-por=fecha-publicacion-desc' for url in self.start_urls]
        yield scrapy.Request(f'{self.start_urls}')

    total_urls_pass = 1  # Inicialitzem contador

    custom_settings = {
        # 'DOWNLOAD_DELAY': 2,
        # 'ITEM_PIPELINES': {
        #    'freedom.pipelines.IndexPipeline': 300
        # },
        #'FEED_FORMAT': 'json',
        #'FEED_URI': 'flats_habitaclia.json',
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

    '''rules = (
        # Filter all the flats paginated by the website following the pattern indicated
        Rule(LinkExtractor(restrict_xpaths=("//li[@class='next']")),
             callback='parse',  # cridem la funcio parse de nou
             follow=True),  # Seguim l'enllaç
    )'''

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
        #print(flats)
        #print(len(flats))

        # div --> class="pagination" --> ul --> li --> class="next"
        try:
            next_page = soup.find("div", {"class": "pagination"}).find("a", {"class": "icon-arrow-right-after"})['href']
        except:
            next_page = ""
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

            id = ''.join(char for char in rooms if char.isdigit()) + ''.join(char for char in price if char.isdigit()) + ''.join(char for char in m2 if char.isdigit())

            # Add items
            items['id'] = id
            items['title'] = title
            items['price'] = price.replace(' ', '')+'/mes'
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
        #logger.info(f'PAGES SCRAPED TIME ({str(end_time - start_time)[:4]}s)')

        self.total_urls_pass += 1  # Sumem 1 al total de pàgines

    # Overriding parse_start_url to get the first page
    parse_start_url = parse
