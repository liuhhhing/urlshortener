import unittest
import requests
import threading
import time
from runner import setup_shortener
from runner import app
from runner import init_app
from runner import clean_db
import hashlib
#from runner import set_shortener_range
from flask import jsonify
import json
from flask import Flask
import pytest
import pytest_flask


class MyTestCase(unittest.TestCase):

    def test_first_time_shorten_url(self):
        init_app()
        setup_shortener(url_prefix='http://mydomain.com/', port=5050)
        clean_db()

        def thread_func():
            app.run()

        threading.Thread(target=thread_func)

        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'}, json=[{'LongURL': 'http://www.yahoo.com'}])
        self.assertEqual(rv.data, b'{"ShortenedURL":"http://mydomain.com:5050/6b86b27"}\n')

    def test_redirect_from_shorten_url(self):
        init_app()
        setup_shortener(url_prefix='http://mydomain.com/', port=5050)
        clean_db()

        def thread_func():
            app.run()

        threading.Thread(target=thread_func)

        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'}, json=[{'LongURL': 'http://www.yahoo.com'}])
        self.assertEqual(rv.data, b'{"ShortenedURL":"http://mydomain.com:5050/6b86b27"}\n')

        rv = app.test_client().get('/6b86b27')
        self.assertEqual(rv.location, 'http://www.yahoo.com')

    def test_shorten_same_url(self):
        init_app()
        setup_shortener(url_prefix='http://mydomain.com/', port=5050)
        clean_db()

        def thread_func():
            app.run()

        threading.Thread(target=thread_func)

        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'}, json=[{'LongURL': 'http://www.yahoo.com'}])
        self.assertEqual(rv.data, b'{"ShortenedURL":"http://mydomain.com:5050/6b86b27"}\n')

        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'}, json=[{'LongURL': 'http://www.yahoo.com'}])
        self.assertEqual(rv.data, b'{"ShortenedURL":"http://mydomain.com:5050/6b86b27"}\n')

        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'}, json=[{'LongURL': 'http://www.yahoo.com'}])
        self.assertEqual(rv.data, b'{"ShortenedURL":"http://mydomain.com:5050/6b86b27"}\n')

        rv = app.test_client().get('/6b86b27')
        self.assertEqual(rv.location, 'http://www.yahoo.com')

    def test_shorten_diff_url(self):
        init_app()
        setup_shortener(url_prefix='http://mydomain.com/', port=5050)
        clean_db()

        def thread_func():
            app.run()

        threading.Thread(target=thread_func)

        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'}, json=[{'LongURL': 'http://www.yahoo.com'}])
        self.assertEqual(rv.data, b'{"ShortenedURL":"http://mydomain.com:5050/6b86b27"}\n')

        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'}, json=[{'LongURL': 'http://www.google.com'}])
        self.assertEqual(rv.data, b'{"ShortenedURL":"http://mydomain.com:5050/d4735e3"}\n')

        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'}, json=[{'LongURL': 'http://www.tvb.com'}])
        self.assertEqual(rv.data, b'{"ShortenedURL":"http://mydomain.com:5050/4e07408"}\n')

        rv = app.test_client().get('/6b86b27')
        self.assertEqual(rv.location, 'http://www.yahoo.com')

        rv = app.test_client().get('/d4735e3')
        self.assertEqual(rv.location, 'http://www.google.com')

        rv = app.test_client().get('/4e07408')
        self.assertEqual(rv.location, 'http://www.tvb.com')

    def test_counter_range(self):
        init_app()
        setup_shortener(url_prefix='http://mydomain.com/', port=5050, count_start=1, count_end=5)
        clean_db()

        def thread_func():
            app.run()

        threading.Thread(target=thread_func)

        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'}, json=[{'LongURL': 'http://www.music1.com'}])
        self.assertEqual(rv.data, b'{"ShortenedURL":"http://mydomain.com:5050/6b86b27"}\n')

        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'}, json=[{'LongURL': 'http://www.music2.com'}])
        self.assertEqual(rv.data, b'{"ShortenedURL":"http://mydomain.com:5050/d4735e3"}\n')

        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'}, json=[{'LongURL': 'http://www.music3.com'}])
        self.assertEqual(rv.data, b'{"ShortenedURL":"http://mydomain.com:5050/4e07408"}\n')

        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'}, json=[{'LongURL': 'http://www.music4.com'}])
        self.assertEqual(rv.data, b'{"ShortenedURL":"http://mydomain.com:5050/4b22777"}\n')

        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'}, json=[{'LongURL': 'http://www.music5.com'}])
        self.assertEqual(rv.data, b'{"ShortenedURL":"http://mydomain.com:5050/ef2d127"}\n')

        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'}, json=[{'LongURL': 'http://www.music6.com'}])
        self.assertEqual(rv.data, b'{"Error":"Counter All used up"}\n')


        rv = app.test_client().get('/6b86b27')
        self.assertEqual(rv.location, 'http://www.music1.com')

        rv = app.test_client().get('/d4735e3')
        self.assertEqual(rv.location, 'http://www.music2.com')

        rv = app.test_client().get('/4e07408')
        self.assertEqual(rv.location, 'http://www.music3.com')

        rv = app.test_client().get('/4b22777')
        self.assertEqual(rv.location, 'http://www.music4.com')

        rv = app.test_client().get('/e7f6c01')
        self.assertEqual(rv.data, b'{"Error":"No record for this shortened URL e7f6c01"}\n')

    def test_non_exist_hash(self):
        init_app()
        setup_shortener(url_prefix='http://mydomain.com/', port=5050, count_start=1, count_end=5)
        clean_db()

        def thread_func():
            app.run()

        threading.Thread(target=thread_func)

        rv = app.test_client().get('/e7f6c01')
        self.assertEqual(rv.data, b'{"Error":"No record for this shortened URL e7f6c01"}\n')

    def test_range_clash(self):
        init_app()
        setup_shortener(url_prefix='http://mydomain.com/', port=5050, mapping_store_file='test_clash.sqlite',
                        count_start=30, count_end=40)

        for x in range(30, 41):
            url = 'http://www.notgood{0}.com'.format(x)
            rv = app.test_client().post('/shorten', headers={'Accept': '*/*'},
                                        json=[{'LongURL': url}])
            self.assertEqual(rv.data, b'{"Error":"Counter All used up"}\n')


    def test_range_clash(self):
        init_app()
        setup_shortener(url_prefix='http://mydomain.com/', port=5050, mapping_store_file='test_clash.sqlite',
                        count_start=30, count_end=40)

        for x in range(30, 41):
            url = 'http://www.notgood{0}.com'.format(x)
            rv = app.test_client().post('/shorten', headers={'Accept': '*/*'},
                                        json=[{'LongURL': url}])
            self.assertEqual(rv.data, b'{"Error":"Counter All used up"}\n')


    def test_stress(self):
        init_app()
        setup_shortener(url_prefix='http://mydomain.com/', port=5050, count_start=1, count_end=-1)
        clean_db()

        def thread_func():
            app.run()

        threading.Thread(target=thread_func)

        for x in range(1,100):
            url = 'http://www.music{0}.com'.format(x)
            rv = app.test_client().post('/shorten', headers={'Accept': '*/*'},
                                        json=[{'LongURL': url}])
            hash_value = hashlib.sha256(str(x).encode()).hexdigest()[:7]
            shortened = """http://mydomain.com:5050/{0}""".format(hash_value)
            shortened = '{"ShortenedURL":"' + shortened + '"}\n'
            self.assertEqual(rv.data, shortened.encode('UTF-8'))

        for x in range(1,100):
            hash_value = hashlib.sha256(str(x).encode()).hexdigest()[:7]
            rv = app.test_client().get('/' + hash_value)
            long_url = 'http://www.music{0}.com'.format(x)
            self.assertEqual(rv.location, long_url)




if __name__ == '__main__':
    unittest.main()
