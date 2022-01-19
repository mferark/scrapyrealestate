import datetime, logging
import scrapyrealestate.db_module as db_engine_module
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapyrealestate.spiders.spiders_realestates import *
from multiprocessing.context import Process
from main import data, tb  # Importem la data del yaml

def crawl_realestate(realestate):
    '''
    Amb aquesta funció podem executar varies spiders en diferents processos
    :return:
    '''
    # logging.DEBUG(f'CRAWLING {realestate}') # (!!si descomento es para despres de fer scraping a la primera realestate)
    # Importem settings de la spider idealista
    settings = get_project_settings()
    # Creem la spider amb els settings i l'executem
    crawler = CrawlerProcess(settings)
    crawler.crawl(realestate)
    crawler.start()  # the script swill block here until the crawling is finished
    
def crawl_idealista():
    '''
    Amb aquesta funció podem executar varies spiders en diferents processos
    :return:
    '''
    # Importem settings de la spider idealista
    settings = get_project_settings()
    # Creem la spider amb els settings i l'executem
    crawler = CrawlerProcess(settings)
    crawler.crawl(IdealistaSpider)
    crawler.start()  # the script swill block here until the crawling is finished


def crawl_pisoscom():
    '''
    Amb aquesta funció podem executar varies spiders en diferents processos
    :return:
    '''
    # Importem settings de la spider idealista
    settings = get_project_settings()
    # Creem la spider amb els settings i l'executem
    crawler = CrawlerProcess(settings)
    crawler.crawl(PisoscomSpider)
    crawler.start()  # the script swill block here until the crawling is finished


def crawl_fotocasa():
    '''
    Amb aquesta funció podem executar varies spiders en diferents processos
    :return:
    '''
    # Importem settings de la spider idealista
    settings = get_project_settings()
    # Creem la spider amb els settings i l'executem
    crawler = CrawlerProcess(settings)
    #crawler.crawl(FotocasaSpider)
    crawler.crawl(FotocasaSpider)
    crawler.start()  # the script swill block here until the crawling is finished


def crawl_habitaclia():
    '''
    Amb aquesta funció podem executar varies spiders en diferents processos
    :return:
    '''
    # Importem settings de la spider idealista
    settings = get_project_settings()
    # Creem la spider amb els settings i l'executem
    crawler = CrawlerProcess(settings)
    crawler.crawl(HabitacliaSpider)
    crawler.start()  # the script swill block here until the crawling is finished


'''def crawl_enalquiler():
    # Importem settings de la spider idealista
    settings = get_project_settings()
    # Creem la spider amb els settings i l'executem
    crawler = CrawlerProcess(settings)
    crawler.crawl(EnalquilerSpider)
    crawler.start()  # the script swill block here until the crawling is finished
'''

'''def crawl_yaencontre():
    # Importem settings de la spider idealista
    settings = get_project_settings()
    # Creem la spider amb els settings i l'executem
    crawler = CrawlerProcess(settings)
    crawler.crawl(YaencontreSpider)
    crawler.start()'''


def call_crawl(crawl):
    '''
    Funció que crea un nou procés d'una spider
    :param crawl:
    :return:
    '''
    # Generem un nou proces per evitar conflictes
    process = Process(target=crawl)  # Executem un procès nou de spider
    process.start()
    process.join()

def json_to_bbdd(json_file_name, db_name, db_engine, session, Base, telegram_msg):
    '''
    Funció que llegeix un json dels habitatges amb les seves propietats.
    Compara si n'hi ha cap que no estigui a la bbdd i notifica amb missatge.
    :param json:
    :return:
    '''
    new_flats = 0

    # Obrir json
    # with open('flats_idealista.json') as json_file:
    json_file = open(json_file_name)

    # Encapsulem per si dona error
    try:
        data_json = json.load(json_file)
    except:
        data_json = ""

    # Check if JSON is empty
    if len(data_json) == 0:
        logging.warning('NO DATA IN JSON')
    json_file.close()

    # Creem class objecte taula
    Flat = db_engine_module.create_table_bbdd_flat(db_name, Base)

    # Creem, sino existeixen, les taula a la bbdd
    Base.metadata.create_all(db_engine)
    logging.debug(f"NEW TABLE BBDD {db_name.upper()} CREATED (IF NOT EXISTS)")

    # Guardem tots els idds de la bbdd (per comparar ids)
    ids_bbdd = []
    connection = db_engine.connect()

    result = connection.execute(f'select id from {db_name}')
    for row in result:
        ids_bbdd.append(row['id'])

    # Iterem cada pis del diccionar i tractem les dades
    for flat in data_json:
        flat_id = int(flat['id'])  # Convertim a int
        title = flat["title"].replace("\'", "")
        # Agafem nomes els digits de price, rooms i m2
        try:
            price = int(''.join(char for char in flat['price'] if char.isdigit()))
        except:
            try: price = flat['price']
            except: price = 0
        try:
            rooms = int(''.join(char for char in flat['rooms'] if char.isdigit()))
        except:
            try: rooms = flat['rooms']
            except: rooms = 0
        try:
            m2 = int(''.join(char for char in flat['m2'] if char.isdigit())[:-1])
            m2_tg = f'{m2}m²'
        except:
            try:
                m2 = flat['m2']
                m2_tg = f'{m2}m²'
            except:
                m2 = 0
                m2_tg = ''

        floor = flat['floor']
        href = flat['href']

        # Comprovem si aquest id (nou) esta a la llista de ids de la bbdd
        bbdd_exists = False
        for id_bbdd in ids_bbdd:
            # Si existeix, canviem el signe de la variable
            if id_bbdd == flat_id:
                bbdd_exists = True

        # Si la id no està a la bbdd (bbdd_exists = False), creem objecte (tambe a la bbdd) i avisem per telegram
        if not bbdd_exists:
            currentDateTime = datetime.datetime.now()
            new_flats += 1 # Sumem al contador de nous flats
            # Creem objecte flat (tambe a la bbdd)
            flat = Flat(flat_id, title, price, rooms, m2, floor, href, currentDateTime)
            session.add(flat)
            session.commit()  # Fem el commit a la BBDD
            logging.info(f'ADDING FLAT {flat_id} TO BBDD {db_name.upper()}')

            # Fem modul de 5 dels flats. Cada modul de 5 esperem 10s a veure si no peta el puto telegram
            if new_flats % 20 == 0:
                time.sleep(200)

            if telegram_msg:
                if price <= data['flat_details']['max_price'] or data['flat_details']['max_price'] == 0:  # Enviar missatge a telegram si es True i el preu es <= 1000
                    try:
                        logging.info(f'SENDING FLAT {flat_id} TO TELEGRAM GROUP')
                        # Enviem missatge tg del preu, m2, mitjana i href
                        mitja_price_m2 = '%.2f' % (price /float(m2))
                        tb.send_message(data['telegram_chatuserID'], f"{price}€ [{m2_tg}] → {mitja_price_m2}€/m²\n{href}")
                    except:
                        logging.error(f'SENDING FLAT TELEGRAM ERROR')

    logging.info(f"SPIDER {db_name.upper()} FINISHED - [NEW: {new_flats}] [TOTAL: {len(data_json)}]")