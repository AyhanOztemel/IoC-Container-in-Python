# IoC Container Örneği (Python)

Bu depo, Python’da **IoC (Inversion of Control) Container** yaklaşımını kullanarak **Singleton**, **Scoped** ve **Transient** yaşam döngülerini göstermektedir. Örnek kod, `ioc_container.Container` sınıfını kullanır ve servislerin nasıl **kayıt** edildiğini ve **çözümlendiğini (resolve)** adım adım demonstrasyonlarla açıklar.

> Not: Örnek dosya, depo kökünde bir `ioc_container.py` (veya eşdeğeri) bekler. Aşağıdaki komutlar bu sınıfın mevcut olduğu varsayımıyla gösterilir.

---

## 📁 Proje Yapısı (Önerilen)

```
.
├── ioc_container.py         # IoC Container implementasyonu (senin Container sınıfın)
├── example.py               # Aşağıdaki örnek akış (yüklü dosyadan uyarlanmıştır)
└── README.md
```

`example.py` içinde yer alan başlıca bileşenler:
- `ISingletonService`, `IScopedService`, `ITransientService`: Soyut servis arayüzleri (ABC).
- `SingletonService`, `ScopedService`, `TransientService`: Somut implementasyonlar.
- `Container`: Kayıt/çözümleme ve scope yönetimi.

---

## 🚀 Kurulum

1) Python 3.10+ önerilir.
2) Depoyu klonla veya dosyaları indir:
```bash
git clone <repo-url>
cd <repo-folder>
```
3) (İsteğe bağlı) Sanal ortam oluştur:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

Herhangi bir ek bağımlılık yoktur; standart kütüphane yeterlidir.

---

## 🧩 Servis Yaşam Döngüleri

### 1) Singleton
- Uygulama ömrü boyunca **tek bir örnek** tutulur; her çözümlemede aynı nesne döner.
```python
container.register_singleton(ISingletonService, SingletonService)
a = container.resolve(ISingletonService)
b = container.resolve(ISingletonService)
assert a is b
```

### 2) Scoped
- **Scope** başına tek örnek tutulur. Aynı scope içinde aynı nesne, farklı scopelarda farklı nesne döner.
```python
container.register_scoped(IScopedService, ScopedService)
with container.create_scope() as scope:
    s1 = scope.resolve(IScopedService)
    s2 = scope.resolve(IScopedService)
    assert s1 is s2        # aynı scope
with container.create_scope() as scope2:
    s3 = scope2.resolve(IScopedService)
    assert s1 is not s3    # farklı scope
```

### 3) Transient
- **Her çözümlemede yeni bir örnek** oluşturulur.
```python
container.register_transient(ITransientService, TransientService)
t1 = container.resolve(ITransientService)
t2 = container.resolve(ITransientService)
assert t1 is not t2
```

---

## 📌 Örnek Akış (example.py)

Aşağıdaki akış, yüklü dosyanın sadeleştirilmiş bir versiyonudur. `ioc_container.py` mevcutsa doğrudan çalıştırabilirsiniz.

```python
from abc import ABC, abstractmethod
from ioc_container import Container

# 1) Arayüzler
class ISingletonService(ABC):
    @abstractmethod
    def process(self): ...

class IScopedService(ABC):
    @abstractmethod
    def process(self): ...

class ITransientService(ABC):
    @abstractmethod
    def process(self): ...

# 2) Implementasyonlar
class SingletonService(ISingletonService):
    def process(self): return "Singleton İşlendi"

class ScopedService(IScopedService):
    def process(self): return "Scoped İşlendi"

class TransientService(ITransientService):
    def process(self): return "Transient İşlendi"

# 3) Container
container = Container(strict_interfaces=True)

# 4) Kayıtlar
container.register_singleton(ISingletonService, SingletonService)
container.register_scoped(IScopedService, ScopedService)
container.register_transient(ITransientService, TransientService)

# 5) Singleton Test
s1 = container.resolve(ISingletonService)
s2 = container.resolve(ISingletonService)
print("Singleton Test:", s1 is s2)                # True
print(s1.process())                               # "Singleton İşlendi"

# 6) Scoped Test
with container.create_scope() as scope1:
    sc1 = scope1.resolve(IScopedService)
    sc2 = scope1.resolve(IScopedService)
print("Scoped Test (Aynı Scope):", sc1 is sc2)    # True
print(sc1.process())                              # "Scoped İşlendi"

with container.create_scope() as scope2:
    sc3 = scope2.resolve(IScopedService)
print("Scoped Test (Farklı Scope):", sc1 is not sc3)  # True

# 7) Transient Test
t1 = container.resolve(ITransientService)
t2 = container.resolve(ITransientService)
print("Transient Test:", t1 is not t2)            # True
print(t1.process())                               # "Transient İşlendi"
```

Çalıştırmak için:
```bash
python example.py
```

Beklenen çıktı (örnek):

```
Singleton Test: True
Singleton İşlendi
Scoped Test (Aynı Scope): True
Scoped İşlendi
Scoped Test (Farklı Scope): True
Transient Test: True
Transient İşlendi
```

---

## 🧠 İpuçları ve En İyi Uygulamalar
- **`strict_interfaces=True`** ile Container, sadece arayüz–implementasyon eşleşmelerine izin verir; yanlış kayıtları erken yakalarsın.
- Scoped servisler için **`with container.create_scope()`** kullanımı sızıntıları engeller.
- Transient servisleri **hafif** ve **durumsuz** tutmak performans/temizlik için faydalıdır.

---

## 📝 Lisans
Tüm örnekler eğitim amaçlıdır. İstediğiniz gibi kullanıp genişletebilirsiniz.
