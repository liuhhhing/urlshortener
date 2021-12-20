import unittest
from rangeRetrieveInterface import RangeRetrieveInterface
from rangeRetrieveDB import RangeRetrieveDB
import sqlite3
import threading

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
                i, (i-1)*100 +1, i*100
            ))
    except sqlite3.Error as e:
        print(e)

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
        print(e)

    try:
        for i in range(0, 200):
            cursor.execute('''insert into ranges (id, start, end, occupied) values ({0}, {1}, {2}, 1)'''.format(
                i, (i-1)*100 +1, i*100
            ))
    except sqlite3.Error as e:
        print(e)

    db_connection.commit()

class MyTestCase(unittest.TestCase):
    def test_basic_get_range(self):
        init_db()
        range = RangeRetrieveInterface.register(RangeRetrieveDB)()
        range.db_file = 'test_range.db'
        range.get_lock(100)
        result = range.get_range()
        print (result[0], result[1], result[2])
        range.release_lock()

        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], 100)
        self.assertEqual(result[2], True)

        range.get_lock(100)
        result = range.get_range()
        print(result[0], result[1], result[2])
        range.release_lock()

        self.assertEqual(result[0], 101)
        self.assertEqual(result[1], 200)
        self.assertEqual(result[2], True)

    def test_all_occupied(self):
        init_db_with_all_occupied()

        range = RangeRetrieveInterface.register(RangeRetrieveDB)()
        range.db_file = 'test_range.db'
        range.get_lock(100)
        result = range.get_range()
        print(result[0], result[1], result[2])
        range.release_lock()

        self.assertEqual(result[2], False)

    def test_get_multiple(self):
        init_db()
        range1 = RangeRetrieveInterface.register(RangeRetrieveDB)()
        range2 = RangeRetrieveInterface.register(RangeRetrieveDB)()

        range1.db_file = 'test_range.db'
        range2.db_file = 'test_range.db'

        def thread_func_1():
            for i in range(1, 50):
                range1.get_lock(100000)
                result = range1.get_range()
               # print("From 1 {0}, {1}, {2}".format(result[0], result[1], result[2]))
                range1.release_lock()

        def thread_func_2():
            for i in range(1, 50):
                range2.get_lock(100000)
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
        self.assertEqual(result[0], 98)


if __name__ == '__main__':
    unittest.main()
