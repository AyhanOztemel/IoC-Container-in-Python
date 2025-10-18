from abc import ABC, abstractmethod

# 1. Soyut sınıfları tanımla
class Abs_SingletonService(ABC):
    @abstractmethod
    def process(self):
        pass


class IScopedService(ABC):
    @abstractmethod
    def process(self):
        pass

class ITransientService(ABC):
    @abstractmethod
    def process(self):
        pass

