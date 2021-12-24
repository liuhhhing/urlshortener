import logging
import threading

from rangeRetrieveInterface import RangeRetrieveInterface
import sqlite3
import time


class RangeRetrieveDB(RangeRetrieveInterface):
    def __init__(self):
        self.timeout = 0
        self.db_file = None
        self.conn = None

    def set_db_file(self, db_file):
        self.db_file = db_file

    def get_lock(self, timeout):
        logging.debug("Start to get lock")
        success = True
        self.timeout = timeout

        # this is to lock the db
        count = self.timeout
        while True:
            try:
                logging.debug("connect to {0}".format(str(self.db_file)))
                self.conn = sqlite3.connect(str(self.db_file), detect_types=sqlite3.PARSE_DECLTYPES, timeout=10)
                cursor = self.conn.cursor()
                cursor.execute("update ranges set occupied = 1 where id = 0 and occupied = 0")
                if cursor.rowcount == 1:
                    logging.debug("Success to acquire lock")
                    self.conn.commit()
                    success = True
                else:
                    success = False

            except sqlite3.Error as e:
                logging.debug("Exception on acquire: {0}".format(str(e)))
                success = False

            self.conn.close()
            if success:
                break
            else:
                time.sleep(1)
                logging.debug("retrying acquire lock: {0}/{1}".format(count, timeout))
                count = count - 1
                if count < 0:
                    logging.debug("timeout reached and still cannot acquire the lock")
                    break

        logging.debug("Acquire lock done {0}".format(success))
        return success

    def get_range(self):
        logging.debug("Start to get range")
        start = 0
        end = 0
        success = True
        all_occupied = False

        while True:
            try:
                self.conn = sqlite3.connect(str(self.db_file), detect_types=sqlite3.PARSE_DECLTYPES)
                with self.conn:
                    cursor = self.conn.cursor()

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
                        self.conn.commit()
                        logging.debug("Success to get range {0}, {1}".format(start, end))
                        success = True
                    else:
                        logging.debug("No Range available")
                        all_occupied = True
                        success = False

            except sqlite3.Error as e:
                logging.debug("Exception on get range: {0}".format(str(e)))
                success = False

            if success:
                break
            if all_occupied:
                break

        self.conn.close()
        return start, end, success

    def release_lock(self):
        logging.debug("Start to release lock")
        success = True
        while True:
            try:
                self.conn = sqlite3.connect(str(self.db_file), detect_types=sqlite3.PARSE_DECLTYPES)
                with self.conn:
                    cursor = self.conn.cursor()
                    cursor.execute("update ranges set occupied = 0 where id = 0 and occupied = 1")
                    if cursor.rowcount == 0:
                        logging.debug("Fail to release the lock")
                        success = False
                    else:
                        logging.debug("Success to release the lock")
                        self.conn.commit()
                        success = True
            except sqlite3.Error as e:
                logging.debug("Exception on release: {0}".format(str(e)))
                success = False

            if success:
                break

        self.conn.close()
        return success
