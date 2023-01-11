import sys, datetime, pymongo
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

def create_engine_sqlite_db(db_name, db_path_name, db_file_name, logger):
    # Crear engine
    db_engine = create_engine(f'sqlite:///{db_path_name}/{db_file_name}')

    # Crear sessio
    Session = sessionmaker(bind=db_engine)
    session = Session()

    # Creem classe base (Esta clase será de la que hereden todos los modelos y tiene la capacidad de realizar el mapeo correspondiente a partir de la metainformación)
    Base = declarative_base()
    logger.debug(f'CREATE ENGINE {db_name.upper()} BBDD ON {db_path_name.upper()}/{db_file_name.upper()}')
    return db_engine, session, Base

def insert_host_mongodb(db_client, db_name, data_host, logger):
    try:
        db = db_client[db_name]
        db.sr_connections.insert_one({"id": data_host['id'],
                          "chat_id": data_host['chat_id'],
                          "group_name": data_host['chat_id'],
                          "time_refresh": data_host['refresh'],
                          "max_price": data_host['max_price'],
                          "urls": data_host['urls'],
                          "so": data_host['so'],
                          "host_name": data_host['host_name'],
                          "datetime": datetime.datetime.now()
                          })
    except:
        logger.error(f"ERROR WHILE INSERTING MONGODB. MAYBE YOU ARE NOT USING LAST VERSION.")
        sys.exit()

    logger.debug(f"INSERT TO MONGODB: {data_host}")

def insert_flat_mongodb(db_client, db_name, data_flat, logger):
    try:
        db = db_client[db_name]
        db.sr_flats.insert_one({"id": data_flat['id'],
                          "title": data_flat['title'],
                          "price": data_flat['price'],
                          "rooms": data_flat['rooms'],
                          "m2": data_flat['m2'],
                          "floor": data_flat['floor'],
                          "href": data_flat['href'],
                          "datetime": datetime.datetime.now()
                          })
    except:
        #logger.error(f"ERROR WHILE INSERTING MONGODB. MAYBE YOU ARE NOT USING LAST VERSION.")
        pass

def check_bbdd_mongodb(config_bbdd, logger):
    try:
        client = pymongo.MongoClient(f"mongodb+srv://{config_bbdd['db_user']}:{config_bbdd['db_password']}@{config_bbdd['db_host']}/?retryWrites=true&w=majority")
    except:
        logger.error(f"ERROR WHILE CONNECTING MONGODB. MAYBE YOU ARE NOT USING LAST VERSION.")
        sys.exit()

    logger.debug(f"CONNECTED TO MONGODB")
    return client
