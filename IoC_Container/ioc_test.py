from abc import ABC, abstractmethod
from ioc_container import Container

# 1. Soyut sınıfları tanımla
class ISingletonService(ABC):
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

# 2. Somut implementasyonlar oluştur
class SingletonService(ISingletonService):
    def process(self):
        return "Singleton İşlendi"

class ScopedService(IScopedService):
    def process(self):
        return "Scoped İşlendi"

class TransientService(ITransientService):
    def process(self):
        return "Transient İşlendi"

# 3. IoC Container'ı oluştur
container = Container()

# 4. Servisleri kaydet
container.register_singleton(ISingletonService, SingletonService)
container.register_scoped(IScopedService, ScopedService)
container.register_transient(ITransientService, TransientService)

# 5. Singleton Test
singleton1 = container.resolve(ISingletonService)
singleton2 = container.resolve(ISingletonService)
singleton3 = container.resolve(ISingletonService)

print("Singleton Test:", singleton1 is singleton2 is singleton3)  # True (Aynı nesne)
print(singleton1.process())  # "Singleton İşlendi"
print(id(singleton1))
print(id(singleton2))
print(id(singleton3))
# 6. Scoped Test
with container.create_scope() as scope1:
    scoped1 = scope1.resolve(IScopedService)
    scoped2 = scope1.resolve(IScopedService)
    scoped3 = scope1.resolve(IScopedService)
with container.create_scope() as scope2:
    scoped4 = scope2.resolve(IScopedService)
    scoped5 = scope2.resolve(IScopedService)
    scoped6 = scope2.resolve(IScopedService)

print("Scoped Test (Aynı Scope):", scoped1 is scoped2 is scoped3)  # True (Aynı scope içinde aynı nesne)
print(scoped1.process())  # "Scoped İşlendi"
print(id(scoped1))
print(id(scoped2))
print(id(scoped3))
print(id(scoped4))
print(id(scoped5))
print(id(scoped6))
with container.create_scope() as scope2:
    scoped4 = scope2.resolve(IScopedService)

print("Scoped Test (Farklı Scope'lar):", scoped1 is not scoped4)  # True (Farklı scope'larda farklı nesneler)

# 7. Transient Test
transient1 = container.resolve(ITransientService)
transient2 = container.resolve(ITransientService)
transient3 = container.resolve(ITransientService)

print("Transient Test:", transient1 is not transient2 and transient2 is not transient3)  # True (Her çağrıda yeni nesne)
print(transient1.process())  # "Transient İşlendi"
print(id(transient1))
print(id(transient2))
print(id(transient3))
