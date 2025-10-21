# 2. Somut implementasyonlar oluştur
from abs_services import Abs_SingletonService,IScopedService,ITransientService


class SingletonService(Abs_SingletonService):
    def process(self):
    
        return "Singleton İşlendi"

class ScopedService(IScopedService):
    def process(self):
        return "Scoped İşlendi"

class TransientService(ITransientService):
    def process(self):
        return "Transient İşlendi"
