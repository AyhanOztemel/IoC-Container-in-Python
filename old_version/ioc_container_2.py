# ioc_container.py

import inspect
from enum import Enum
from typing import Dict, Any, Type, Callable, Optional, TypeVar, Generic

T = TypeVar('T')

class LifetimeScope(Enum):
    """Servis ömür döngüsünü tanımlayan enum sınıfı"""
    SINGLETON = 1  # Her zaman aynı örneği döndürür
    SCOPED = 2     # Aynı scope içerisinde aynı örneği döndürür
    TRANSIENT = 3  # Her istekte yeni bir örnek oluşturur


class ServiceRegistration:
    """Servis kayıtlarını tutan sınıf"""
    def __init__(self, service_type: Type, implementation_type: Optional[Type] = None,
factory: Optional[Callable] = None, scope: LifetimeScope = LifetimeScope.TRANSIENT):
        self.service_type = service_type
        self.implementation_type = implementation_type or service_type
        self.factory = factory
        self.scope = scope
        self.instance = None  # Singleton instance için kullanılır


class ScopeManager:
    """Scope yönetimi için sınıf"""
    def __init__(self):
        self.scoped_instances: Dict[Type, Any] = {}
    
    def get_or_create_instance(self, registration: ServiceRegistration, container) -> Any:
        """Scoped servislerin örneklerini yönetir"""
        if registration.service_type not in self.scoped_instances:
            self.scoped_instances[registration.service_type] = container._create_instance(registration)
        return self.scoped_instances[registration.service_type]

    def dispose(self):
        """Scope sonlandırıldığında çağrılır"""
        for instance in self.scoped_instances.values():
            if hasattr(instance, 'dispose') and callable(instance.dispose):
                instance.dispose()
        self.scoped_instances.clear()


class Container:
    """IoC Container sınıfı"""
    def __init__(self):
        self.registrations: Dict[Type, ServiceRegistration] = {}
        self.current_scope: Optional[ScopeManager] = None
    
    def register(self, service_type: Type, implementation_type: Type = None, 
             scope: LifetimeScope = LifetimeScope.TRANSIENT) -> None:
        #"""Bir servis tipini container'a kaydeder"""
        self.registrations[service_type] = ServiceRegistration(
            service_type=service_type,
            implementation_type=implementation_type,
            scope=scope
        )

    def register_singleton(self, service_type: Type, implementation_type: Type = None) -> None:
        """Singleton olarak bir servis kaydeder"""
        self.register(service_type, implementation_type, LifetimeScope.SINGLETON)

    def register_scoped(self, service_type: Type, implementation_type: Type = None) -> None:
        """Scoped olarak bir servis kaydeder"""
        self.register(service_type, implementation_type, LifetimeScope.SCOPED)

    def register_transient(self, service_type: Type, implementation_type: Type = None) -> None:
        """Transient olarak bir servis kaydeder"""
        self.register(service_type, implementation_type, LifetimeScope.TRANSIENT)

    def register_instance(self, service_type: Type, instance: Any) -> None:
        """Önceden oluşturulmuş bir örneği kaydeder (her zaman singleton olarak çalışır)"""
        registration = ServiceRegistration(
            service_type=service_type,
            scope=LifetimeScope.SINGLETON
        )
        registration.instance = instance
        self.registrations[service_type] = registration

    def register_factory(self, service_type: Type, factory: Callable, scope: LifetimeScope = LifetimeScope.TRANSIENT) -> None:
        """Bir fabrika fonksiyonu kullanarak servis kaydeder"""
        self.registrations[service_type] = ServiceRegistration(
            service_type=service_type,
            factory=factory,
            scope=scope
        )

    def create_scope(self) -> 'Scope':
        """Yeni bir servis scope'u oluşturur"""
        return Scope(self)

    def resolve(self, service_type: Type[T]) -> T:
        """Bir servis tipini resolve eder (çözer)"""
        if service_type not in self.registrations:
            raise KeyError(f"Servis tipi kaydedilmemiş: {service_type.__name__}")
        
        registration = self.registrations[service_type]
        
        # Scope'a göre instance oluşturma stratejisi
        if registration.scope == LifetimeScope.SINGLETON:
            if registration.instance is None:
                registration.instance = self._create_instance(registration)
            return registration.instance
        
        elif registration.scope == LifetimeScope.SCOPED:
            if self.current_scope is None:
                raise RuntimeError("Scoped servisler için bir scope oluşturulmalıdır.")
            return self.current_scope.get_or_create_instance(registration, self)
        
        else:  # TRANSIENT
            return self._create_instance(registration)

    def _create_instance(self, registration: ServiceRegistration) -> Any:
        """Bir servis örneği oluşturur"""
        if registration.instance is not None:
            return registration.instance
        
        if registration.factory is not None:
            return registration.factory(self)
        
        implementation_type = registration.implementation_type
        
        # Constructor injection için parametreleri oluştur
        if hasattr(implementation_type, '__init__'):
            sig = inspect.signature(implementation_type.__init__)
            constructor_params = {}
            
            for param_name, param in list(sig.parameters.items())[1:]:  # self parametresini atla
                if param.annotation != inspect.Parameter.empty:
                    try:
                        constructor_params[param_name] = self.resolve(param.annotation)
                    except KeyError:
                        # Eğer bir bağımlılık bulunamazsa ve varsayılan değer varsa kullan
                        if param.default != inspect.Parameter.empty:
                            constructor_params[param_name] = param.default
                        else:
                            raise ValueError(f"'{param_name}' parametresi için servis bulunamadı: {param.annotation}")
            
            return implementation_type(**constructor_params)
        
        return implementation_type()


class Scope:
    """Scope yönetimi için context manager sınıfı"""
    def __init__(self, container: Container):
        self.container = container
        self.previous_scope = None
        self.scope_manager = ScopeManager()
    
    def __enter__(self):
        self.previous_scope = self.container.current_scope
        self.container.current_scope = self.scope_manager
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.scope_manager.dispose()
        self.container.current_scope = self.previous_scope

    def resolve(self, service_type: Type[T]) -> T:
        """Scope içerisinde servis çözümleme"""
        return self.container.resolve(service_type)
