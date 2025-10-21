
from abs_services import Abs_SingletonService,IScopedService,ITransientService
#from services  import SingletonService,ScopedService, TransientService
from ioc_container import Container

import services  # ÖNEMLİ: Somut sınıfları belleğe yükler
##Bu sayede container, Abs_SingletonService → SingletonService,
##IScopedService → ScopedService,
##ITransientService → TransientService eşleşmelerini otomatik bulur.

# 3. IoC Container'ı oluştur
container = Container( strict_interfaces= True)
Container._instance = container  # 👈 Eğer ioc_container bağımsız kullanlılacaksa
                                 #resolve yerine static provider method kullanmak istedğimizde
                                 #resolve her seferinde container instance oluşturmak zorunda 

# 4. Servisleri kaydet--> # net ve tartışmasız
##container.register_singleton(Abs_SingletonService, SingletonService)
##container.register_scoped(IScopedService, ScopedService)
##container.register_transient(ITransientService, TransientService)

# 4. Sadece abstract sınıflar register edilse olur
container.register_singleton(Abs_SingletonService) 
container.register_scoped(IScopedService) 
container.register_transient(ITransientService)
