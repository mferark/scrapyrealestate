#!/usr/bin/python3
import subprocess
import sys, telebot, time, shutil, os.path, platform, os, logging, uuid
import scrapyrealestate.crawler_module as crawler_module
import scrapyrealestate.db_module as db_module
from os import path
from art import *
import urllib.request, json

__author__ = "mferark"
__author__ = "mferarg@gmail.com"
__license__ = "GPL"
__version__ = "2.0.2"

# Parameters
config_db_mongodb = {
    'db_user': "scrapyrealestate",
    'db_password': "23sjz0UJdfRwsIZm",
    'db_host': "scrapyrealestate.sk0pae1.mongodb.net",
    'db_name': f"scrapyrealestate{__version__.replace('.', '')}",
}
data = {}

def init_logs():
    global logger
    try:
        log_level = data['log_level'].upper()
    except:
        log_level = 'INFO'

    if log_level == 'DEBUG':
        log_level = logging.DEBUG
    elif log_level == 'INFO':
        log_level = logging.INFO
    elif log_level == 'WARNING':
        log_level = logging.WARNING
    elif log_level == 'ERROR':
        log_level = logging.ERROR
    elif log_level == 'CRITICAL':
        log_level = logging.CRITICAL

    # create logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(log_level)

    # create formatter
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s',
                                  "%Y-%m-%d %H:%M:%S")
    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    return logger

def del_json(dir):
    # Si existeixen data eliminem els json que hi pugui haver
    filelist = [f for f in os.listdir('data') if f.endswith(".json")]
    for f in filelist:
        os.remove(os.path.join(dir, f))

def del_json_flats(dir):
    # Si existeixen data eliminem els json que hi pugui haver
    filelist = [f for f in os.listdir('data') if f.endswith(".json")]
    for f in filelist:
        if f != 'config.json':
            os.remove(os.path.join(dir, f))

def get_config():
    # Sino existeix el fitxer de configuració agafem les dades de la web
    if not os.path.isfile('./data/config.json'):
        # Mirem si existeix el directori data i logs, sinó el creem.
        if not os.path.exists('data'):
            os.makedirs('data')
        pid = init_app_flask()  # iniciem  flask a localhost:8080
        get_config_flask(pid)  # agafem les dades de la configuració
    else:
        with open('./data/config.json') as json_file:
            global data
            data = json.load(json_file)

def check_config(db_client, db_name):
    # creem l'objecte per enviar tg
    tb = telebot.TeleBot('5042109408:AAHBrCsNiuI3lXBEiLjmyxqXapX4h1LHbJs')

    # Sino existeix el fitxer scrapy.cfg, sortim
    if not path.exists("scrapy.cfg"):
        logger.error("NOT FILE FOUND scrapy.cfg")
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
                logger.error(f"MAXIM URLS PORTAL (1) YOU HAVE ({len(urls[portal])}) IN {url.split('/')[2]}")
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
        logger.error(f"MAXIM URLS (4) YOU HAVE ({urls_ok_count})")
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
                                                                    f"<code>REFRESH     <b>{data['time_update']}</b>s</code>\n"
                                                                    f"<code>MAX PRICE   <b>{data['max_price']}€</b> (0 = NO LIMIT)</code>\n"
                                                                    f"<code>URLS        <b>{urls_ok_count}</b>  →   </code>{urls_ok}\n",
                                           parse_mode='HTML'
                                           )
        # Si no s'ha enviat el missatge de telegram correctament, sortim
        except:
            logger.error('TELEGRAM CHAT ID IS NOT CORRECT OR BOT @scrapyrealestatebot NOT ADDED CORRECTLY TO CHANNEL')
            sys.exit()

        # data
        data_host = {
            'id': str(uuid.uuid4())[:8],
            'chat_id': info_message.chat.id,
            'gtname': info_message.chat.title,
            'refresh': data['time_update'],
            'max_price': data['max_price'],
            'urls': db_urls,
            'host_name': platform.node(),
            'so': platform.platform()
        }

        # Si ha funcionat enviem dades
        logger.info(f"TELEGRAM {info_message.chat.title} CHANNEL VERIFIED")

        # enviem dades
        db_module.insert_host_mongodb(db_client, db_name, data_host, logger)

    else:
        logger.error('TELEGRAM CHAT ID IS EMPTY')
        sys.exit()

    return info_message

def checks():
    # Mirem el time update
    if int(data['time_update']) < 300:
        logger.error("TIME UPDATE < 300")
        sys.exit()
    time.sleep(0.05)
    db_client = db_module.check_bbdd_mongodb(config_db_mongodb, logger)  # comprovem la connexió amb la bbdd
    info_message = check_config(db_client, config_db_mongodb['db_name'])  # Comprovem parametres configuració
    return db_client, info_message

def check_url(url):
    try:
        url_code = urllib.request.urlopen(url).getcode()
    except:
        url_code = 404

    return url_code

def init_app_flask():
    # comprovem si el servidor està engengat.
    # si no trobem cap pàgina a localhost:8080 executem el servidor
    localhost_code = check_url("http://localhost:8080")
    if localhost_code != 200:
        try:
            #os.system('python ./scrapyrealestate/flask_server.py &')
            proces_server = subprocess.Popen('python ./scrapyrealestate/flask_server.py &', shell=True)
        except:
            #os.system('python3 ./scrapyrealestate/flask_server.py &')
            proces_server = subprocess.Popen('python3 ./scrapyrealestate/flask_server.py &', shell=True)
        #proces_server.wait()
        pid = proces_server.pid
        real_pid = pid + 1 # +1 perque el pid real sempre es un numero mes
        #proces_server.terminate()
    else:
        real_pid = os.popen('pgrep python ./scrapyrealestate/flask_server.py').read()

    return real_pid

def get_config_flask(pid):
    while True:
        try:
            # si trobem info a localhost:8080/data guardem les dades i sortim del bucle
            with open('./data/config.json') as json_file:
                global data
                data = json.load(json_file)
                os.system(f'kill {pid}')  # matem el proces del servidor web
                break
        except:
            pass
        time.sleep(1)

def get_urls():
    urls = {}

    # sino hi ha urls, sortim
    if data['url_idealista'] == '' and data['url_pisoscom'] == '' and data['url_fotocasa'] == '' and data['url_habitaclia'] == '':
        logger.warning("NO URLS ENTERED (MINIUM 1 URL)")
        sys.exit()

    try:
        start_urls_idealista = [data['url_idealista']]
        start_urls_idealista = [url + '?ordenado-por=fecha-publicacion-desc' for url in start_urls_idealista]
    except:
        start_urls_idealista = ['https://www.idealista.com/']

    try:
        start_urls_pisoscom = [data['url_pisoscom']]
        start_urls_pisoscom = [url + 'fecharecientedesde-desc/' for url in start_urls_pisoscom]
    except:
        start_urls_pisoscom = ['https://www.pisos.com/']

    try:
        start_urls_fotocasa = [data['url_fotocasa']]
    except:
        start_urls_fotocasa = ['https://www.fotocasa.es/']

    try:
        start_urls_habitaclia = [data['url_habitaclia']]
        start_urls_habitaclia = [url + '?ordenar=mas_recientes' for url in start_urls_habitaclia]
    except:
        start_urls_habitaclia = ['https://www.habitaclia.com/']

    urls['start_urls_idealista'] = start_urls_idealista
    urls['start_urls_pisoscom'] = start_urls_pisoscom
    urls['start_urls_fotocasa'] = start_urls_fotocasa
    urls['start_urls_habitaclia'] = start_urls_habitaclia

    return urls

def scrap_realestate(db_client, db_name, telegram_msg):
    start_time = time.time()

    # Si el nom del projecte te alguna "-" les canviem ja que dona problemes amb el sqlite
    scrapy_rs_name = data['scrapy_rs_name'].replace("-", "_")
    scrapy_log = data['log_level_scrapy'].upper()
    proxy_idealista = data['proxy_idealista']

    urls = []
    urls.append(data['url_idealista'])
    urls.append(data['url_pisoscom'])
    urls.append(data['url_fotocasa'])
    urls.append(data['url_habitaclia'])

    # iterem les urls que hi ha i fem scrape
    for url in urls:
        # Mirem quin portal es ['idealista', 'pisoscom', 'fotocasa', 'habitaclia', 'yaencontre', 'enalquiler' ]
        # try:
        if url == '':
            continue
        portal_url = url.split('/')[2]
        portal_name = portal_url.split('.')[1]
        try:
            portal_name_url = portal_url.split('.')[1] + '.' + portal_url.split('.')[2]
        except:
            portal_name = portal_url
            portal_name_url = ''

        # Validem que les spiders hi son
        command = "scrapy list"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait()
        if process.returncode != 0:
            logger.error("SPIDERS NOT DETECTED")
            sys.exit()

        # Fem crawl amb la spider depenen del portal amb la url
        logger.debug(f"SCRAPING PORTAL {portal_name_url} FROM {scrapy_rs_name}...")
        if portal_name_url == 'idealista.com':
            url_last_flats = url + '?ordenado-por=fecha-publicacion-desc'
            # Mirem si està o no activat el proxy i fem crawl cridant la spider per terminal
            if proxy_idealista == 'on':
                logger.debug('IDEALISTA PROXY ACTIVATED')
                os.system(f"scrapy crawl -L {scrapy_log} idealista_proxy -o ./data/{scrapy_rs_name}.json -a start_urls={url_last_flats}")
            else:
                os.system(f"scrapy crawl -L {scrapy_log} idealista -o ./data/{scrapy_rs_name}.json -a start_urls={url_last_flats}")
        elif portal_name_url == 'pisos.com':
            url_last_flats = url + '/fecharecientedesde-desc/'
            os.system(f"scrapy crawl -L {scrapy_log} pisoscom -o ./data/{scrapy_rs_name}.json -a start_urls={url_last_flats}")
        elif portal_name_url == 'fotocasa.es':
            os.system(f"scrapy crawl -L {scrapy_log} fotocasa -o ./data/{scrapy_rs_name}.json -a start_urls={url}")
        elif portal_name_url == 'habitaclia.com':
            # Fem crawl cridant la spider per terminal
            url_last_flats = url + '?ordenar=mas_recientes'
            os.system(f"scrapy crawl -L {scrapy_log} habitaclia -o ./data/{scrapy_rs_name}.json -a start_urls={url_last_flats}")

        logger.debug(f"CRAWLED {portal_name.upper()}")

    # Arreglar JSON - S'han d'unir les diferents parts - o treure les parts que els uneixen (][)
    #os.chdir("..") # tornem al directori pare
    logger.debug(f"EDITING ./data/{scrapy_rs_name}.json...")
    with open(f'./data/{scrapy_rs_name}.json', 'r') as file:
        filedata = file.read()
    # Replace the target string
    filedata = filedata.replace('\n][', ',')
    # Write the file out again
    with open(f'./data/{scrapy_rs_name}.json', 'w') as file:
        file.write(filedata)

    # Creem la sessió de la bbdd amb les dades
    db_engine, session, Base = db_module.create_engine_sqlite_db(scrapy_rs_name,
                                                                 'data',
                                                                 'realestates.sqlite',
                                                                 logger)

    # Cridem la funció que pasa el json a objecte i crea la bbdd
    crawler_module.json_to_bbdd(f"./data/{scrapy_rs_name}.json",
                                scrapy_rs_name,
                                db_engine,
                                session,
                                Base,
                                data['max_price'],
                                data['telegram_chatuserID'],
                                db_client,
                                db_name,
                                telegram_msg,
                                logger)

def init():
    print('LOADING...')
    time.sleep(1)
    print(f'scrapyrealestate v{__version__}')
    tprint("scrapyrealestate")
    print(f'scrapyrealestate v{__version__}')
    time.sleep(0.05)
    logger = init_logs()  # iniciem els logs
    time.sleep(0.05)
    get_config()    # Agafem la configuració
    time.sleep(0.05)
    db_client, info_message = checks()    # Comprovacions
    time.sleep(0.05)
    count = 0
    telegram_msg = False
    scrapy_rs_name = data['scrapy_rs_name'].replace("-", "_")
    send_first = data['send_first']

    while True:
        try:    os.remove(f"./data/{scrapy_rs_name}.json")  # Eliminem l'arxiu json
        except:
            pass

        # Si senf_first està activat o bé hem passat al segon cicle, canviem telegram_msg a true per enviar els missatges
        if send_first == 'True' or count > 0:
            telegram_msg = True
            logger.debug('TELEGRAM MSG ENABLED')

        try:
        # Cridem la funció d'scraping
            scrap_realestate(db_client, config_db_mongodb['db_name'], telegram_msg)
        except:
            pass

        count += 1  # Sumem 1 cicle
        logger.debug(f"SLEEPING {data['time_update']} SECONDS")
        time.sleep(int(data['time_update']))

if __name__ == "__main__":
    init()
