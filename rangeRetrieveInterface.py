import abc

class RangeRetrieveInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'get_lock') and
                callable(subclass.get_lock) and
                hasattr(subclass, 'get_range') and
                callable(subclass.get_range) and
                hasattr(subclass, 'release_lock') and
                callable(subclass.release_lock) or
                NotImplemented)

    @abc.abstractmethod
    def get_lock(self, timeout):
        raise NotImplementedError

    @abc.abstractmethod
    def get_range(self):
        raise NotImplementedError

    @abc.abstractmethod
    def release_lock(self):
        raise NotImplementedError
