import logging
import hashlib
import mappingStore
from multiprocessing import Value

class Shortener:
    def __init__(self):
        self.first_n_char = 7
        self.counter = Value('i', 1)
        self.counter_upper_limit = -1  # means no limit
        self.token_url = ''
        self.response_url_prefix = ''
        self.secret_key = '+goodwishtoHongKong'
        self.db_path = None
        # self.file_path = ''
        # self.mapping = {} # this is a dictionary in memory

    def set_counter_range(self, start, end):
        self.counter = Value('i', start)
        self.counter_upper_limit = end

    def still_can_hash(self):
        return self.counter_upper_limit == -1 or self.counter.value <= self.counter_upper_limit

    def generate_hash(self):
        with self.counter.get_lock():
            hash_operation = hashlib.sha256((self.secret_key + str(self.counter.value)).encode()).hexdigest()[:self.first_n_char]
            logging.debug('{{Counter, Hash}} = {{{0},{1}}}'.format(self.counter.value, hash_operation))
            mapping_store = mappingStore.MappingStore(self.db_path)
            while mapping_store.is_hashed_url_exist(hash_operation):  # loop until no cash
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
        if len(self.token_url) > 0:
            # TODO: meaning it is defined, issue a request to the token service and get a new set of counter
            # now just make it a fake one
            self.counter = Value('i', 1)
            # TODO: if the service is defined, we need to see if it can successfully return the new range, not always return true
            return True
        # meaning it is not defined, just return
        return False

    def generate_shortened_url(self, longUrl):
        hash_value, counter_id = self.generate_hash()
        if len(hash_value) == 0 and self.still_can_hash() is False:
            return '', False

        mapping_store = mappingStore.MappingStore(self.db_path)
        mapping_store.insert_hashed_url(counter_id, longUrl, hash_value)
        return hash_value, True
