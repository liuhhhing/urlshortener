import logging
from rangeRetrieveInterface import RangeRetrieveInterface
import sqlite3


class RangeRetrieveDB(RangeRetrieveInterface):
    def __init__(self):
        self.timeout = 0
        self.db_file = None
        self.conn = None

    def get_lock(self, timeout):
        self.timeout = timeout
        self.conn = sqlite3.connect(str(self.db_file), detect_types=sqlite3.PARSE_DECLTYPES, timeout=self.timeout)
        try:
            with self.conn:
                self.conn.execute("update ranges set occupied = 1 where id = 0")
                # this is to lock the db

        except sqlite3.Error as e:
            logging.debug(e)
            return False

        return True

    def get_range(self):
        start = 0
        end = 0

        try:
            with self.conn:
                cursor = self.conn.cursor()

                cursor.execute("update ranges set occupied = 1 where id = 0") # this is to lock the db
                # table with col like
                # id, start, end, occupied
                # SELECT id, start, end from ranges where occupied = 0 order by id asc
                # update ranges set occupied = 1 where id = <last id>
                cursor.execute(
                    "SELECT id, start, end from ranges where occupied = 0 and id > 0 order by id asc"
                )
                result = cursor.fetchone()
                if result is not None:
                    id = result[0]
                    start = result[1]
                    end = result[2]
                    cursor.execute(
                        "update ranges set occupied = 1 where id = {0}".format(id)
                    )
                else:
                    return start, end, False

        except sqlite3.Error as e:
            logging.debug(e)
            return start, end, False

        return start, end, True

    def release_lock(self):
        try:
            self.conn.commit()
            self.conn.close()
        except sqlite3.Error as e:
            logging.debug(e)
            return False


        return True
