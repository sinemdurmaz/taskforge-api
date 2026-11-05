# 📋 TaskForge — Görev & Sprint Yönetim API'si

**TaskForge**, kurumsal seviyede geliştirilmiş; **Clean Architecture**, **SOLID**, **ACID** prensipleri, **Design Patterns** (Tasarım Kalıpları) ve **Veri Yapıları (Data Structures)** üzerine inşa edilmiş modern bir Görev ve Proje Yönetimi RESTful API'sidir.

---

## 🏛️ Mimari Katmanlar (Layered Architecture)

Bu projede kodlar tek bir dosyada değil, **Sorumlulukların Ayrılması (Separation of Concerns)** ilkesine uygun katmanlarda yaşar:

* **`core/`:** Sistem ayarları, güvenlik (JWT, Argon2) ve veritabanı motoru.
* **`models/`:** Veritabanı tabloları (Entities) ve veri aktarım şablonları (DTO'lar).
* **`repositories/`:** **[Repository Pattern]** Veritabanı ile konuşan ve sorguları soyutlayan katman.
* **`services/`:** **[Business Logic & ACID]** İş kuralları, transaction yönetimi ve algoritmalar.
* **`api/`:** **[Controller / Routers]** FastAPI yönlendirmeleri ve HTTP uç noktaları.

---

## 🧩 Uygulanan Prensipler ve Tasarım Kalıpları

* **SOLID:** Single Responsibility, Open/Closed, Dependency Inversion
* **Design Patterns:** Repository Pattern, State Pattern, Factory Pattern, Dependency Injection
* **ACID Transactions:** Veri bütünlüğü ve Rollback güvencesi
* **Data Structures:** Priority Queue (Heap), Hash Set ($O(1)$ lookup), Ağaç (Tree) Hiyerarşisi

---

## 🛠️ Teknolojiler

* Python 3.11+
* FastAPI & Uvicorn
* SQLModel (SQLAlchemy ORM)
* SQLite / PostgreSQL
* Pwdlib (Argon2) & PyJWT
* Pytest (TDD)
