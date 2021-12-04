import unittest
import requests
import threading
import time
from runner import run_shortener


class MyTestCase(unittest.TestCase):
    def test_shorten_url(self):
        def thread_function(ip, port):
            run_shortener(ip, port, 7, None, None, None, 'test2.sqlite', None)

        x = threading.Thread(target=thread_function, args=('127.0.0.1', 5051))
        x.setDaemon(True)
        x.start()

        print("just start")
        time.sleep(5)

        try:
            json_obj = [{"LongURL": "http://www.google.com"}]
            response = requests.post('http://127.0.0.1:5051/shorten/', headers={"Accept": "*/*"}, data={"LongURL":"http://www.google.com"})
            print response.content
        except requests.exceptions.HTTPError as error:
            print(error)

        print("sent")
        time.sleep(5)

        self.assertEqual(True, True)  # add assertion here


if __name__ == '__main__':
    unittest.main()
