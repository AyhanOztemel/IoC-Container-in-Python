from register import container
from register import ITransientService,Abs_SingletonService

class Transient_instance:
    def __init__(self):
        print("------------transient_ins.py----------------------------------------")
        # 7. Transient Test
        self.transient1 = container.resolve(ITransientService)
        self.transient2 = container.resolve(ITransientService)
        self.transient3 = container.resolve(ITransientService)

    def transient_method(self):
        print("Transient Test:", self.transient1 is not self.transient2 and self.transient2 is not self.transient3)  # True (Her çağrıda yeni nesne)
        print(self.transient1.process())  # "Transient İşlendi"
        print(id(self.transient1))
        print(id(self.transient2))
        print(id(self.transient3))
        print("--------------transient_ins.py----------------------------------")
        # 5. Singleton Test
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
