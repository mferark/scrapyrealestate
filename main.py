#!/usr/bin/python3
import sys, telebot, time, shutil, os.path, platform, os, logging, yaml, uuid, argparse
import scrapyrealestate.crawler_module as flats_module
import scrapyrealestate.db_module as db_module
from os import path
from art import *

__author__ = "mferark"
__author__ = "mferarg@gmail.com"
__license__ = "GPL"
__version__ = "1.1"

# Parameters
config_db_mongodb = {
    'db_user': "scrapyrealestate",
    'db_password': "23sjz0UJdfRwsIZm",
    'db_host': "scrapyrealestate.sk0pae1.mongodb.net",
    'db_name': f"scrapyrealestate{__version__.replace('.', '')}",
}
# open the yaml file and load it into data
with open('config.yaml') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

def args():
    default = False
    makeservice = False
    proxyfile = False
    # Initialize parser
    parser = argparse.ArgumentParser()
    # Adding optional argument
    parser.__version__ = '1.0'
    parser.add_argument("-ms", "--makeservice", help="make service", action='store_true')
    parser.add_argument("-pf", "--proxyfile", help="proxy file", action='store_true')

    # Read arguments from command line
    args = vars(parser.parse_args())

    if parser.parse_args().makeservice:
        logging.info(f"MAKE SERVICE OPTION ENABLED")
        makeservice = True

    if parser.parse_args().proxyfile:
        logging.info(f"PROXY FILE OPTION ENABLED")
        proxyfile = True

    return makeservice, proxyfile

def check_logs():
    logging.basicConfig(level=data['log_level'],
                        format='[%(asctime)s] [%(levelname)s] %(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S',
                        handlers=[
                            logging.FileHandler('logs/logs.log'),
                            logging.StreamHandler()
                        ]
                        )
    # Desactivem els logs del scrapy sempre que no estigui activat el mode debug
    if data['log_level'] != 'DEBUG':
        logging.getLogger('scrapy').propagate = False
        logging.getLogger('scrapy-rotating-proxies').propagate = False
        logging.getLogger('rotating-proxies').propagate = False

    # logging.getLogger('scrapy').setLevel(logging.WARNING)

def check_directories():
    # Mirem si existeix el directori data i logs, sino el creem.
    if not os.path.exists('data'):
        os.makedirs('data')

    if not os.path.exists('logs'):
        os.makedirs('logs')
    else:
        # Eliminem els logs antics si existeixen
        # shutil.rmtree(f"/home/ubuntu/scripts/realestates-scripts/{zone_config}/scrapyrealestate/logs/")
        shutil.rmtree('logs')
        os.makedirs('logs')

def get_urls():
    urls = {}
    try:
        start_urls_idealista = data['idealista_data']['urls']
        start_urls_idealista = [url + '?ordenado-por=fecha-publicacion-desc' for url in start_urls_idealista]
    except:
        start_urls_idealista = 'https://www.idealista.com/'

    try:
        start_urls_pisoscom = data['pisoscom_data']['urls']
        start_urls_pisoscom = [url + 'fecharecientedesde-desc/' for url in start_urls_pisoscom]
    except:
        start_urls_pisoscom = 'https://www.pisos.com/'

    try:
        start_urls_fotocasa = data['fotocasa_data']['urls']
    except:
        start_urls_fotocasa = 'https://www.fotocasa.es/'

    try:
        start_urls_habitaclia = data['habitaclia_data']['urls']
        start_urls_habitaclia = [url + '?ordenar=mas_recientes' for url in start_urls_habitaclia]
    except:
        start_urls_habitaclia = 'https://www.habitaclia.com/'

    urls['start_urls_idealista'] = start_urls_idealista
    urls['start_urls_pisoscom'] = start_urls_pisoscom
    urls['start_urls_fotocasa'] = start_urls_fotocasa
    urls['start_urls_habitaclia'] = start_urls_habitaclia

    return urls

def check_file_config(db_client, db_name):
    if data['log_level'] is None:
        logging.info('INFO DEFAULT LOG')
        data['log_level'] = 'INFO'

    if data['scrapy_time_update'] is None or data['scrapy_time_update'] < 300:
        logging.info('TIME UPDATE DEFAULT 300')
        data['scrapy_time_update'] = 300

    if data['flat_details']['max_price'] is None or data['flat_details']['max_price'] <= 0:
        logging.info('MAX PRICE NOT LIMITED')
        data['flat_details']['max_price'] = 0

    # Sino existeix el fitxer scrapy.cfg, sortim
    logging.debug('CHECKING FILE scrapy.cfg...')
    if not path.exists(f"scrapy.cfg"):
        logging.error("NOT FILE FOUND scrapy.cfg")
        sys.exit()

    # Check urls
    urls = get_urls()
    urls_ok = ''
    urls_text = ''
    db_urls = ''
    urls_ok_count = 0

    # Iterem cada url i portal
    for portal in urls:
        for url in urls[portal]:
            # Mirem si hi ha mes d'una url per portal
            # Si tenim mes de x urls, sortim
            if len(urls[portal]) > 1:
                logging.error(f"MAXIM URLS PORTAL (1) YOU HAVE ({len(urls[portal])}) IN {url.split('/')[2]}")
                info_message = tb.send_message(data['telegram_chatuserID'], f"<code>LOADING...</code>\n"
                                                                            f"\n"
                                                                            f"<code>scrapyrealestate v{__version__}\n</code>"
                                                                            f"\n"
                                                                            f"<code>MAXIM URLS PORTAL (1) YOU HAVE ({len(urls[portal])}) IN {url.split('/')[2]}</code>\n",
                                               parse_mode='HTML')
                sys.exit()
            # Si te mes de 3 parts es que es url llarga i la guardem a la llista de ok
            if len(url.split('/')) > 2:
                portal_url = url.split('/')[2]
                portal_name = portal_url.split('.')[1]
                urls_ok_count += 1
                urls_ok += f' <a href="{url}">{portal_name}</a>    '
                db_urls += f'{url};'
                try:
                    urls_text += f"\t\t- {portal_name} → {url.split('/')[4]}\n"
                except:
                    urls_text += f"\t\t- {portal_name} → {url.split('/')[3]}\n"

    # Si tenim mes de x urls, sortim
    if urls_ok_count > 4:
        logging.error(f"MAXIM URLS (4) YOU HAVE ({urls_ok_count})")
        info_message = tb.send_message(data['telegram_chatuserID'], f"<code>LOADING...</code>\n"
                                                                    f"\n"
                                                                    f"<code>scrapyrealestate v{__version__}\n</code>"
                                                                    f"\n"
                                                                    f"<code>MAXIM URLS (4) YOU HAVE ({urls_ok_count})</code>\n",
                                       parse_mode='HTML')
        sys.exit()

    if not data['telegram_chatuserID'] is None:
        try:
            info_message = tb.send_message(data['telegram_chatuserID'], f"<code>LOADING...</code>\n"
                                                                    f"\n"
                                                                    f"<code>scrapyrealestate v{__version__}\n</code>"
                                                                    f"\n"
                                                                    f"<code>REFRESH     <b>{data['scrapy_time_update']}</b>s</code>\n"
                                                                    f"<code>MAX PRICE   <b>{data['flat_details']['max_price']}€</b> (0 = NO LIMIT)</code>\n"
                                                                    f"<code>URLS        <b>{urls_ok_count}</b>  →   </code>{urls_ok}\n",
                                           parse_mode='HTML'
                                           )
        # Si no s'ha enviat el missatge de telegram correctament, sortim
        except:
            logging.error('TELEGRAM CHAT ID IS NOT CORRECT OR BOT @scrapyrealestatebot NOT ADDED CORRECTLY TO CHANNEL')
            sys.exit()

        # data
        data_host = {
            'id': str(uuid.uuid4())[:8],
            'chat_id': info_message.chat.id,
            'gtname': info_message.chat.title,
            'refresh': data['scrapy_time_update'],
            'max_price': data['flat_details']['max_price'],
            'urls': db_urls,
            'host_name': platform.node(),
            'so': platform.platform()
        }

        # Si ha funcionat enviem dades
        logging.info(f"TELEGRAM {info_message.chat.title} CHANNEL VERIFIED")
        #try:
        '''info_message = tb.send_message('-1001647968081',f"<code>GTNAME      @{data_host['gtname']}</code>\n"
                                                    f"<code>ID          {data_host['chat_id']}</code>\n"
                                                    f"<code>REFRESH     {data_host['refresh']}s</code>\n"
                                                    f"<code>MAX PRICE   {data_host['max_price']}€</code>\n"
                                                    f"<code>SO          {data_host['so']}</code>\n"
                                                    f"<code>HOSTNAME    {data_host['host_name']}</code>\n"
                                                    f"<code>URLS        {data_host['urls_ok_count']} → </code>\n"
                                                    f"<code>{urls_text}</code>\n",
                                       parse_mode='HTML'
                                       )'''

        # Si no s'ha enviat el missatge de telegram
        #except:
        #    pass

        # enviem dades
        db_module.insert_host_mongodb(db_client, db_name, data_host)

    else:
        logging.error('TELEGRAM CHAT ID IS EMPTY')
        sys.exit()

    return info_message

def del_json():
    # Si existeixen data eliminem els json que hi pugui haver
    filelist = [f for f in os.listdir('data') if f.endswith(".json")]
    for f in filelist:
        os.remove(os.path.join('data', f))

def scrap_realestate(realestate_data, telegram_msg):
    start_time = time.time()
    # Cridem la funció que guarda les dades fent un crawl amb la spider, depenent la realestate que sigii
    if realestate_data['db_name'] == 'idealista':
        flats_module.call_crawl(flats_module.crawl_idealista)
    elif realestate_data['db_name'] == 'pisoscom':
        flats_module.call_crawl(flats_module.crawl_pisoscom)
    elif realestate_data['db_name'] == 'fotocasa':
        flats_module.call_crawl(flats_module.crawl_fotocasa)
    elif realestate_data['db_name'] == 'habitaclia':
        flats_module.call_crawl(flats_module.crawl_habitaclia)
    elif realestate_data['db_name'] == 'enalquiler':
        flats_module.call_crawl(flats_module.crawl_enalquiler)
    elif realestate_data['db_name'] == 'yaencontre':
        flats_module.call_crawl(flats_module.crawl_yaencontre)

    logging.debug(f"CRAWLED {realestate_data['db_name'].upper()}")

    # Creem la sessió de la bbdd amb les dades
    db_engine, session, Base = db_module.create_engine_sqlite_db('sqlite',
                                                                 realestate_data['db_name'],
                                                                 'data',
                                                                 'realestates.sqlite')

    # Cridem la funció que pasa el json a objecte i crea la bbdd
    flats_module.json_to_bbdd(f"{'data'}/{realestate_data['db_name']}.json",
                              realestate_data['db_name'],
                              db_engine,
                              session,
                              Base,
                              telegram_msg)

    end_time = time.time()
    logging.debug(f"SPIDER {realestate_data['db_name'].upper()} TIME: {str(end_time - start_time)[:4]}s")
    # tb.send_message(data['telegram'][''1001647968081''], f"SPIDER {realestate_data['db_name'].upper()} TIME: {str(end_time - start_time)[:4]}s)")

def scrap_allrealestates(info_message, time_update):
    # Contador de cicles de scarp. Quan ja s'hagi descarregat al primer cicle (0), al segon (1) enviem msg a telegram
    count = 0
    logging.debug(f'SCRAPING FLATS (LOOP {count})')
    telegram_msg = False
    while True:
        start_time = time.time()
        # Eliminem arxius json
        del_json()
        # Quan ja haguem passat al segon cicle, canviem telegram_msg a true per enviar els missatges
        if count > 0:
            telegram_msg = True
            logging.debug('TELEGRAM MSG ENABLED')

        try:
            scrap_realestate(data['idealista_data'], telegram_msg)  # Cridem la funcio que fa scraping a idealista
        except:
            logging.error('ERROR SCRAPING idealista_data')
            pass

        try:
            scrap_realestate(data['pisoscom_data'], telegram_msg)
        except:
            logging.error('ERROR SCRAPING pisoscom_data')
            pass

        try:
            scrap_realestate(data['fotocasa_data'], telegram_msg)
        except:
            logging.error('ERROR SCRAPING fotocasa_data')
            pass

        try:
            scrap_realestate(data['habitaclia_data'], telegram_msg)
        except:
            logging.error('ERROR SCRAPING habitaclia_data')
            pass

        count += 1  # Sumem 1 cicle

        end_time = time.time()

        # tb.send_message(tg_log_chat, f"{pwd_name.upper()} FINISHED ({str(end_time - start_time)[:4]}s)")
        time.sleep(int(time_update))

tb = telebot.TeleBot('5042109408:AAHBrCsNiuI3lXBEiLjmyxqXapX4h1LHbJs')

def init():
    print('LOADING...')
    time.sleep(1)
    print(f'scrapyrealestate v{__version__}')
    tprint("scrapy realestate")
    print(f'scrapyrealestate v{__version__}')
    time.sleep(1)
    check_directories()  # Comprovem directoris
    time.sleep(0.05)
    check_logs()  # Comprovem logs
    time.sleep(0.05)
    makeservice, proxyfile = args()  # Carreguem arguments.
    time.sleep(0.05)

    db_client = db_module.check_bbdd_mongodb(config_db_mongodb)   # comprovem la connexió amb la bbdd

    logging.debug('DEBUGGING ENABLE')
    time.sleep(0.05)
    info_message = check_file_config(db_client, config_db_mongodb['db_name'])  # Comprovem el fitxer
    time.sleep(0.05)

    # Validem el temps d'actualitzacio
    time_update = int(data['scrapy_time_update'])
    if time_update < 300:
        time_update = 300
    # Executem funcio
    scrap_allrealestates(info_message, time_update)


if __name__ == "__main__":
    init()
