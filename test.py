import unittest
import threading
from runner import setup_shortener
from runner import app
from runner import init_app
from runner import clean_db
import hashlib


def get_shortened_url(to_be_hash, domain):
    hash_value = hashlib.sha256(('+goodwishtoHongKong' + str(to_be_hash)).encode()).hexdigest()[:7]
    shortened = """{0}{1}""".format(domain, hash_value)
    shortened = '{"ShortenedURL":"' + shortened + '"}\n'
    return shortened, hash_value


class MyTestCase(unittest.TestCase):

    def test_first_time_shorten_url(self):
        init_app()
        setup_shortener(response_url_prefix='http://mydomain.com/', port=5050, mapping_store_file='mappingTest.sqlite')
        clean_db()

        def thread_func():
            app.run()

        threading.Thread(target=thread_func)

        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'}, json={'LongURL': 'http://www.yahoo.com'})
        shortened, hash_value = get_shortened_url(1, 'http://mydomain.com/')
        self.assertEqual(rv.data, shortened.encode('UTF-8'))

    def test_redirect_from_shorten_url(self):
        init_app()
        setup_shortener(response_url_prefix='http://mydomain.com/', port=5050, mapping_store_file='mappingTest.sqlite')
        clean_db()

        def thread_func():
            app.run()

        threading.Thread(target=thread_func)

        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'}, json={'LongURL': 'http://www.yahoo.com'})
        shortened, hash_value = get_shortened_url(1, 'http://mydomain.com/')
        self.assertEqual(rv.data, shortened.encode('UTF-8'))

        rv = app.test_client().get('/' + hash_value)
        self.assertEqual(rv.location, 'http://www.yahoo.com')

    def test_shorten_same_url(self):
        init_app()
        setup_shortener(response_url_prefix='http://mydomain.com/', port=5050, mapping_store_file='mappingTest.sqlite')
        clean_db()

        def thread_func():
            app.run()

        threading.Thread(target=thread_func)

        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'}, json={'LongURL': 'http://www.yahoo.com'})
        shortened, hash_value = get_shortened_url(1, 'http://mydomain.com/')
        self.assertEqual(rv.data, shortened.encode('UTF-8'))

        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'}, json={'LongURL': 'http://www.yahoo.com'})
        shortened, hash_value = get_shortened_url(1, 'http://mydomain.com/')
        self.assertEqual(rv.data, shortened.encode('UTF-8'))

        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'}, json={'LongURL': 'http://www.yahoo.com'})
        shortened, hash_value = get_shortened_url(1, 'http://mydomain.com/')
        self.assertEqual(rv.data, shortened.encode('UTF-8'))

        rv = app.test_client().get('/' + hash_value)
        self.assertEqual(rv.location, 'http://www.yahoo.com')

    def test_shorten_diff_url(self):
        init_app()
        setup_shortener(response_url_prefix='http://mydomain.com/', port=5050, mapping_store_file='mappingTest.sqlite')
        clean_db()

        def thread_func():
            app.run()

        threading.Thread(target=thread_func)

        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'}, json={'LongURL': 'http://www.yahoo.com'})
        shortened, hash_value1 = get_shortened_url(1, 'http://mydomain.com/')
        self.assertEqual(rv.data, shortened.encode('UTF-8'))

        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'}, json={'LongURL': 'http://www.google.com'})
        shortened, hash_value2 = get_shortened_url(2, 'http://mydomain.com/')
        self.assertEqual(rv.data, shortened.encode('UTF-8'))

        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'}, json={'LongURL': 'http://www.tvb.com'})
        shortened, hash_value3 = get_shortened_url(3, 'http://mydomain.com/')
        self.assertEqual(rv.data, shortened.encode('UTF-8'))

        rv = app.test_client().get('/' + hash_value1)
        self.assertEqual(rv.location, 'http://www.yahoo.com')

        rv = app.test_client().get('/' + hash_value2)
        self.assertEqual(rv.location, 'http://www.google.com')

        rv = app.test_client().get('/' + hash_value3)
        self.assertEqual(rv.location, 'http://www.tvb.com')

    def test_counter_range(self):
        init_app()
        setup_shortener(response_url_prefix='http://mydomain.com/', port=5050, count_start=1, count_end=5, mapping_store_file='mappingTest.sqlite')
        clean_db()

        def thread_func():
            app.run()

        threading.Thread(target=thread_func)

        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'}, json={'LongURL': 'http://www.music1.com'})
        shortened, hash_value1 = get_shortened_url(1, 'http://mydomain.com/')
        self.assertEqual(rv.data, shortened.encode('UTF-8'))

        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'}, json={'LongURL': 'http://www.music2.com'})
        shortened, hash_value2 = get_shortened_url(2, 'http://mydomain.com/')
        self.assertEqual(rv.data, shortened.encode('UTF-8'))

        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'}, json={'LongURL': 'http://www.music3.com'})
        shortened, hash_value3 = get_shortened_url(3, 'http://mydomain.com/')
        self.assertEqual(rv.data, shortened.encode('UTF-8'))

        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'}, json={'LongURL': 'http://www.music4.com'})
        shortened, hash_value4 = get_shortened_url(4, 'http://mydomain.com/')
        self.assertEqual(rv.data, shortened.encode('UTF-8'))

        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'}, json={'LongURL': 'http://www.music5.com'})
        shortened, hash_value5= get_shortened_url(5, 'http://mydomain.com/')
        self.assertEqual(rv.data, shortened.encode('UTF-8'))

        # this exceed the limit
        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'}, json={'LongURL': 'http://www.music6.com'})
        shortened, hash_value6 = get_shortened_url(6, 'http://mydomain.com/')
        self.assertEqual(rv.data, b'{"Error":"Counter All used up"}\n')

        rv = app.test_client().get('/'+ hash_value1)
        self.assertEqual(rv.location, 'http://www.music1.com')

        rv = app.test_client().get('/' + hash_value2)
        self.assertEqual(rv.location, 'http://www.music2.com')

        rv = app.test_client().get('/' + hash_value3)
        self.assertEqual(rv.location, 'http://www.music3.com')

        rv = app.test_client().get('/' + hash_value4)
        self.assertEqual(rv.location, 'http://www.music4.com')

        rv = app.test_client().get('/' + hash_value5)
        self.assertEqual(rv.location, 'http://www.music5.com')

        rv = app.test_client().get('/' + hash_value6)
        error = '{{"Error":"No record for this shortened URL {0}"}}\n'.format(hash_value6).encode('UTF-8')
        self.assertEqual(rv.data, error)

    def test_non_exist_hash(self):
        init_app()
        setup_shortener(response_url_prefix='http://mydomain.com/', port=5050, count_start=1, count_end=5, mapping_store_file='mappingTest.sqlite')
        clean_db()

        def thread_func():
            app.run()

        threading.Thread(target=thread_func)

        rv = app.test_client().get('/e7f6c01') # put a random one
        self.assertEqual(rv.data, b'{"Error":"No record for this shortened URL e7f6c01"}\n')

    def test_range_clash(self):
        init_app()
        setup_shortener(response_url_prefix='http://mydomain.com/', port=5050, count_start=1, count_end=-1, mapping_store_file='mappingTest.sqlite')
        clean_db()

        def thread_func():
            app.run()

        threading.Thread(target=thread_func)

        for x in range(1, 50):
            url = 'http://www.music{0}.com'.format(x)
            rv = app.test_client().post('/shorten', headers={'Accept': '*/*'},
                                        json={'LongURL': url})
            shortened, hash_value = get_shortened_url(x, 'http://mydomain.com/')
            self.assertEqual(rv.data, shortened.encode('UTF-8'))

        for x in range(1, 50):
            shortened, hash_value = get_shortened_url(x, 'http://mydomain.com/')
            rv = app.test_client().get('/' + hash_value)
            long_url = 'http://www.music{0}.com'.format(x)
            self.assertEqual(rv.location, long_url)

        init_app()
        setup_shortener(response_url_prefix='http://mydomain.com/', port=5050, count_start=40, count_end=45, mapping_store_file='mappingTest.sqlite')

        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'},
                                    json={'LongURL': 'http://www.shouldbebad.com'})
        self.assertEqual(rv.data, b'{"Error":"Counter All used up"}\n')

    def test_range_out_of_clash(self):
        init_app()
        setup_shortener(response_url_prefix='http://mydomain.com/', port=5050, count_start=1, count_end=-1, mapping_store_file='mappingTest.sqlite')
        clean_db()

        def thread_func():
            app.run()

        threading.Thread(target=thread_func)

        for x in range(1, 50):
            url = 'http://www.out{0}.com'.format(x)
            rv = app.test_client().post('/shorten', headers={'Accept': '*/*'},
                                        json={'LongURL': url})
            shortened, hash_value = get_shortened_url(x, 'http://mydomain.com/')
            self.assertEqual(rv.data, shortened.encode('UTF-8'))

        for x in range(1, 50):
            shortened, hash_value = get_shortened_url(x, 'http://mydomain.com/')
            rv = app.test_client().get('/' + hash_value)
            long_url = 'http://www.out{0}.com'.format(x)
            self.assertEqual(rv.location, long_url)

        init_app()
        setup_shortener(response_url_prefix='http://mydomain.com/', port=5050, count_start=55, count_end=-1, mapping_store_file='mappingTest.sqlite')

        rv = app.test_client().post('/shorten', headers={'Accept': '*/*'}, json={'LongURL': 'http://www.shouldbegood.com'})
        shortened, hash_value = get_shortened_url(55, 'http://mydomain.com/')
        self.assertEqual(rv.data, shortened.encode('UTF-8'))

    def test_multiple(self):
        init_app()
        setup_shortener(response_url_prefix='http://mydomain.com/', port=5050, mapping_store_file='mappingTest.sqlite', count_start=1, count_end=20)
        clean_db()

        def thread_func():
            app.run()

        threading.Thread(target=thread_func)

        def thread_client(start,end):
            for x in range(start,end+1):
                url = 'http://www.music{0}.com'.format(x)
                app.test_client().post('/shorten', headers={'Accept': '*/*'}, json={'LongURL': url})

        c1 = threading.Thread(target=thread_client, args=(1,10))
        c2 = threading.Thread(target=thread_client, args=(11,20))

        c1.start()
        c2.start()

        c1.join()
        c2.join()

        expected_long_url_list = ['http://www.music1.com',
                                  'http://www.music10.com',
                                  'http://www.music11.com',
                                  'http://www.music12.com',
                                  'http://www.music13.com',
                                  'http://www.music14.com',
                                  'http://www.music15.com',
                                  'http://www.music16.com',
                                  'http://www.music17.com',
                                  'http://www.music18.com',
                                  'http://www.music19.com',
                                  'http://www.music2.com',
                                  'http://www.music20.com',
                                  'http://www.music3.com',
                                  'http://www.music4.com',
                                  'http://www.music5.com', 'http://www.music6.com', 'http://www.music7.com', 'http://www.music8.com', 'http://www.music9.com']
        long_url_list = []
        for x in range(1, 20+1):
            shortened, hash_value = get_shortened_url(x, 'http://mydomain.com/')
            rv = app.test_client().get('/' + hash_value)
            long_url_list.append(rv.location)

        # since it is in multithread the hash value (for example "1") can map to the url of 2 (for example http://music3.com)
        # so now we just make sure the hash get of 1-20 can get our desired list of URL correctly
        long_url_list.sort()
        self.assertEqual(long_url_list, expected_long_url_list)



    def test_stress(self):
        init_app()
        setup_shortener(response_url_prefix='http://mydomain.com/', port=5050, count_start=1, count_end=-1, mapping_store_file='mappingTest.sqlite')
        clean_db()

        def thread_func():
            app.run()

        threading.Thread(target=thread_func)

        for x in range(1, 100):
            url = 'http://www.music{0}.com'.format(x)
            rv = app.test_client().post('/shorten', headers={'Accept': '*/*'},
                                        json={'LongURL': url})
            shortened, hash_value = get_shortened_url(x, 'http://mydomain.com/')
            self.assertEqual(rv.data, shortened.encode('UTF-8'))

        for x in range(1, 100):
            shortened, hash_value = get_shortened_url(x, 'http://mydomain.com/')
            rv = app.test_client().get('/' + hash_value)
            long_url = 'http://www.music{0}.com'.format(x)
            self.assertEqual(rv.location, long_url)


if __name__ == '__main__':
    unittest.main()
