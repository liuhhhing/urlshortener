import argparse
import hashlib
import socket
import datetime
import requests
from flask import Flask, jsonify, redirect
from flask import request
import json
import pickle
import logging

app = Flask(__name__)

class Shortner:
    def __init__(self):
        self.first_n_char = 7
        self.counter = 1
        self.counter_upper_limit = -1 # means no limit
        self.token_url = ''
        self.url_prefix = ''
        self.file_path = ''
        self.mapping = {} # this is a dictionary in memory

    def is_long_url_exist(self, longUrl):
        return longUrl in self.mapping.keys()

    def still_can_hash(self):
        return self.counter_upper_limit == -1 or self.counter < self.counter_upper_limit

    def generate_hash(self):
        hash_operation = hashlib.sha256(str(self.counter).encode()).hexdigest()[:self.first_n_char]
        logging.debug('{{Counter, Hash}} = {{{0},{1}}}'.format(self.counter, hash_operation))
        while hash_operation in self.mapping.values(): # loop until no cash
            # it should happen very rarely
            logging.debug('{{Counter, Hash}} = {{{0},{1}}} clash, try again'.format(self.counter, hash_operation))
            self.counter = self.counter + 1
            if self.still_can_hash():
                break
            hash_operation = hashlib.sha256(str(self.counter).encode()).hexdigest()[:self.first_n_char]


        if self.still_can_hash() == False:
            logging.debug('{{Counter, Hash}} = {{{0},{1}}} limit reached'.format(self.counter, hash_operation))
            return '' # just return nothing

        logging.debug('{{Counter, Hash}} = {{{0},{1}}} succeed'.format(self.counter, hash_operation))
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

    def save_mapping(self):
        # TODO: Support saving to different interface, for example, DB, queue, file ... etc
        if len(self.file_path) > 0:
            try:
                with open(self.file_path, 'ab+') as f:
                    pickle.dump(self.mapping, f, pickle.HIGHEST_PROTOCOL)
            except IOError:
                pass

    def load_mapping(self):
        # TODO: Support loading from different interface, for example, DB, queue, file ... etc
        if len(self.file_path) > 0:
            try:
                with open(self.file_path, 'rb+') as f:
                    self.mapping = pickle.load(f)
            except EOFError:
                print("EOF Error when Loading ... ")
            except IOError:
                pass

    def generate_shortened_url(self, longUrl):
        hash = self.generate_hash()
        if len(hash) == 0 and self.still_can_hash() == False:
            return '', False

        self.mapping[longUrl] = hash
        self.save_mapping()
        return hash, True

g_shortener = Shortner()

@app.route('/<hashed_id>')
def redirect_to_link(hashed_id):
    if hashed_id not in g_shortener.mapping.values():
        return jsonify({'Error': 'No record for this shortened URL ' + hashed_id}), 400
    long_url = list(g_shortener.mapping.keys())[list(g_shortener.mapping.values()).index(hashed_id)]
    print(long_url)
    return redirect(long_url)

@app.route("/shorten", methods=['POST'])
def shorten():
    response_key = 'ShortenedURL'
    if request.method == 'POST':
        # get the URL to be shorten
        long_url = request.json[0]['LongURL']
        if g_shortener.is_long_url_exist(long_url):
            response = {response_key : g_shortener.url_prefix + g_shortener.mapping[long_url]}
            return jsonify(response), 200
        short_url, succeed = g_shortener.generate_shortened_url(long_url)
        if not succeed and g_shortener.still_can_hash() == False:
            return jsonify({'Error': 'Counter All used up'}), 400

        return jsonify({response_key: g_shortener.url_prefix + short_url}), 200

def loadMap():
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='urlshortener service runner.')
    parser.add_argument('--port', dest='port', type=int, required=False, default=5050, help='The port the service running at')
    parser.add_argument('--ip', dest='ip', type=str, required=False, default='0.0.0.0', help='The ip address to bind for running the service')
    parser.add_argument('--urlprefix', dest='url_prefix', type=str, required=False, help='The URL prefix return to the POST request, when it is not defined it will be defaulted to system hostname')
    parser.add_argument('--firstN', dest='first_N', type=int, required=False, default=7, help='The first n characters from the hashed counter to form the shortened URL')
    parser.add_argument('--tokenUrl', dest='token_url', type=str, required=False, help='The URL to get the range of available counter when it is running in distributed manner')
    parser.add_argument('--countRange', dest='count_range', type=str, required=False, help='Hyphen separated range, for example 1-100, if it is not defined it will be default run from 1 to infinite')
    parser.add_argument('--filePath', dest='file_path', type=str, required=False, help='The file path that the mapping saved to, if it is not defined it will just use the memory way')
    parser.add_argument('--verbose', dest='verbose', action="store_true", help='Increase logging verbosity')
    parser.add_argument('--loggerFilePath', dest='logger_file_path', type=str, required=False, help='The logger file path, if it is not specified, no log will be outputted to file')

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG) # set to DEBUG mode and output to console
    else:
        if args.logger_file_path is not None:
            logging.basicConfig(filename=args.logger_file_path + "_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S"), format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)

    app.logger.info("Running The Shortener service")

    if args.url_prefix is not None:
        if args.port != 80:
            g_shortener.url_prefix = args.url_prefix.strip('/') + ":" + str(args.port) + "/"
        else:
            g_shortener.url_prefix = args.url_prefix.strip('/') + "/"
    else:
        if args.port != 80:
            g_shortener.url_prefix = "http://"+socket.gethostname() +":" + str(args.port) +"/"
        else:
            g_shortener.url_prefix = "http://"+socket.gethostname() + "/"

    if args.file_path is not None:
        g_shortener.file_path = args.file_path
        g_shortener.load_mapping()

#    logger.debug("URL_PREFIX=" + g_shortener.url_prefix)

    g_shortener.first_n_char = args.first_N
    if args.token_url is not None:
        g_shortener.token_url = args.token_url
    if args.count_range is not None:
        g_shortener.counter = int(args.count_range.split('-')[0])
        g_shortener.counter_upper_limit = int(args.count_range.split('-')[1])

    # initialize the flask
    app.logger.info("Start the service")
    app.run(host=args.ip, port=args.port)
