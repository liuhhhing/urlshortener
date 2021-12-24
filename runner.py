import argparse
import socket
import datetime
from flask import Flask, jsonify, redirect
from flask import request
import logging
import shortener
import mappingStoreDB
import mappingStoreFile
from mappingStoreInterface import MappingStoreInterface



app = Flask(__name__)

g_shortener = None
g_mapping_store = None
g_db_path = None
g_range_retriever = None

def init_app():
    global g_shortener
    g_shortener = shortener.Shortener()

def clean_db():

    g_mapping_store.init_or_open_store(g_db_path)
    g_mapping_store.clean_store()


def set_shortener_range(start=1, end=-1):
    global g_shortener
    g_shortener.set_counter_range(start, end)

def set_shortener_range_retriever_as_db(db_path, lock_timeout):
    global g_shortener
    logging.debug("db_path is {0}".format(db_path))

    g_shortener.set_range_retriever(db_path, lock_timeout)

    return g_shortener.refresh_counter()


@app.route('/<hashed_id>')
def redirect_to_link(hashed_id):

    g_mapping_store.init_or_open_store(g_db_path)
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
        app.logger.debug(request.json)
        long_url = request.json['LongURL']

        g_mapping_store.init_or_open_store(g_db_path)
        if g_mapping_store.is_long_url_exist(long_url):
            # if it exists just return directly from the g_g_mapping_store
            hashed_url = g_mapping_store.get_hash_from_long_url(long_url)
            response = {response_key: g_shortener.response_url_prefix + hashed_url}
            return jsonify(response), 200

        # if it doesn't exist then generate the valid shortened URL
        short_url, succeed = g_shortener.generate_shortened_url(long_url)
        if not succeed and g_shortener.still_can_hash() is False:
            return jsonify({'Error': 'Counter All used up'}), 400

        return jsonify({response_key: g_shortener.response_url_prefix + short_url}), 200


def setup_shortener(ip='0.0.0.0', port=5050, first_N=7, response_url_prefix=None, range_db=None, range_db_timeout=5, count_start=1, count_end=-1,
                    storage_type="sqlite",
                    mapping_store_file=None, logger_file_path=None):
    # if logger_file_path exist it will log to file, otherwise it will log to stdout and stderr
    if logger_file_path is not None:
        logging.basicConfig(filename=logger_file_path + "_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
                            format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',
                            level=logging.DEBUG)  # set to DEBUG mode and output to console

    app.logger.info("Running The Shortener service")

    # specify a custom URL prefix to return to the user
    if response_url_prefix is not None:
        g_shortener.response_url_prefix = response_url_prefix.strip('/') + "/"
    else:
        if port != 80:
            g_shortener.response_url_prefix = "http://" + socket.gethostname() + ":" + str(port) + "/"
        else:
            g_shortener.response_url_prefix = "http://" + socket.gethostname() + "/"

    g_shortener.first_n_char = first_N

    if range_db is None:
        set_shortener_range(count_start, count_end)
    else:
        if not set_shortener_range_retriever_as_db(range_db, range_db_timeout):
            raise Exception("Fail to refresh counter from db")

    g_shortener.db_path = mapping_store_file

    # initialize the flask
    app.logger.info("Start the service")

    global g_db_path
    g_db_path = mapping_store_file

    global  g_mapping_store
    if storage_type == 'sqlite':
        g_mapping_store = MappingStoreInterface.register(mappingStoreDB.MappingStoreDB)()
    elif storage_type == 'file':
        g_mapping_store = MappingStoreInterface.register(mappingStoreFile.MappingStoreFile)()
    g_mapping_store.init_or_open_store(g_db_path)

    g_shortener.set_mapping_store(g_mapping_store)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='urlshortener service runner.')
    parser.add_argument('--port', dest='port', type=int, required=False, default=5050,
                        help='The port the service running at')
    parser.add_argument('--ip', dest='ip', type=str, required=False, default='0.0.0.0',
                        help='The ip address to bind for running the service')
    parser.add_argument('--responseUrlprefix', dest='response_url_prefix', type=str, required=False,
                        help='The response URL prefix return to the POST request in the format of http://www.myDesiredDomain/,'
                             'when it is not defined it will be defaulted to system hostname and port like http://www.myHost.com:5050/')
    parser.add_argument('--firstN', dest='first_N', type=int, required=False, default=7,
                        help='The first n characters from the hashed counter to form the shortened URL')
    parser.add_argument('--rangeDB', dest='range_db', type=str, required=False,
                        help='The DB that contains the range to retrieve')
    parser.add_argument('--rangeDBTimeout', dest='range_db_timeout', type=int, required=False, default=5,
                        help='The timeout to get lock or connect to the DB for a new range')
    parser.add_argument('--countRange', dest='count_range', type=str, required=False,
                        help='Hyphen separated range, for example 1-100, if it is not defined it will be defaulted from 1 to sizeof(int)'
                             'When rangeDB is defined the process will ignore this')
    parser.add_argument('--storageType', dest='storage_type', type=str, required=False, default='sqlite',
                        help='The storage type, now it support "sqlite","file". If it is not specified it will be defaulted to sqlite')
    parser.add_argument('--mappingStoreFile', dest='mapping_store_file', type=str, default='mapping.sqlite',
                        required=False,
                        help='The file path that the mapping file saved to, if it is not defined it will be defaulted to be the current'
                             ' running directory and named as mapping.sqlite')
    parser.add_argument('--loggerFilePath', dest='logger_file_path', type=str, required=False,
                        help='The logger file path, if it is not specified, the log will be outputted to console'
                             'Notice the log file name will be appended with the "_YYYYMMDDhhmmss" so on every run '
                             'the previous log will not be overwritten')

    args = parser.parse_args()

    init_app()
    setup_shortener(ip=args.ip,
                    port=args.port,
                    first_N=args.first_N,
                    response_url_prefix=args.response_url_prefix,
                    range_db=args.range_db,
                    range_db_timeout=args.range_db_timeout,
                    count_start=1 if args.count_range is None else int(args.count_range.split("-")[0]),
                    count_end=-1 if args.count_range is None else int(args.count_range.split("-")[1]),
                    storage_type=args.storage_type,
                    mapping_store_file=args.mapping_store_file,
                    logger_file_path=args.logger_file_path)
    app.run(host=args.ip, port=args.port)
