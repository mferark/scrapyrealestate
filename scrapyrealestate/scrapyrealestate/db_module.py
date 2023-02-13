import sys, datetime, pymongo

def insert_host_mongodb(db_client, db_name, db_col, data_host, logger):
    #try:
    db = db_client[db_name]  # creem la connexio amb la bbdd de mongodb
    col = db[db_col]  # creem una colecció amb el nom de la població
    col.insert_one({"id": data_host['id'],
                      "chat_id": data_host['chat_id'],
                      "group_name": data_host['group_name'],
                      "time_refresh": data_host['refresh'],
                      "min_price": data_host['min_price'],
                      "max_price": data_host['max_price'],
                      "urls": data_host['urls'],
                      "so": data_host['so'],
                      "host_name": data_host['host_name'],
                      "connections": data_host['connections'],
                      "first_connection": datetime.datetime.now(),
                      "last_connection": datetime.datetime.now()
                      })
    #except:
        #logger.error(f"ERROR WHILE INSERTING MONGODB. MAYBE YOU ARE NOT USING LAST VERSION.")
        #sys.exit()

    #logger.debug(f"INSERT TO MONGODB: {data_host}")

def query_host_mongodb(db_client, db_name, db_col, data_host, logger):
    try:
        db = db_client[db_name]  # creem la connexio amb la bbdd de mongodb
        col = db[db_col]  # creem una colecció amb el nom de la població

        myquery = {"chat_id": data_host['chat_id'], "group_name": data_host['group_name']}

        host_list = col.find(myquery)
        match_host_list = []

        for host in host_list:
            match_host_list.append(host)
        return match_host_list
    except pymongo.errors.OperationFailure:
        logger.error(f"MAYBE YOU ARE NOT USING LAST VERSION.")
        sys.exit()


def update_host_mongodb(db_client, db_name, db_col, data_host, logger):
    # try:
    db = db_client[db_name]  # creem la connexio amb la bbdd de mongodb
    col = db[db_col]  # creem una colecció amb el nom de la població

    myquery = {"chat_id": data_host['chat_id'], "group_name": data_host['group_name']}
    # El nou valor incrementa 1 a la connexio
    newvalues = {"$set": {"connections":  data_host['connections']+1}}
    col.update_one(myquery, newvalues)
    # Actualizem l'ultima data
    newvalues2 = {"$set": {"last_connection": datetime.datetime.now()}}
    col.update_one(myquery, newvalues2)


def insert_flat_mongodb(db_client, db_name, db_col, data_flat, logger):
    #try:
    db = db_client[db_name] # creem la connexio amb la bbdd de mongodb
    col = db[db_col] # creem una colecció amb el nom de la població
    col.create_index('id', unique = True) # creem index
    try:
        col.insert_one({"id": data_flat['id'],
                          "price": data_flat['price'],
                          "m2": data_flat['m2'],
                          "rooms": data_flat['rooms'],
                          "floor": data_flat['floor'],
                          "town": data_flat['town'],
                          "neighbour": data_flat['neighbour'],
                          "street": data_flat['street'],
                          "number": data_flat['number'],
                          "title": data_flat['title'],
                          "href": data_flat['href'],
                          "site": data_flat['site'],
                          "type": data_flat['type'],
                          "online": data_flat['online'],
                          "datetime": datetime.datetime.now()
                          })
    except pymongo.errors.DuplicateKeyError:
        '''logger.debug(f"ID {data_flat['id']} EXISTS ID MONGO DB. PASS.")'''
        pass
    #except:
        #logger.error(f"ERROR WHILE INSERTING MONGODB. MAYBE YOU ARE NOT USING LAST VERSION.")
     #   pass

def query_flat_mongodb(db_client, db_name, db_col, data_flat, logger):
    #try:
    db = db_client[db_name]  # creem la connexio amb la bbdd de mongodb
    col = db[db_col]  # creem una colecció amb el nom de la població

    myquery = {"site": {"$ne": f"{data_flat['site']}"},"price": data_flat['price'], "m2": data_flat['m2'], "rooms": data_flat['rooms']}

    flat_list = col.find(myquery)
    match_flat_list = []


    for flat in flat_list:
        match_flat_list.append(flat)
    return match_flat_list
    #except pymongo.errors.OperationFailure:
    #    logger.error(f"MAYBE YOU ARE NOT USING LAST VERSION.")

def check_bbdd_mongodb(config_bbdd, logger):
    try:
        client = pymongo.MongoClient(f"mongodb+srv://{config_bbdd['db_user']}:{config_bbdd['db_password']}@{config_bbdd['db_host']}/?retryWrites=true&w=majority")
    except pymongo.errors.ConfigurationError:
        logger.error("INTERNET ERROR CONNECTION")
        sys.exit()

    logger.debug(f"CONNECTED TO MONGODB")
    return client
