# Translate.uz — Tarjima va Notarial Xizmatlar Platformasi

Translate.uz — mijoz (client), tarjimon (translator) va yurist/notarius (lawyer) uchun mo'ljallangan **hujjat tarjimasi va tasdiqlash xizmatlari** platformasining backend qismi. Loyiha **Django + Django REST Framework + Django Channels (WebSocket)** asosida qurilgan bo'lib, uch tomonlama ish oqimini (mijoz → tarjimon/yurist → natija) va real vaqtli xabar almashishni birlashtiradi.

## Mundarija

- [Asosiy imkoniyatlar](#asosiy-imkoniyatlar)
- [Texnologiyalar](#texnologiyalar)
- [Arxitektura va ish oqimi](#arxitektura-va-ish-oqimi)
- [Foydalanuvchi rollari](#foydalanuvchi-rollari)
- [Loyiha tuzilishi](#loyiha-tuzilishi)
- [O'rnatish](#ornatish)
- [Muhit o'zgaruvchilari](#muhit-ozgaruvchilari)
- [API hujjatlari](#api-hujjatlari)
- [WebSocket (real vaqtli chat)](#websocket-real-vaqtli-chat)
- [Loyihaning joriy holati](#loyihaning-joriy-holati)
- [Muallif haqida](#muallif-haqida)

## Asosiy imkoniyatlar

- **Uch rolli autentifikatsiya** — mijoz, tarjimon va yurist uchun alohida ro'yxatdan o'tish/profil boshqaruvi (JWT, cookie-based)
- **Hujjatlarni tarjima uchun buyurtma qilish** (`OrderCilent`) — manba/maqsad tili, hujjat turi, sahifalar soni, narx, biriktirilgan fayl
- **Yuridik xizmat buyurtmalari** (`LawyerOrders`) — mijoz va yuristning fayl almashinuvi
- **Tarjimonning bajarilgan ishlari** (`TranslatorOrders`) — natija faylini yuklash, buyurtma hajmi va narxi
- **Bildirishnomalar** — yangi buyurtma tushganda tarjimon/yuristga, natija tayyor bo'lganda mijozga avtomatik bildirishnoma yaratiladi (Django signal orqali)
- **Parolni tiklash oqimi** — email orqali token yuborish, tasdiqlash va yangi parol o'rnatish (mijoz, tarjimon, yurist uchun alohida)
- **Real vaqtli chat** — mijoz, tarjimon va yurist bitta guruh (`Group`) ichida WebSocket orqali xabar almashadi
- **Swagger/OpenAPI hujjatlari** (`drf-yasg`) va Django Jazzmin bilan zamonaviylashtirilgan admin panel

## Texnologiyalar

| Qatlam | Texnologiya |
|---|---|
| Backend framework | Django 4.0, Django REST Framework 3.13 |
| Autentifikatsiya | `dj-rest-auth` (JWT cookie-based), `djangorestframework-simplejwt`, `PyJWT` |
| Real vaqtli aloqa | Django Channels 3.0, Daphne (ASGI), Redis (`channels-redis`) |
| Admin panel | django-jazzmin (zamonaviy Django admin UI) |
| API hujjatlari | drf-yasg (Swagger/OpenAPI) |
| Fayl bilan ishlash | Pillow, fayl kengaytmasi va hajmi validatsiyasi (`validate_file_extension`) |
| Tashqi integratsiya (rejalashtirilgan) | `google-api-python-client` (Google API integratsiyasi uchun asos, hozircha faol foydalanilmagan) |
| CORS | django-cors-headers |

## Arxitektura va ish oqimi

```
                     ┌────────────────────┐
                     │      config         │  ← settings, URL routing, ASGI, JWT WS middleware
                     └──────────┬──────────┘
                                │
                ┌───────────────┼───────────────┐
                │                                 │
             users                              chat
    (autentifikatsiya, rollar,             (Group, Message,
     buyurtmalar, bildirishnoma)           WebSocket consumer)
```

**Tipik ish oqimi:**

1. Mijoz `OrderCilent` orqali hujjatni tarjima/notarial tasdiqlash uchun yuboradi (manba/maqsad til, hujjat turi va fayl bilan)
2. Buyurtma saqlanganda **signal** orqali tegishli tarjimon/yuristga `ClientNotification` avtomatik yaratiladi
3. Tarjimon/yurist ishni bajarib, natija faylini (`TranslatorOrders` / `LawyerOrders`) yuklaydi
4. Natija saqlanganda mijozga `TranslatorNotification` orqali xabar beriladi
5. Jarayon davomida uch tomon (`chat` app'i orqali) real vaqtli WebSocket chatda muloqot qiladi — har bir `Group` bitta buyurtma/ish uchun mijoz, tarjimon va yuristni bog'laydi

## Foydalanuvchi rollari

Yagona `User` modeli (`users/models.py`) uch xil rolni bitta jadvalda `is_client`, `is_translator`, `is_lawyer` boolean maydonlari orqali belgilaydi:

| Rol | Tavsif |
|---|---|
| **Client** (standart) | Hujjatni tarjima/tasdiqlash uchun yuboradi, natijani kutadi, chatda ishtirok etadi |
| **Translator** | Diplom, sertifikat, tillar ro'yxati bilan profil; mijoz buyurtmalarini qabul qilib bajaradi |
| **Lawyer** | Yuridik hujjatlarni ko'rib chiqadi/tasdiqlaydi, mijoz bilan fayl almashadi |

Har bir rol uchun qo'shimcha profil modeli ham mavjud (`Translator`, `Lawyer` — `User`ga `OneToOne` bog'langan).

## Loyiha tuzilishi

```
Translate.uz/
├── config/
│   ├── settings.py         # Django sozlamalari, JWT/CORS/Channels konfiguratsiyasi
│   ├── urls.py               # Asosiy URL marshrutlash
│   ├── middleware.py         # WebSocket uchun custom JWT autentifikatsiya middleware
│   └── asgi.py                # ASGI konfiguratsiyasi (HTTP + WebSocket)
├── users/
│   ├── models.py             # User, Translator, Lawyer, OrderCilent, LawyerOrders,
│   │                          # TranslatorOrders, bildirishnoma modellari
│   ├── views.py               # Ro'yxatdan o'tish, profil, buyurtmalar, parolni tiklash
│   ├── managers.py            # Custom user manager (email asosida autentifikatsiya)
│   └── urls.py
├── chat/
│   ├── models.py              # Group (mijoz+tarjimon+yurist), Message
│   ├── consumers.py            # WebSocket consumer — guruh tanlash, xabar yuborish
│   ├── extra_func.py           # Rolga qarab foydalanuvchining chatlarini olish
│   ├── tokenizator.py          # JWT token generatsiyasi uchun yordamchi (qo'shimcha)
│   └── routing.py               # WebSocket URL marshrutlari
├── dj_rest_auth/              # dj-rest-auth kutubxonasining loyiha ichiga ko'chirilgan nusxasi
├── requirements.txt
└── manage.py
```

## O'rnatish

```bash
git clone https://github.com/Nazimjonovna/Translate.uz.git
cd Translate.uz

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

`.env` fayl yarating (pastdagi bo'limga qarang), so'ng:

```bash
python manage.py migrate
python manage.py createsuperuser
```

Real vaqtli chat uchun Redis kerak:
```bash
docker run -p 6379:6379 redis
```

Serverni ishga tushirish (WebSocket ishlashi uchun ASGI orqali):
```bash
daphne config.asgi:application
```

Swagger: `http://127.0.0.1:8000/swagger/`
Admin panel (Jazzmin): `http://127.0.0.1:8000/admin/`

## Muhit o'zgaruvchilari

> Joriy holatda `SECRET_KEY` `config/settings.py` faylida qattiq yozilgan. Production/ochiq repository uchun quyidagi qiymatlarni `.env` fayliga ko'chirish tavsiya etiladi:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True

REDIS_HOST=127.0.0.1
REDIS_PORT=6379

EMAIL_HOST=smtp.example.com
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
```

## API hujjatlari

Asosiy endpoint guruhlari (to'liq ro'yxat `users/urls.py` va `chat/urls.py` da):

### Autentifikatsiya va profil

| Method | Endpoint | Tavsif |
|---|---|---|
| POST | `/user/register/`, `/trans/register/`, `/lawyer/register/` | Rolga mos ro'yxatdan o'tish |
| POST | `/user/logout/`, `/trans/logout/`, `/lawyer/logout/` | Tizimdan chiqish |
| GET/PUT | `/user/user-detail/<id>/`, `/trans/user-detail/<id>/`, `/lawyer/user-detail/<id>/` | Profil ma'lumotlari |
| GET | `/trans/def/home`, `/lawyer/def/home` | Tarjimon/yurist ro'yxati |
| PUT | `/user/change_password/<id>/`, `/trans/change_password/<id>/`, `/lawyer/change_password/<id>/` | Parolni almashtirish |
| POST | `/request-reset-email/` | Parolni tiklash — email yuborish |
| POST | `/password-reset/<uidb64>/<token>/` | Tiklash tokenini tekshirish |
| POST | `/password-reset-complete` | Yangi parolni o'rnatish |
| POST/GET | `dj-rest-auth/` | `dj-rest-auth` orqali qo'shimcha autentifikatsiya endpointlari (login va h.k.) |

### Buyurtmalar

| Method | Endpoint | Tavsif |
|---|---|---|
| GET | `/Home/` | Bosh sahifa uchun umumiy ma'lumot |
| POST | `/user/order/` | Mijoz tomonidan yangi tarjima buyurtmasi yaratish |
| GET | `/user/order/get/` | Mijozning barcha buyurtmalari |
| GET | `/user/order/detail/<id>/` | Buyurtma tafsiloti |
| GET/PUT | `/trans/order/<id>/` | Tarjimon tomonidan buyurtmani bajarish/natija yuklash |
| GET | `/trans/order/` | Tarjimonga tegishli buyurtmalar ro'yxati |
| GET/PUT | `/lawyer/order/<id>/` | Yurist tomonidan buyurtmani bajarish |
| GET | `/lawyer/order/` | Yuristga tegishli buyurtmalar ro'yxati |

### Bildirishnomalar

| Method | Endpoint | Tavsif |
|---|---|---|
| GET | `/user/client/notification/` | Mijoz bildirishnomalari |
| GET | `/tanslator/notification/` | Tarjimon bildirishnomalari |
| GET/PATCH | `/user/client/notification/<id>/` | Bitta bildirishnomani ko'rish/o'qilgan deb belgilash |
| POST | `/user/client/notification/mark-as-read/` | Mijoz bildirishnomalarini ommaviy o'qilgan qilish |
| GET/PATCH | `/tanslator/notification/mark-as-read/<id>/` | Tarjimon bildirishnomasini o'qilgan deb belgilash |
| POST | `/tanslator/notification/mark-as-read/` | Tarjimon bildirishnomalarini ommaviy o'qilgan qilish |

## WebSocket (real vaqtli chat)

**Ulanish:** `ws://<host>/chat/chat/?token=<jwt_access_token>`

Autentifikatsiya `config/middleware.py` dagi custom `JWTAuthMiddlewareStack` orqali amalga oshiriladi — token query-parametrda uzatiladi va foydalanuvchi email orqali topiladi.

**Mijozdan yuboriladigan amallar (`action`):**

| Action | Tavsif |
|---|---|
| `select-group` | Chat guruhini tanlash — shu guruhdagi barcha xabarlar tarixi qaytariladi |
| `send-message` | Tanlangan guruhga yangi xabar yuborish — barcha guruh a'zolariga real vaqtda yetkaziladi |

Har bir `Group` — bitta buyurtma bo'yicha mijoz, tarjimon va yuristni bog'laydigan uch tomonlama suhbat xonasi.

## Loyihaning joriy holati

Ushbu repozitoriya CV/portfolio uchun ko'rib chiqilganda, quyidagi holatga e'tibor bering — bu ishlab chiqish jarayonidagi (WIP) loyiha:

- `chat/views.py` dagi REST endpointlar (`RoomListView`, `MessageView`, `MessageCreateView`) va `chat/urls.py` dagi marshrutlar hozircha **kodda izohga olingan (commented out)** — chatning asosiy funksionalligi WebSocket consumer (`chat/consumers.py`) orqali ishlaydi, REST orqali emas
- `chat/tokenizator.py` — JWT token yaratish uchun qo'shimcha yordamchi modul, loyihaning asosiy autentifikatsiya oqimida (`dj-rest-auth`) hozircha ishlatilmaydi
- `dj_rest_auth` kutubxonasi ham `requirements.txt` orqali o'rnatiladi, ham loyiha ichiga to'liq nusxa sifatida ko'chirilgan (`dj_rest_auth/` papkasi) — buni kelgusida faqat pip paketi sifatida qoldirib, loyiha ichidan olib tashlash tavsiya etiladi


## Muallif haqida

Ushbu loyiha men tomonimdan uch tomonlama (marketplace) biznes-modelni backend darajasida loyihalash tajribasi sifatida ishlab chiqilgan bo'lib, quyidagi ko'nikmalarni namoyish etadi:

- Bir nechta rolli (client/translator/lawyer) foydalanuvchi tizimini yagona modelda loyihalash
- Django signal'lar orqali avtomatik bildirishnoma tizimini qurish
- WebSocket orqali ko'p tomonlama (group-based) real vaqtli chatni amalga oshirish, shu jumladan custom JWT autentifikatsiya middleware yozish
- Fayl yuklash validatsiyasi (kengaytma, hajm) va media-fayllarni boshqarish
- `dj-rest-auth` va `simplejwt` asosida cookie-based JWT autentifikatsiyani sozlash
- Swagger (drf-yasg) orqali API hujjatlashtirish