
from register import container
from register import Abs_SingletonService,IScopedService
from scope_ins import  Scoped_Instance
print("--------------ioc_test.py-------------------------------")
# 5. Singleton Test
singleton1 = container.resolve(Abs_SingletonService)
singleton2 = container.resolve(Abs_SingletonService)
singleton3 = container.resolve(Abs_SingletonService)

print("Singleton Test:", singleton1 is singleton2 is singleton3)  # True (Aynı nesne)
print(singleton1.process())  # "Singleton İşlendi"
print(id(singleton1))
print(id(singleton2))
print(id(singleton3))
print("----------------------------------------------------------")

print("---------------------genator kullanarak-------------------------------------")
def request_scope():
    # İstek başında aç, yanıt dönerken kapanır
    with container.create_scope() as scope:
        yield scope


scope_gen = request_scope()          # generator oluşturulur
scopeK = next(scope_gen)             # yield'e kadar gider, scope döner

scoped9 = scopeK.resolve(IScopedService)
scoped10 = scopeK.resolve(IScopedService)

print(scoped9 is scoped10)           # True
print(id(scoped9))
print(id(scoped10))
print("Scoped Test (scoped9 is not scoped10):", scoped9 is not scoped10)  # False(aynı scope'larda farklı nesneler)
next(scope_gen, None)  # 🔹 Bu satır scope’u otomatik kapatır

print("---------------------genator kullanarak-------------------------------------")
scope_gen = request_scope()          # generator oluşturulur
scopeH = next(scope_gen)             # yield'e kadar gider, scope döner

scoped11 = scopeH.resolve(IScopedService)
scoped12 = scopeH.resolve(IScopedService)

print(scoped11 is scoped12)           # True
print(id(scoped11))
print(id(scoped12))
print("Scoped Test (scoped11 is not scoped12):", scoped11 is not scoped12)  # False(aynı scope'larda farklı nesneler)
next(scope_gen, None)  # 🔹 Bu satır scope’u otomatik kapatır
print("--------------------klasik yöntem--------------------------------------")
with container.create_scope() as scopeM:
    scoped13 = scopeM.resolve(IScopedService)
    scoped14 = scopeM.resolve(IScopedService)
    print(id(scoped13))
    print(id(scoped14))
    print("Aynı scope:", scoped13 is scoped14)
print("-----------------main_scoped kullanım---------------------------------")
s15 = container.resolve(IScopedService)
s16 = container.resolve(IScopedService)
print(id(s15))
print(id(s16))
print("Scoped Test (scoped15 is not scoped16):", s15 is not s16)  # False(aynı scope'larda farklı nesneler)
print("----------------------------------------------------------")
scoped_Instance=Scoped_Instance()
scoped_Instance.scope_method()
