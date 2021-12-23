import unittest
from rangeRetrieveInterface import RangeRetrieveInterface
from rangeRetrieveDB import RangeRetrieveDB
import sqlite3
import threading
import os
import time
import logging
import concurrent.futures

logging.basicConfig(format='%(thread)d %(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',
                            level=logging.DEBUG)


def init_db():
    db_connection = sqlite3.connect(str('test_range.db'), detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = db_connection.cursor()
    try:
        cursor.execute('''drop table ranges''')
    except sqlite3.Error as e:
        print(e)

    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS ranges (
            [id] INTEGER NOT NULL unique,
            [start] INTEGER NOT NULL unique,
            [end] INTEGER NOT NULL unique,
            [occupied] INTEGER NOT NULL
            )''')
    except sqlite3.Error as e:
        print(e)

    try:
        for i in range(0, 200):
            cursor.execute('''insert into ranges (id, start, end, occupied) values ({0}, {1}, {2}, 0)'''.format(
                i, (i - 1) * 100 + 1, i * 100
            ))
    except sqlite3.Error as e:
        logging.debug(e)

    db_connection.commit()


def init_db_with_all_occupied():
    db_connection = sqlite3.connect(str('test_range.db'), detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = db_connection.cursor()
    try:
        cursor.execute('''drop table ranges''')
    except sqlite3.Error as e:
        print(e)

    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS ranges (
            [id] INTEGER NOT NULL unique,
            [start] INTEGER NOT NULL unique,
            [end] INTEGER NOT NULL unique,
            [occupied] INTEGER NOT NULL
            )''')
    except sqlite3.Error as e:
        logging.debug(e)

    try:
        cursor.execute('''insert into ranges (id, start, end, occupied) values (0, -99, 1, 0)''')
        for i in range(1, 200):
            cursor.execute('''insert into ranges (id, start, end, occupied) values ({0}, {1}, {2}, 1)'''.format(
                i, (i - 1) * 100 + 1, i * 100
            ))
    except sqlite3.Error as e:
        logging.debug(e)

    db_connection.commit()



class MyTestCase(unittest.TestCase):
    def test_basic_get_range(self):
        init_db()
        rangeObj = RangeRetrieveInterface.register(RangeRetrieveDB)()
        rangeObj.db_file = 'test_range.db'
        rangeObj.get_lock(100)
        result = rangeObj.get_range()
        print(result[0], result[1], result[2])
        rangeObj.release_lock()

        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], 100)
        self.assertEqual(result[2], True)

        rangeObj.get_lock(100)
        result = rangeObj.get_range()
        print(result[0], result[1], result[2])
        rangeObj.release_lock()

        self.assertEqual(result[0], 101)
        self.assertEqual(result[1], 200)
        self.assertEqual(result[2], True)

    def test_all_occupied(self):
        init_db_with_all_occupied()

        rangeObj = RangeRetrieveInterface.register(RangeRetrieveDB)()
        rangeObj.db_file = 'test_range.db'
        if rangeObj.get_lock(100):
            result = rangeObj.get_range()
            print(result[0], result[1], result[2])
            rangeObj.release_lock()

        self.assertEqual(result[2], False)

    def test_lock_timeout(self):
        init_db()
        range1 = RangeRetrieveInterface.register(RangeRetrieveDB)()
        range2 = RangeRetrieveInterface.register(RangeRetrieveDB)()

        range1.db_file = 'test_range.db'
        range2.db_file = 'test_range.db'


        def thread_func_1():
            range1.get_lock(5)
            time.sleep(5) # intend not to release lock

        def thread_func_2():
            time.sleep(1)
            result = range2.get_lock(5) # it should have timeout
            return result

        result = True
        c1 = threading.Thread(target=thread_func_1)
        c1.start()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(thread_func_2)
            result = future.result()


        c1.join()


        self.assertEqual(result, False)

    def test_get_multiple(self):
        init_db()
        range1 = RangeRetrieveInterface.register(RangeRetrieveDB)()
        range2 = RangeRetrieveInterface.register(RangeRetrieveDB)()

        range1.db_file = 'test_range.db'
        range2.db_file = 'test_range.db'

        def thread_func_1():
            for i in range(1, 5):
                if range1.get_lock(10) == True:
                    result = range1.get_range()
                    # print("From 1 {0}, {1}, {2}".format(result[0], result[1], result[2]))
                    range1.release_lock()

        def thread_func_2():
            for i in range(1, 5):
                if range2.get_lock(10) == True:
                    result = range2.get_range()
                    # print("From 2 {0}, {1}, {2}".format(result[0], result[1], result[2]))
                    range2.release_lock()

        c1 = threading.Thread(target=thread_func_1)
        c2 = threading.Thread(target=thread_func_2)

        c1.start()
        c2.start()

        c1.join()
        c2.join()

        conn = sqlite3.connect('test_range.db', detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = conn.cursor()
        cursor.execute("select count(*) from ranges where id > 0 and occupied = 1")
        result = cursor.fetchone()
        self.assertEqual(result[0], 8)


if __name__ == '__main__':
    unittest.main()
