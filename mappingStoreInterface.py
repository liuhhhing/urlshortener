import abc


class MappingStoreInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'init_store') and
                callable(subclass.init_store) and
                hasattr(subclass, 'clean_store') and
                callable(subclass.clean_store) and
                hasattr(subclass, 'insert_hashed_url') and
                callable(subclass.insert_hashed_url) and
                hasattr(subclass, 'is_hashed_url_exist') and
                callable(subclass.is_hashed_url_exist) and
                hasattr(subclass, 'is_long_url_exist') and
                callable(subclass.is_long_url_exist) and
                hasattr(subclass, 'get_long_url_from_hash') and
                callable(subclass.get_long_url_from_hash) and
                hasattr(subclass, 'get_hash_from_long_url') and
                callable(subclass.get_hash_from_long_url) or
                NotImplemented)

    @abc.abstractmethod
    def init_store(self, store_path):
        raise NotImplementedError

    @abc.abstractmethod
    def clean_store(self):
        raise NotImplementedError

    @abc.abstractmethod
    def insert_hashed_url(self, id, long_url, hash):
        raise NotImplementedError

    @abc.abstractmethod
    def is_hashed_url_exist(self, hash_value):
        raise NotImplementedError

    @abc.abstractmethod
    def is_long_url_exist(self, longUrl):
        raise NotImplementedError

    @abc.abstractmethod
    def get_long_url_from_hash(self, hash):
        raise NotImplementedError

    @abc.abstractmethod
    def get_hash_from_long_url(self, longUrl):
        raise NotImplementedError
