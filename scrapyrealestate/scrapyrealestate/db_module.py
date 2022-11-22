import sys, datetime, pymongo
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

def create_engine_sqlite_db(db_type, db_name, db_path_name, db_file_name, logger):
    # Table Names
    REALESTATE_IDEALISTA = db_name

    # Crear engine
    # Afegim ?check_same_thread=False per evitar l'error "SQLite objects created in a thread can only be used in that same thread."
    # db_engine = create_engine(f'sqlite:///{db_path_name}/{db_file_name}?check_same_thread=False')
    db_engine = create_engine(f'sqlite:///{db_path_name}/{db_file_name}')
    #db_engine = create_engine("mysql+pymysql://realestates:1yUCVhoswC*@18.159.45.101")

    # Crear sessio
    Session = sessionmaker(bind=db_engine)
    # Session = scoped_session(sessionmaker(bind=db_engine))
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
        logger.error(f"ERROR WHILE INSERTING MONGODB")
        sys.exit()

    logger.debug(f"INSERT TO MONGODB: {data_host}")

def check_bbdd_mongodb(config_bbdd, logger):
    try:
        client = pymongo.MongoClient(f"mongodb+srv://{config_bbdd['db_user']}:{config_bbdd['db_password']}@{config_bbdd['db_host']}/?retryWrites=true&w=majority")
    except:
        logger.error(f"ERROR WHILE CONNECTING MONGODB")
        sys.exit()

    logger.debug(f"CONNECTED TO MONGODB")
    return client
