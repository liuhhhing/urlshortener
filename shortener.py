import logging
import hashlib

class Shortener:
    def __init__(self):
        self.first_n_char = 7
        self.counter = 1
        self.counter_upper_limit = -1  # means no limit
        self.token_url = ''
        self.response_url_prefix = ''
        self.mapping_store = None
        self.secret_key = '+goodwishtoHongKong'
        # self.file_path = ''
        # self.mapping = {} # this is a dictionary in memory

    def still_can_hash(self):
        return self.counter_upper_limit == -1 or self.counter <= self.counter_upper_limit

    def generate_hash(self):

        hash_operation = hashlib.sha256((self.secret_key + str(self.counter)).encode()).hexdigest()[:self.first_n_char]
        logging.debug('{{Counter, Hash}} = {{{0},{1}}}'.format(self.counter, hash_operation))
        while self.mapping_store.is_hashed_url_exist(hash_operation):  # loop until no cash
            # it should happen very rare
            logging.debug('{{Counter, Hash}} = {{{0},{1}}} clash, try again'.format(self.counter, hash_operation))
            self.counter = self.counter + 1
            if not self.still_can_hash():
                break
            hash_operation = hashlib.sha256((self.secret_key + str(self.counter)).encode()).hexdigest()[:self.first_n_char]

        if self.still_can_hash() == False:
            logging.debug('{{Counter, Hash}} = {{{0},{1}}} limit reached'.format(self.counter, hash_operation))
            return ''  # just return nothing

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

    def generate_shortened_url(self, longUrl):
        hash_value = self.generate_hash()
        if len(hash_value) == 0 and self.still_can_hash() is False:
            return '', False

        self.mapping_store.insert_hashed_url(self.counter - 1, longUrl, hash_value)
        return hash_value, True
