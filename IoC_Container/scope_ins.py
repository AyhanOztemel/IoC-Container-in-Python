
from register import container
from transient_ins import Transient_instance
from register import IScopedService,Abs_SingletonService

class Scoped_Instance:
    def __init__(self):
        print("-----------------scpoe_ins.py----------------------------------")
        # 6. Scoped Test
        with container.create_scope() as scopeX:
            self.scoped1 = scopeX.resolve(IScopedService)
            self.scoped2 = scopeX.resolve(IScopedService)
            self.scoped3 = scopeX.resolve(IScopedService)
        with container.create_scope() as scopeY:
            self.scoped4 = scopeY.resolve(IScopedService)
            self.scoped5 = scopeY.resolve(IScopedService)
            self.scoped6 = scopeY.resolve(IScopedService)

    def scope_method(self):
        print("Scoped Test (self.scoped1 is self.scoped2):", self.scoped1 is self.scoped2 is self.scoped3)  # True (Aynı scope içinde aynı nesne)
        print(self.scoped1.process())  # "Scoped İşlendi"
        print(id(self.scoped1))
        print(id(self.scoped2))
        print(id(self.scoped3))
        print(id(self.scoped4))
        print(id(self.scoped5))
        print(id(self.scoped6))
        #yeni scope
        
        with container.create_scope() as scopeZ:
            self.scoped7 = scopeZ.resolve(IScopedService)
            self.scoped8 = scopeZ.resolve(IScopedService)

        print("Scoped Test (self.scoped2 is not self.scoped7):", self.scoped2 is not self.scoped7)  # True(Farklı scope'larda farklı nesneler)
        print("Scoped Test (self.scoped7 is not self.scoped8):", self.scoped7 is not self.scoped8)  # False(aynı scope'larda farklı nesneler)

        print("---------------scpoe_ins.py--------------------------------")
        # 5. Singleton Test
        self.singleton1 = container.resolve(Abs_SingletonService)
        self.singleton2 = container.resolve(Abs_SingletonService)
        self.singleton3 = container.resolve(Abs_SingletonService)

        print("Singleton Test:", self.singleton1 is self.singleton2 is self.singleton3)  # True (Aynı nesne)
        print(self.singleton1.process())  # "Singleton İşlendi"
        print(id(self.singleton1))
        print(id(self.singleton2))
        print(id(self.singleton3))
        print("----------------------------------------------------------")
        transient_instance=Transient_instance()
        transient_instance.transient_method()
