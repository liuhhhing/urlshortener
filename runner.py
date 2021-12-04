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
import mappingStore
import shortener
from mappingStore import MappingStore
import os

app = Flask(__name__)

g_shortener = shortener.Shortner()
g_mapping_store = MappingStore()

@app.route('/<hashed_id>')
def redirect_to_link(hashed_id):
    if not g_mapping_store.is_hashed_url_exist(hashed_id):
        return jsonify({'Error': 'No record for this shortened URL ' + hashed_id}), 400
        
    long_url = g_mapping_store.get_long_url_from_hash(hashed_id)
    print(long_url)
    return redirect(long_url)

@app.route("/shorten", methods=['POST'])
def shorten():
    response_key = 'ShortenedURL'
    if request.method == 'POST':
        # get the URL to be shorten
        long_url = request.json[0]['LongURL']
        if g_mapping_store.is_long_url_exist(long_url):
            # if it exists just return directly from the g_mapping_store
            hashed_url = g_mapping_store.get_hash_from_long_url(long_url)
            response = {response_key : g_shortener.url_prefix + hashed_url}
            return jsonify(response), 200

        # if it doesn't exist then generate the valid shortened URL
        short_url, succeed = g_shortener.generate_shortened_url(long_url)
        if not succeed and g_shortener.still_can_hash() is False:
            return jsonify({'Error': 'Counter All used up'}), 400

        return jsonify({response_key: g_shortener.url_prefix + short_url}), 200

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='urlshortener service runner.')
    parser.add_argument('--port', dest='port', type=int, required=False, default=5050, help='The port the service running at')
    parser.add_argument('--ip', dest='ip', type=str, required=False, default='0.0.0.0', help='The ip address to bind for running the service')
    parser.add_argument('--urlprefix', dest='url_prefix', type=str, required=False, help='The URL prefix return to the POST request, when it is not defined it will be defaulted to system hostname')
    parser.add_argument('--firstN', dest='first_N', type=int, required=False, default=7, help='The first n characters from the hashed counter to form the shortened URL')
    parser.add_argument('--tokenUrl', dest='token_url', type=str, required=False, help='The URL to get the range of available counter when it is running in distributed manner')
    parser.add_argument('--countRange', dest='count_range', type=str, required=False, help='Hyphen separated range, for example 1-100, if it is not defined it will be default run from 1 to infinite')
    parser.add_argument('--mappingStoreFile', dest='mapping_store_file', type=str, default='mapping.sqlite', required=False, help='The file path that the mapping saved to, if it is not defined it will be defaulted to be the current running directory and named as mapping.sqlite')
    parser.add_argument('--loggerFilePath', dest='logger_file_path', type=str, required=False, help='The logger file path, if it is not specified, no log will be outputted to file')

    args = parser.parse_args()

    # if logger_file_path exist it will log to file, otherwise it will log to stdout and stderr
    if args.logger_file_path is not None:
        logging.basicConfig(filename=args.logger_file_path + "_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S"), format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG) # set to DEBUG mode and output to console

    app.logger.info("Running The Shortener service")

    # specify a custom URL prefix to return to the user
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

    g_shortener.first_n_char = args.first_N
    if args.token_url is not None:
        g_shortener.token_url = args.token_url
    if args.count_range is not None:
        g_shortener.counter = int(args.count_range.split('-')[0])
        g_shortener.counter_upper_limit = int(args.count_range.split('-')[1])

    # initialize the flask
    app.logger.info("Start the service")    

    g_mapping_store.logger = app.logger
    g_mapping_store.store_path = args.mapping_store_file
    g_shortener.mapping_store = g_mapping_store
    g_mapping_store.init_db()
    app.run(host=args.ip, port=args.port)
