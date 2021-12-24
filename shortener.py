import logging
import hashlib
import mappingStoreDB
from multiprocessing import Value
from mappingStoreInterface import MappingStoreInterface
from rangeRetrieveInterface import RangeRetrieveInterface
import rangeRetrieveDB

class Shortener:
    def __init__(self):
        self.first_n_char = 7
        self.counter = Value('i', 1)
        self.counter_upper_limit = -1  # means no limit
        self.response_url_prefix = ''
        self.secret_key = '+goodwishtoHongKong'
        self.db_path = None
        self.mapping_store = None
        self.range_retriever = None
        self.range_retriever_timeout_in_sec = 10 # in sec
        # self.file_path = ''
        # self.mapping = {} # this is a dictionary in memory

    def set_mapping_store(self, mapping_store):
        self.mapping_store = mapping_store

    def set_counter_range(self, start, end):
        self.counter = Value('i', start)
        self.counter_upper_limit = end

    def set_range_retriever(self, db_file, lock_timeout):
        self.range_retriever = RangeRetrieveInterface.register(rangeRetrieveDB.RangeRetrieveDB)()
        self.range_retriever.set_db_file(db_file)
        self.range_retriever_timeout_in_sec = int(lock_timeout)

    def still_can_hash(self):
        result = self.counter_upper_limit == -1 or self.counter.value <= self.counter_upper_limit
        if not result: # meaning all id used up
            # then try to refresh counter, if it still fail it will return False
            # otherwise, it will update the counter value, and the new counter_upper_limit
            return self.refresh_counter()
        return result

    def generate_hash(self):
        with self.counter.get_lock():
            hash_operation = hashlib.sha256((self.secret_key + str(self.counter.value)).encode()).hexdigest()[:self.first_n_char]
            logging.debug('{{Counter, Hash}} = {{{0},{1}}}'.format(self.counter.value, hash_operation))

            self.mapping_store.init_or_open_store(self.db_path)
            while self.mapping_store.is_hashed_url_exist(hash_operation):  # loop until no cash
                # it should happen very rare
                logging.debug('{{Counter, Hash}} = {{{0},{1}}} clash, try again'.format(self.counter.value, hash_operation))
                self.counter.value = self.counter.value + 1
                if not self.still_can_hash():
                    break
                hash_operation = hashlib.sha256((self.secret_key + str(self.counter.value)).encode()).hexdigest()[:self.first_n_char]

            if self.still_can_hash() == False:
                logging.debug('{{Counter, Hash}} = {{{0},{1}}} limit reached'.format(self.counter.value, hash_operation))
                return '', -1  # just return nothing

            logging.debug('{{Counter, Hash}} = {{{0},{1}}} succeed'.format(self.counter.value, hash_operation))
            # all success, inc the counter
            return_counter = self.counter.value
            self.counter.value = self.counter.value + 1
            return hash_operation[:self.first_n_char], return_counter

    def refresh_counter(self):
        logging.debug("Refresh Counter")
        if self.range_retriever is not None:
            if self.range_retriever.get_lock(self.range_retriever_timeout_in_sec):
                result = self.range_retriever.get_range()
                if result[2] == True:
                    self.counter = Value('i', result[0])
                    self.counter_upper_limit = result[1]
                    self.range_retriever.release_lock()
                    return True
                else:
                    self.range_retriever.release_lock()
                    return False
            else:
                return False
        else:
            # meaning it is not defined, just return
            return False

    def generate_shortened_url(self, longUrl):
        hash_value, counter_id = self.generate_hash()
        if len(hash_value) == 0 and self.still_can_hash() is False:
            return '', False

        self.mapping_store.init_or_open_store(self.db_path)
        self.mapping_store.insert_hashed_url(counter_id, longUrl, hash_value)
        return hash_value, True
