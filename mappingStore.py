import sqlite3

class MappingStore:
    def __init__(self):
        self.db_connection = None
        self.logger = None
        self.store_path = None

    def get_db(self):
        self.db_connection = sqlite3.connect(str(self.store_path), detect_types=sqlite3.PARSE_DECLTYPES)
        return self.db_connection, self.db_connection.cursor()

    def close_db(self):
        if self.db_connection is not None:
            self.db_connection.close()

    def init_db(self):
        db, cursor = self.get_db()
        cursor.execute('''CREATE TABLE IF NOT EXISTS mapping (
            [id] INTEGER NOT NULL,
            [long_url] text NOT NULL,
            [short_url_hash] text NOT NULL,
            PRIMARY KEY(id, long_url, short_url_hash)
            )''')
        db.commit()
        self.close_db()

    def insert_hashed_url(self, id, long_url, hash):
        self.logger.debug("Insert Hashed URL {{{0},{1},{2}}}".format(id, long_url, hash))
        db, cursor = self.get_db()
        error = None
        try:
            cursor.execute(
                "INSERT INTO mapping (id, long_url, short_url_hash) VALUES (?,?,?)",
                (id, long_url, hash),
            )
            db.commit()
            self.close_db()
        except db.IntegrityError:
            error = "Record {{{0}, {1}, {2}}} is already existed".format(id, long_url,hash)

        return error

    def is_hashed_url_exist(self, hash):
        self.logger.debug("is_hashed_url_exist")
        db, cursor = self.get_db()

        cursor.execute(
            "SELECT COUNT(*) FROM mapping where short_url_hash = '{0}'".format(hash)
        )
        result = cursor.fetchone()
        self.logger.debug("Hashed Count For {0} is {1}".format(hash, result))
        self.close_db()
        return True if result[0] > 0 else False

    def is_long_url_exist(self, longUrl):
        self.logger.debug("is_long_url_exist")
        db, cursor = self.get_db()
        cursor.execute(
            "SELECT COUNT(*) FROm mapping where long_url = '{0}'".format(longUrl)
        )
        result = cursor.fetchone()
        self.logger.debug("LongUrl Count For {0} is {1}".format(longUrl, result))
        self.close_db()
        return True if result[0] > 0 else False

    def get_long_url_from_hash(self, hash):
        self.logger.debug("get_long_url_from_hash")
        db, cursor = self.get_db()
        cursor.execute(
            "SELECT long_url FROM mapping where short_url_hash = '{0}'".format(hash)
        )
        result = cursor.fetchone()
        self.logger.debug("Hash URL mapping For {0} is {1}".format(hash, result))
        self.close_db()
        return result[0]

    def get_hash_from_long_url(self, longUrl):
        self.logger.debug("get_hash_from_long_url")
        db, cursor = self.get_db()
        cursor.execute(
            "SELECT short_url_hash FROM mapping where long_url = '{0}'".format(longUrl)
        )
        result = cursor.fetchone()
        self.logger.debug("Long URL mapping For {0} is {1}".format(longUrl, result))
        self.close_db()
        return result[0]
    
    def get_max_count(self):
        self.logger.debug("get_max_count")
        db, cursor = self.get_db()

        cursor.execute(
            "SELECT max(id) FROM mapping"
        )
        self.close_db()

        return 0 if cursor.fetchone() is None else cursor.fetchone()[0]