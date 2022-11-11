import logging, sys, datetime, pymongo
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Float, DateTime

def create_engine_sqlite_db(db_type, db_name, db_path_name, db_file_name):
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
    logging.debug(f'CREATE ENGINE {db_name.upper()} BBDD ON {db_path_name.upper()}/{db_file_name.upper()}')
    return db_engine, session, Base

def create_table_bbdd_flat(tablename, Base):
    '''
    Funció que crea un model de taula igual. Funciona amb sqlamchemy
    i es crea l'objecte i la taula alhora.
    :param tablename:
    :return:
    '''

    class Flat(Base):
        __tablename__ = tablename

        id = Column(Integer, primary_key=True)
        title = Column(String)
        price = Column(Integer)
        rooms = Column(Integer)
        m2 = Column(Integer)
        floor = Column(String)
        href = Column(String)
        datetime = Column(DateTime)

        def __init__(self, id, title, price, rooms, m2, floor, href, datetime):
            # self.set_is_new(is_new)
            # TODO: self.__id NO!! why?
            self.id = id
            self.title = title
            self.price = price
            self.rooms = rooms
            self.m2 = m2
            self.floor = floor
            self.href = href
            self.datetime = datetime

        def __repr__(self):
            return f'{tablename}({self.id}, {self.title}, {self.price}, {self.rooms}, {self.m2}, {self.floor}, {self.href}, {self.datetime})'

        def __str__(self):
            return self.title

    return Flat

def insert_host_mongodb(db_client, db_name, data_host):
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
        logging.error(f"ERROR WHILE INSERTING MONGODB")
        sys.exit()

    logging.debug(f"INSERT TO MONGODB: {data_host}")

def check_bbdd_mongodb(config_bbdd):
    try:
        client = pymongo.MongoClient(f"mongodb+srv://{config_bbdd['db_user']}:{config_bbdd['db_password']}@{config_bbdd['db_host']}/?retryWrites=true&w=majority")
    except:
        logging.error(f"ERROR WHILE CONNECTING MONGODB")
        sys.exit()

    logging.debug(f"CONNECTED TO MONGODB")
    return client
