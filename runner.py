import argparse
import hashlib
import datetime
import requests
from flask import Flask, jsonify
from flask import request
import json

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

class Shortner:
    def __init__(self):
        self.first_n_char = 7
        self.counter = 1
        self.counter_upper_limit = -1 # means no limit
        self.token_url = ''
        self.url_prefix = ''
        self.mapping = {} # this is a dictionary in memory

    def is_long_url_exist(self, longUrl):
        return longUrl in self.mapping.keys()

    def still_can_hash(self):
        return self.counter_upper_limit == -1 or self.counter < self.counter_upper_limit

    def generate_hash(self):
        hash_operation = hashlib.sha256(str(self.counter).encode()).hexdigest()[:self.first_n_char]
        while hash_operation in self.mapping.values(): # loop until no cash
            self.counter = self.counter + 1
            if self.still_can_hash():
                break
            hash_operation = hashlib.sha256(str(self.counter).encode()).hexdigest()[:self.first_n_char]

        if self.still_can_hash() == False:
            return '' # just return nothing

        # all success, inc the counter
        self.counter = self.counter + 1
        return hash_operation[:self.first_n_char]

    def refresh_counter(self):
        if len(self.token_url) > 0:
            # TODO: meaning it is defined, issue a request to the token service and get a new set of counter
            # now just make it a fake one
            self.counter = 1
            # TODO: if the service is defined, we need to see if it can successfully return the new range, not always return true
            return True
        # meaning it is not defined, just return
        return False

    def generate_shortened_url(self, longUrl):
        hash = self.generate_hash()
        if len(hash) == 0 and self.still_can_hash() == False:
            return '', False
        # TODO: Save to a permanent disk rather than in memory
        self.mapping[longUrl] = hash
        return hash, True

g_shortener = Shortner()

@app.route("/shorten", methods=['POST'])
def shorten():
    if request.method == 'POST':
        # get the URL to be shorten
        longUrl = request.json[0]['LongURL']
        if g_shortener.is_long_url_exist(longUrl):
            response = {'shortenedUrl': g_shortener.url_prefix + g_shortener.mapping[longUrl]}
            return jsonify(response), 200
        shortUrl, succeed = g_shortener.generate_shortened_url(longUrl)
        if not succeed and g_shortener.still_can_hash() == False:
            return jsonify({'Error': 'Counter All used up'}), 400

        return jsonify({'shortenedUrl': g_shortener.url_prefix + shortUrl}), 200

def loadMap():
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='urlshortener service runner.')
    parser.add_argument('--port', dest='port', type=int, required=False, default=5050, help='The port the service running at')
    parser.add_argument('--ip', dest='ip', type=str, required=False, default='0.0.0.0', help='The ip address to bind for running the service')
    parser.add_argument('--urlprefix', dest='url_prefix', type=str, required=False, default='http://hing.com/', help='The URL prefix return to the POST request')
    parser.add_argument('--firstN', dest='first_N', type=int, required=False, default=7, help='The first n characters from the hashed counter to form the shortened URL')
    parser.add_argument('--tokenUrl', dest='token_url', type=str, required=False, help='The URL to get the range of counter')
    parser.add_argument('--countRange', dest='count_range', type=str, required=False, help='hyphen separated range, for example 1-100, if not defined it will be default run from 1 to infinite')
    args = parser.parse_args()

    g_shortener.url_prefix = args.url_prefix
    g_shortener.first_n_char = args.first_N
    if args.token_url is not None:
        g_shortener.token_url = args.token_url
    if args.count_range is not None:
        g_shortener.counter = int(args.count_range.split('-')[0])
        g_shortener.counter_upper_limit = int(args.count_range.split('-')[1])
    # TODO: load the g_shortener.mapping from a centralized database

    # initialize the flask
    app.run(host=args.ip, port=args.port)

    print "hello world"
