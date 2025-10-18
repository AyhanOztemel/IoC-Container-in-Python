import inspect
from enum import Enum
from typing import Dict, Any, Type, Callable, Optional, TypeVar
from abc import ABC, ABCMeta
import contextvars
from functools import wraps
import sys
import importlib
import importlib.util
from pathlib import Path

def _all_concrete_subclasses(cls):
    """Tüm concrete subclass'ları bul - derin modül yapısını da tara"""
    seen, out = set(), []
    
    # Önce normal subclass walking
    def walk(c):
        for sc in c.__subclasses__():
            if sc in seen:
                continue
            seen.add(sc)
            if not inspect.isabstract(sc):
                out.append(sc)
            walk(sc)
    
    walk(cls)
    
    # Eğer hiç bulunamadıysa, yüklü modüllerde ara
    if not out:
        cls_name = cls.__name__
        for mod_name, mod in sys.modules.items():
            if not mod or not hasattr(mod, '__file__'):
                continue
            
            try:
                for name, obj in inspect.getmembers(mod, inspect.isclass):
                    if (obj != cls and 
                        issubclass(obj, cls) and 
                        not inspect.isabstract(obj) and
                        obj not in seen):
                        out.append(obj)
                        seen.add(obj)
            except:
                continue
    
    return out

def _deep_module_discovery(root_dir: Path = None):
    """Derin klasör yapılarındaki modülleri keşfet ve yükle"""
    if root_dir is None:
        # Çağrılan dosyanın dizinini bul
        import __main__
        if hasattr(__main__, '__file__'):
            root_dir = Path(__main__.__file__).parent
        else:
            root_dir = Path.cwd()
    else:
        root_dir = Path(root_dir)
    
    # sys.path'e ekle
    root_str = str(root_dir.resolve())
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    
    # Tüm Python dosyalarını bul (sınırsız derinlik)
    py_files = list(root_dir.rglob("*.py"))
    
    # Derinliğe göre sırala
    py_files.sort(key=lambda p: len(p.relative_to(root_dir).parts))
    
    loaded = 0
    for py_file in py_files:
        # Skip edilecek dosyalar
        if (py_file.stem.startswith("__") or 
            py_file.stem.startswith("test_") or
            "py_autowired" in py_file.stem or
            "ioc_container" in py_file.stem or
            py_file.name == "setup.py"):
            continue
        
        # Modül adını oluştur
        try:
            parts = []
            current = py_file.parent
            
            # Dosya adını ekle
            if py_file.stem != "__init__":
                parts.append(py_file.stem)
            
            # Package yapısını bul
            while current >= root_dir and current != current.parent:
                parts.append(current.name)
                current = current.parent
                if current == root_dir:
                    break
            
            parts.reverse()
            module_name = ".".join(parts) if parts else py_file.stem
            
            # Modülü yükle
            if module_name not in sys.modules:
                try:
                    # Önce normal import
                    importlib.import_module(module_name)
                    loaded += 1
                except ImportError:
                    # Doğrudan dosyadan yükle
                    try:
                        spec = importlib.util.spec_from_file_location(module_name, py_file)
                        if spec and spec.loader:
                            module = importlib.util.module_from_spec(spec)
                            sys.modules[module_name] = module
                            spec.loader.exec_module(module)
                            loaded += 1
                    except:
                        pass
        except:
            continue
    
    return loaded

def _guess_impl(service_type):
    """Implementation'ı tahmin et - geliştirilmiş versiyon"""
    # Önce derin modül keşfi yap
    _deep_module_discovery()
    
    # Sonra normal akış
    cands = _all_concrete_subclasses(service_type)
    if not cands:
        # Naming convention ile ara
        sname = service_type.__name__
        possible_names = []
        
        # IService -> Service
        if sname.startswith('I') and len(sname) > 1 and sname[1].isupper():
            base = sname[1:]
            possible_names.extend([
                base,
                f"{base}Impl",
                f"{base}Implementation",
                f"Default{base}",
                f"Concrete{base}"
            ])
        
        # Tüm modüllerde ara
        for mod_name, mod in sys.modules.items():
            if not mod:
                continue
            
            try:
                for name, obj in inspect.getmembers(mod, inspect.isclass):
                    if (name in possible_names and 
                        not inspect.isabstract(obj)):
                        
                        # Interface'i implement ediyor mu kontrol et
                        try:
                            if (hasattr(service_type, '__abstractmethods__') and
                                all(hasattr(obj, method) for method in service_type.__abstractmethods__)):
                                cands.append(obj)
                        except:
                            # Duck typing - method isimleri uyuşuyor mu?
                            service_methods = [m for m in dir(service_type) 
                                             if not m.startswith('_')]
                            if all(hasattr(obj, m) for m in service_methods):
                                cands.append(obj)
            except:
                continue
        
        if not cands:
            return None
    
    # Skorlama ve seçim
    sname = service_type.__name__
    prefs = {sname.lstrip('I'), f"{sname}Impl", f"{sname}Implementation"}
    spkg = (getattr(service_type, "__module__", "") or "").split(".")[0]
    
    def score(c):
        name = c.__name__
        cmod = getattr(c, "__module__", "") or ""
        smod = getattr(service_type, "__module__", "") or ""
        
        # Aynı modüldeyse en yüksek skor
        samemod = 100 if cmod == smod else 0
        
        # Aynı package tree'deyse
        samepkg = 50 if cmod.split(".")[0] == spkg else 0
        
        # Modül derinliği benzerliği
        depth_diff = abs(len(cmod.split(".")) - len(smod.split(".")))
        depth_score = max(0, 20 - depth_diff * 5)
        
        # İsim tercihi
        namepref = 30 if name in prefs else 0
        
        return (samemod, samepkg, depth_score, namepref)
    
    cands.sort(key=score, reverse=True)
    return cands[0]


T = TypeVar('T')

class LifetimeScope(Enum):
    SINGLETON = 1
    SCOPED = 2
    TRANSIENT = 3


class ServiceRegistration:
    def __init__(self, service_type: Type, implementation_type: Optional[Type] = None,
                 factory: Optional[Callable] = None, scope: LifetimeScope = LifetimeScope.TRANSIENT):
        self.service_type = service_type
        self.implementation_type = implementation_type or service_type
        self.factory = factory
        self.scope = scope
        self.instance = None  # sadece SINGLETON için kullanılacak


class ScopeManager:
    def __init__(self):
        self.scoped_instances: Dict[Type, Any] = {}

    def get_or_create_instance(self, registration: ServiceRegistration, container) -> Any:
        if registration.service_type not in self.scoped_instances:
            self.scoped_instances[registration.service_type] = container._create_instance(registration)
        return self.scoped_instances[registration.service_type]

    def dispose(self):
        for instance in self.scoped_instances.values():
            if hasattr(instance, 'dispose') and callable(instance.dispose):
                instance.dispose()
        self.scoped_instances.clear()


class Container:
    def __init__(self, strict_interfaces: bool = False, auto_discover: bool = True):
        self.registrations: Dict[Type, ServiceRegistration] = {}
        self.current_scope: Optional[ScopeManager] = None
        self.strict_interfaces = strict_interfaces
        
        # Ambient scope
        self._ambient_scope_var: contextvars.ContextVar[Optional[ScopeManager]] = \
            contextvars.ContextVar("ambient_scope_var", default=None)
        
        # Auto discovery
        if auto_discover:
            print(f"🔍 Derin modül keşfi başlatılıyor...")
            count = _deep_module_discovery()
            print(f"✅ {count} modül yüklendi")

    def register(self, service_type: Type, implementation_type: Type = None, 
                 scope: LifetimeScope = LifetimeScope.TRANSIENT) -> None:
        """
        Servisi container'a kaydet
        Geriye dönük uyumluluk için orijinal method imzası korundu
        """
        if implementation_type is None:
            if inspect.isabstract(service_type) or (
                hasattr(service_type, '__abstractmethods__') and 
                service_type.__abstractmethods__):
                
                print(f"🔎 {service_type.__name__} için implementation aranıyor...")
                impl = _guess_impl(service_type)
                
                if impl is None:
                    # Son bir kez daha derin keşif yap
                    _deep_module_discovery()
                    impl = _guess_impl(service_type)
                    
                    if impl is None:
                        raise ValueError(f"Otomatik implementation bulunamadı: {service_type.__name__}")
                
                implementation_type = impl
                print(f"✅ Bulunan implementation: {implementation_type.__name__}")
            else:
                if self.strict_interfaces:
                    raise TypeError(f"Somut tip kaydedilemez (strict mod): {service_type.__name__}")
                implementation_type = service_type

        self.registrations[service_type] = ServiceRegistration(
            service_type=service_type,
            implementation_type=implementation_type,
            scope=scope
        )

    def register_singleton(self, service_type: Type, implementation_type: Type = None) -> None:
        """Singleton olarak kaydet - orijinal method"""
        self.register(service_type, implementation_type, LifetimeScope.SINGLETON)

    def register_scoped(self, service_type: Type, implementation_type: Type = None) -> None:
        """Scoped olarak kaydet - orijinal method"""
        self.register(service_type, implementation_type, LifetimeScope.SCOPED)

    def register_transient(self, service_type: Type, implementation_type: Type = None) -> None:
        """Transient olarak kaydet - orijinal method"""
        self.register(service_type, implementation_type, LifetimeScope.TRANSIENT)

    def register_instance(self, service_type: Type, instance: Any) -> None:
        """Instance olarak kaydet - orijinal method"""
        registration = ServiceRegistration(service_type=service_type, scope=LifetimeScope.SINGLETON)
        registration.instance = instance
        self.registrations[service_type] = registration

    def register_factory(self, service_type: Type, factory: Callable, scope: LifetimeScope = LifetimeScope.TRANSIENT) -> None:
        """Factory olarak kaydet - orijinal method"""
        self.registrations[service_type] = ServiceRegistration(
            service_type=service_type,
            factory=factory,
            scope=scope
        )

    def create_scope(self) -> 'Scope':
        """Scope oluştur - orijinal method"""
        return Scope(self)

    def resolve(self, service_type: Type[T]) -> T:
        """Servisi çöz - orijinal method"""
        if service_type not in self.registrations:
            raise KeyError(f"Servis tipi kaydedilmemiş: {service_type.__name__}")
        
        registration = self.registrations[service_type]

        if registration.scope == LifetimeScope.SINGLETON:
            if registration.instance is None:
                registration.instance = self._create_instance(registration)
            return registration.instance

        elif registration.scope == LifetimeScope.SCOPED:
            # Önce with scope kontrol et
            scope_mgr = self.current_scope
            # Yoksa ambient scope'a bak
            if scope_mgr is None:
                scope_mgr = self._ambient_scope_var.get()
                if scope_mgr is None:
                    # İlk kez girildiyse otomatik ambient scope oluştur
                    scope_mgr = ScopeManager()
                    self._ambient_scope_var.set(scope_mgr)
            return scope_mgr.get_or_create_instance(registration, self)

        else:  # TRANSIENT
            return self._create_instance(registration)

    def _create_instance(self, registration: ServiceRegistration) -> Any:
        """Instance oluştur - orijinal method"""
        # SINGLETON için önceden var olan instance kullanılmalı
        if registration.scope == LifetimeScope.SINGLETON and registration.instance is not None:
            return registration.instance

        if registration.factory is not None:
            return registration.factory(self)

        implementation_type = registration.implementation_type
        if hasattr(implementation_type, '__init__'):
            sig = inspect.signature(implementation_type.__init__)
            constructor_params = {}
            for param_name, param in list(sig.parameters.items())[1:]:
                if param.annotation != inspect.Parameter.empty:
                    try:
                        constructor_params[param_name] = self.resolve(param.annotation)
                    except KeyError:
                        if param.default != inspect.Parameter.empty:
                            constructor_params[param_name] = param.default
                        else:
                            raise ValueError(
                                f"'{param_name}' parametresi için servis bulunamadı: {param.annotation}"
                            )
            return implementation_type(**constructor_params)
        return implementation_type()

    def scoped_function(self, fn: Callable) -> Callable:
        """Fonksiyonları otomatik scope içine al - orijinal method"""
        @wraps(fn)
        def wrapper(*args, **kwargs):
            mgr = self._ambient_scope_var.get()
            created_here = False
            if mgr is None:
                mgr = ScopeManager()
                self._ambient_scope_var.set(mgr)
                created_here = True
            try:
                return fn(*args, **kwargs)
            finally:
                if created_here:
                    mgr.dispose()
                    self._ambient_scope_var.set(None)
        return wrapper


class Scope:
    """Scope sınıfı - orijinal yapı korundu"""
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
        return self.container.resolve(service_type)
