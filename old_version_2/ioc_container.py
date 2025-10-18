# ioc_container.py

import inspect
import threading
from enum import Enum
from typing import Dict, Any, Type, Callable, Optional, TypeVar, Generic, Set
from abc import ABC, ABCMeta


def _all_concrete_subclasses(cls):
    seen, out = set(), []
    def walk(c):
        for sc in c.__subclasses__():
            if sc in seen:
                continue
            seen.add(sc)
            if not inspect.isabstract(sc):
                out.append(sc)
            walk(sc)
    walk(cls)
    return out

def _guess_impl(service_type):
    cands = _all_concrete_subclasses(service_type)
    if not cands:
        return None
    sname = service_type.__name__
    prefs = {sname.lstrip('I'), f"{sname}Impl", f"{sname}Implementation"}
    spkg = (getattr(service_type, "__module__", "") or "").split(".")[0]
    def score(c):
        name = c.__name__
        samepkg = int((getattr(c, "__module__", "") or "").split(".")[0] == spkg)
        namepref = 2 if name in prefs else 0
        return (namepref, samepkg)
    cands.sort(key=score, reverse=True)
    return cands[0]


T = TypeVar('T')

class LifetimeScope(Enum):
    """Servis ömür döngüsünü tanımlayan enum sınıfı"""
    SINGLETON = 1  # Her zaman aynı örneği döndürür
    SCOPED = 2     # Aynı scope içerisinde aynı örneği döndürür
    TRANSIENT = 3  # Her istekte yeni bir örnek oluşturur


class ServiceRegistration:
    """Servis kayıtlarını tutan sınıf - Thread-safe"""
    def __init__(self, service_type: Type, implementation_type: Optional[Type] = None,
                 factory: Optional[Callable] = None, scope: LifetimeScope = LifetimeScope.TRANSIENT):
        self.service_type = service_type
        self.implementation_type = implementation_type or service_type
        self.factory = factory
        self.scope = scope
        self.instance = None  # Singleton instance için kullanılır
        self._lock = threading.Lock()  # Thread-safety için lock


class ScopeManager:
    """Scope yönetimi için sınıf - Thread-safe"""
    def __init__(self):
        self.scoped_instances: Dict[Type, Any] = {}
        self._lock = threading.Lock()
    
    def get_or_create_instance(self, registration: ServiceRegistration, container) -> Any:
        """Scoped servislerin örneklerini yönetir - Thread-safe"""
        if registration.service_type not in self.scoped_instances:
            with self._lock:  # Thread-safe instance creation
                if registration.service_type not in self.scoped_instances:
                    self.scoped_instances[registration.service_type] = container._create_instance(registration)
        return self.scoped_instances[registration.service_type]

    def dispose(self):
        """Scope sonlandırıldığında çağrılır"""
        with self._lock:
            for instance in self.scoped_instances.values():
                if hasattr(instance, 'dispose') and callable(instance.dispose):
                    try:
                        instance.dispose()
                    except Exception:
                        pass  # Dispose hatalarını sessizce geç
            self.scoped_instances.clear()

#strict_interfaces: bool = False---> auto_wire ile kullanımda
#strict_interfaces: bool = True----> bağımsız kullanımda
class Container:
    """IoC Container sınıfı - Thread-safe"""
    def __init__(self, strict_interfaces: bool = False):
        self.registrations: Dict[Type, ServiceRegistration] = {}
        self.current_scope: Optional[ScopeManager] = None
        self.strict_interfaces = strict_interfaces
        self._resolving: Set[Type] = set()  # Circular dependency detection
        self._resolve_lock = threading.Lock()  # Thread-safety için
    
    def register(self, service_type: Type, implementation_type: Type = None, 
                 scope: LifetimeScope = LifetimeScope.TRANSIENT) -> None:
        # Sadece soyut üzerinden kayıt istiyorsan:
        if implementation_type is None:
            if inspect.isabstract(service_type):
                impl = _guess_impl(service_type)
                if impl is None:
                    raise ValueError(f"Otomatik implementation bulunamadı: {service_type.__name__}")
                implementation_type = impl
            else:
                if self.strict_interfaces:
                    raise TypeError(f"Somut tip kaydedilemez (strict mod): {service_type.__name__}")
                implementation_type = service_type  # esnek modda somut da kabul

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
        """Bir servis tipini resolve eder (çözer) - Thread-safe"""
        if service_type not in self.registrations:
            raise KeyError(f"Servis tipi kaydedilmemiş: {service_type.__name__}")
        
        # Circular dependency kontrolü
        if service_type in self._resolving:
            raise RuntimeError(f"Circular dependency detected: {service_type.__name__}")
        
        registration = self.registrations[service_type]
        
        # Scope'a göre instance oluşturma stratejisi
        if registration.scope == LifetimeScope.SINGLETON:
            # Double-checked locking pattern
            if registration.instance is None:
                with registration._lock:
                    if registration.instance is None:
                        self._resolving.add(service_type)
                        try:
                            registration.instance = self._create_instance(registration)
                        finally:
                            self._resolving.discard(service_type)
            return registration.instance
        
        elif registration.scope == LifetimeScope.SCOPED:
            if self.current_scope is None:
                raise RuntimeError("Scoped servisler için bir scope oluşturulmalıdır.")
            self._resolving.add(service_type)
            try:
                return self.current_scope.get_or_create_instance(registration, self)
            finally:
                self._resolving.discard(service_type)
        
        else:  # TRANSIENT
            self._resolving.add(service_type)
            try:
                return self._create_instance(registration)
            finally:
                self._resolving.discard(service_type)

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
