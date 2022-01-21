#!/usr/bin/python3
import datetime, sys, telebot, time, shutil, os.path, platform, os, logging, yaml, uuid, argparse
import scrapyrealestate.crawler_module as flats_module
import scrapyrealestate.db_module as db_module
from os import path
from art import *

__author__ = "mferark"
__author__ = "mferarg@gmail.com"
__license__ = "GPL"
__version__ = "1.0"

# Parameters
host_bbdd = 'sticker.ddns.net'
user_bbdd = 'realestate'
passwd_bbdd = '1yUCVhoswC*'
bbdd_name = f"scrapyrealestate{__version__.replace('.', '')}"

# open the yaml file and load it into data
with open('config.yaml') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

def args():
    default = False
    makeservice = False
    # Initialize parser
    parser = argparse.ArgumentParser()
    # Adding optional argument
    parser.__version__ = '1.0'
    parser.add_argument("-ms", "--makeservice", help="make service", action='store_true')

    # Read arguments from command line
    args = vars(parser.parse_args())

    if parser.parse_args().makeservice:
        logging.info(f"MAKE SERVICE OPTION ENABLED")
        makeservice = True

    return makeservice

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

def check_file_config():
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
    urls_mysql = ''
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
                urls_mysql += f'{url};'
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
        id = str(uuid.uuid4())[:8]
        chat_id = info_message.chat.id
        gtname = info_message.chat.title
        refresh = data['scrapy_time_update']
        max_price = data['flat_details']['max_price']
        host_name = platform.node()
        so = platform.platform()

        # Si ha funcionat enviem dades
        logging.info(f"TELEGRAM {info_message.chat.title} CHANNEL VERIFIED")
        try:
            info_message = tb.send_message('-1001647968081',f"<code>GTNAME      @{gtname}</code>\n"
                                                        f"<code>ID          {chat_id}</code>\n"
                                                        f"<code>REFRESH     {refresh}s</code>\n"
                                                        f"<code>MAX PRICE   {max_price}€</code>\n"
                                                        f"<code>SO          {so}</code>\n",
                                                        f"<code>HOSTNAME    {host_name}</code>\n",
                                                        f"<code>URLS        {urls_ok_count} → </code>\n"
                                                        f"<code>{urls_text}</code>\n",
                                           parse_mode='HTML'
                                           )

        # Si no s'ha enviat el missatge de telegram
        except:
            pass

        # enviem dades
        user_connection, db = db_module.create_table_bbdd_mysql(host_bbdd, user_bbdd, passwd_bbdd, bbdd_name, 'sr_connections')

        #try:
        user = user_connection(id, chat_id, gtname, refresh, max_price, urls_mysql, so, host_name, datetime.datetime.now())
        db.session.add(user)  # Adds new User record to database
        db.session.commit()
        #except:
            #logging.info('PROBLEM WHILE MAKING DATABASE CONNECTION USER. PROVABLY CHAT_ID EXISTS. PASS.')
            #pass
            #sys.exit(0)

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
    logging.info(f"SPIDER {realestate_data['db_name'].upper()} TIME: {str(end_time - start_time)[:4]}s")
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

        #try:
        scrap_realestate(data['idealista_data'], telegram_msg)  # Cridem la funcio que fa scraping a idealista
        #except:
        #    logging.error('ERROR SCRAPING idealista_data')
        #    pass

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

def make_service():
    # Comprovem que l'equip es linux
    if platform.system() != 'Linux':
        logging.error(f'TO MAKE SERVICE NEED LINUX AND YOU HAVE {platform.system()}. EXIT.')
        sys.exit()

    # Sino existeix el fitxer scraper_template.service, sortim
    logging.debug('CHECKING /scripts/scraper_template.service...')
    if not path.exists(f"./scripts/scraper_template.service"):
        logging.error("NOT FILE FOUND ./scripts/scraper_template.service")
        sys.exit()

    # Sino existeix el fitxer scraper_script_template.sh, sortim
    logging.debug('CHECKING /scripts/scraper_script_template.sh"...')
    if not path.exists("./scripts/scraper_script_template.sh"):
        logging.error("NOT FILE FOUND ./scripts/scraper_script_template.sh")
        sys.exit()

    # mirem si l'usuari te permisos
    if os.geteuid() != 0:
        logging.error("YOU NEED TO HAVE ROOT PRIVILEGIES FOR MAKE SERVICE. EXIT.")
        sys.exit()

    # agafem la ruta on esta la carpeta del programa
    try:
        route_path = os.getcwd()
    except:
        logging.error("ERROR WHILE GETTING ROUTE PATH. NEED SUDO TO CREATE SERVICE. EXIT")
        sys.exit()

    # agafem el nom de la carpeta (nom servei) ultim de la llista
    try:
        service_name = os.getcwd().split('/')[-1]
    except:
        service_name = ''
        logging.error("service_name NOT FOUND")
        sys.exit(0)

    # Si el servei existeix, preguntem si el volem sobreescriure, sino sortim
    if path.exists(f'/etc/systemd/system/{service_name}.service'):
        logging.info(f"SERVICE {service_name} EXISTS")
        # Preguntem si reescriure el servei
        ans = input(f'Dou you like to reinstall {service_name} service? ')
        # Si es afirmatiu, reescrbim el servei, sino anem a la seguent
        if ans == 'YES' or ans == 'yes' or ans == 'Y' or ans == 'y':
            # Parem i eliminem el servei
            logging.info(f"STOPPING AND DISABLING SERVICE {service_name}")
            try:
                os.system(f"sudo systemctl stop {service_name}.service")
                os.system(f"sudo systemctl disable {service_name}.service")
                os.system(f"sudo rm /etc/systemd/system/{service_name}.service")
                os.system(f"sudo systemctl daemon-reload")
                os.system(f"sudo systemctl reset-failed")
            except:
                logging.error(f"ERROR WHEN STOPPING AND DISABLING SERVICE {service_name}")
        else:
            return

    # Creem servei per al nou script
    try:
        logging.info(
            f"EDITING /etc/systemd/system/{service_name}.service...")
        # Copiar scraper_template.service
        with open('./scripts/scraper_template.service', 'r') as file:
            filedata = file.read()

        # Replace the target string
        filedata = filedata.replace('${route_path}', route_path)
        filedata = filedata.replace('${name_file}', service_name)

        # Write the file out again
        with open(f'/etc/systemd/system/{service_name}.service', 'w') as file:
            file.write(filedata)
    except:
        logging.error(f'ERROR EDITING /etc/systemd/system/{service_name}.service')

    # Creem servei per al nou script
    try:
        logging.info(
            f"EDITING {route_path}/scripts/{service_name}.sh...")
        # Copiar config.yaml
        with open('./scripts/scraper_script_template.sh', 'r') as file:
            filedata = file.read()

        # Replace the target string
        filedata = filedata.replace('${route_path}', f'{route_path}')

        # Write the file out again
        with open(f'{route_path}/scripts/{service_name}.sh', 'w') as file:
            file.write(filedata)

    except:
        logging.error(f'ERROR EDITING {route_path}/scripts/{service_name}.sh')

    # Donem permisos al fitxer
    logging.info("CHANGING PERMISIONS...")
    os.system(f"sudo chmod 744 {route_path}/scripts/{service_name}.sh")
    os.system(f"sudo chmod 644 /etc/systemd/system/{service_name}.service")

    # os.system(f"sudo systemctl enable {service_name}.service") # Perque no s'inicii al iniciar
    os.system("sudo systemctl daemon-reload")

    # Preguntem si volem que el servei s'autoinicii
    ans = input(f'Dou you enable {service_name} service? (This means it start every start)')
    if ans == 'YES' or ans == 'yes' or ans == 'Y' or ans == 'y':
        logging.info(f"ENABLING SERVICE {service_name}....")
        os.system(f"sudo systemctl enable {service_name}.service") # activem el servei

    # Preguntem si volem que el servei s'inicii
    ans = input(f'Dou you start {service_name} service?')
    if ans == 'YES' or ans == 'yes' or ans == 'Y' or ans == 'y':
        logging.info(f"STARTING SERVICE {service_name}....")
        os.system(f"sudo systemctl start {service_name}.service") # iniciem servei

    # un cop finalitzat sortim
    sys.exit(0)
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
    makeservice = args()  # Carreguem arguments.
    time.sleep(0.05)
    # si ha escollit makeservice, executem funcio
    if makeservice:
        make_service()

    #db_module.create_bbdd_mysql(host_bbdd, user_bbdd, passwd_bbdd, bbdd_name)  # crear bbdd mysql
    db_module.check_bbdd_mysql(host_bbdd, user_bbdd, passwd_bbdd, bbdd_name, __version__)   # comprovem si la bbdd de mysq existeix, sino sortim
    logging.debug('DEBUGGING ENABLE')
    time.sleep(0.05)
    info_message = check_file_config()  # Comprovem el fitxer
    time.sleep(0.05)

    # Validem el temps d'actualitzacio
    time_update = int(data['scrapy_time_update'])
    if time_update < 300:
        time_update = 300
    # Executem funcio
    scrap_allrealestates(info_message, time_update)


if __name__ == "__main__":
    init()
