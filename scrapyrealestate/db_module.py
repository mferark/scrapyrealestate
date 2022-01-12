import logging, sys, pymysql.cursors
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Float, DateTime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

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

def create_bbdd_mysql(host_bbdd, user_bbdd, passwd_bbdd, bbdd_name):
    try:
        connection = pymysql.connect(host=host_bbdd,
                                     user=user_bbdd,
                                     port=3306,
                                     password=passwd_bbdd)
        logging.info(f"CONNECTED TO MYSQL DATABASE")
    except:
        logging.error(f"ERROR WHILE CONNECTING MYSQL DATABASE")
        sys.exit()

    try:
        with connection.cursor() as cursor:
            cursor.execute(f'CREATE DATABASE {bbdd_name}')
            logging.info(f'MAKING DATABASE {bbdd_name}')

        cursor.close()
        connection.close()
    except:
        # connection.close()
        logging.info(f'MYSQL DATABASE {bbdd_name} EXISTS')

def create_table_bbdd_mysql(host_bbdd, user_bbdd, passwd_bbdd, bbdd_name, table_name):
    app = Flask(__name__)
    #app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://realestates:1yUCVhoswC*@18.159.45.101/barcelona'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{user_bbdd}:{passwd_bbdd}@{host_bbdd}/{bbdd_name}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db = SQLAlchemy(app)
    ma = Marshmallow(app)

    class User_connection(db.Model):
        __tablename__ = table_name
        id = db.Column(db.String(15), primary_key=True)
        chat_id = db.Column(db.String(15))
        group_name = db.Column(db.String(30))
        time_refresh = db.Column(db.Integer)
        max_price = db.Column(db.Integer)
        urls = db.Column(db.String(500))
        so = db.Column(db.String(80))
        host_name = db.Column(db.String(80))
        datetime = db.Column(db.DateTime)

        def __init__(self, id, chat_id, group_name, time_refresh, max_price, urls, so, host_name, datetime):
            self.group_name = group_name
            self.id = id
            self.chat_id = chat_id
            self.group_name = group_name
            self.time_refresh = time_refresh
            self.max_price = max_price
            self.urls = urls
            self.so = so
            self.host_name = host_name
            self.datetime = datetime

    db.create_all()

    return User_connection, db

def check_bbdd_mysql(host_bbdd, user_bbdd, passwd_bbdd, bbdd_name, __version__):
    try:
        connection = pymysql.connect(host=host_bbdd,
                                     user=user_bbdd,
                                     port=3306,
                                     password=passwd_bbdd)
        logging.info(f"CONNECTED TO MYSQL DATABASE")
    except:
        logging.error(f"ERROR WHILE CONNECTING MYSQL DATABASE")
        sys.exit()

    with connection.cursor() as cursor:
        # SHOW TABLES LIKE "customer_data";
        nmatch = cursor.execute(f"SHOW DATABASES LIKE '{bbdd_name}'")

        if nmatch != 1:
            logging.error(f"DATABASE {bbdd_name} NOT EXISTS. PROBABLY THIS __version__ ({__version__}) IS NOT SUPPORTED.")
            sys.exit()

    logging.debug(f'MYSQL DATABASE {bbdd_name} EXISTS')
