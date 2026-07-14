# Translate.uz — API Hujjatlari

Base URL: `http://<host>/`
Autentifikatsiya: `dj-rest-auth` (JWT, cookie-based) — `Authorization: Bearer <access_token>` yoki `access_token` cookie
Interaktiv hujjatlar: `/swagger/`

> Eslatma: `REST_FRAMEWORK` sozlamasida standart ruxsat `AllowAny` qilib qo'yilgan (`config/settings.py`), shu bilan birga `DEFAULT_AUTHENTICATION_CLASSES` da `dj_rest_auth.jwt_auth.JWTCookieAuthentication` ishlatiladi. Production uchun har bir endpoint darajasida `IsAuthenticated` aniq belgilanishi tavsiya etiladi (hozircha ba'zi view'larda alohida ko'rsatilmagan).

---

## 1. Autentifikatsiya — `dj-rest-auth/`

`dj-rest-auth` kutubxonasi orqali standart endpointlar (login, logout, parolni tiklash) mavjud:

| Method | Endpoint | Tavsif |
|---|---|---|
| POST | `dj-rest-auth/login/` | Email + parol orqali login, JWT access/refresh cookie sifatida qaytariladi |
| POST | `dj-rest-auth/logout/` | Tizimdan chiqish |
| POST | `dj-rest-auth/password/reset/` | Standart parolni tiklash oqimi (kutubxona ichidan) |
| POST | `dj-rest-auth/password/change/` | Parolni almashtirish |

## 2. Ro'yxatdan o'tish va profil boshqaruvi

### Ro'yxatdan o'tish

| Method | Endpoint | So'rov tanasi | Tavsif |
|---|---|---|---|
| POST | `/user/register/` | `first_name, last_name, father_name, email, password, image?, pasport?, sertificate?, diplom?, is_client, born_date` | Yangi **mijoz** hisobini yaratish |
| POST | `/trans/register/` | (yuqoridagi bilan bir xil, `is_translator=True`) | Yangi **tarjimon** hisobini yaratish |
| POST | `/lawyer/register/` | (yuqoridagi bilan bir xil, `is_lawyer=True`) | Yangi **yurist** hisobini yaratish |

> Uchala endpoint bir xil `UserRegisterView` orqali ishlaydi — rol farqi `is_client`/`is_translator`/`is_lawyer` maydonlari orqali belgilanadi.

### Chiqish

| Method | Endpoint |
|---|---|
| POST | `/user/logout/` |
| POST | `/trans/logout/` |
| POST | `/lawyer/logout/` |

### Profil

| Method | Endpoint | Tavsif |
|---|---|---|
| GET/PUT | `/user/user-detail/<id>/` | Mijoz profili (`AccountClientSerializer`) — ism, familiya, tug'ilgan sana, rasm |
| GET/PUT | `/trans/user-detail/<id>/` | Tarjimon profili (`AccountTranslatorSerializer`) — narx, tillar, diplom/sertifikat matni, reyting |
| GET/PUT | `/lawyer/user-detail/<id>/` | Yurist profili (`AccountLawyerSerializer`) — narx, diplom, sertifikat |
| GET | `/trans/def/home` | Barcha tarjimonlar ro'yxati (`GetAccountTranslatorSerializer`) |
| GET | `/lawyer/def/home` | Barcha yuristlar ro'yxati |
| GET/POST | `/page/translators/` | Tarjimonlar bo'yicha to'liq `ModelViewSet` (list/retrieve/create/update/delete) |

### Parolni almashtirish

| Method | Endpoint | So'rov tanasi |
|---|---|---|
| PUT | `/user/change_password/<id>/` | `old_password, new_password, password2` |
| PUT | `/trans/change_password/<id>/` | `old_password, new_password, password2` |
| PUT | `/lawyer/change_password/<id>/` | `old_password, new_password, password2` |

### Parolni tiklash (unutilganda)

| Method | Endpoint | So'rov tanasi | Tavsif |
|---|---|---|---|
| POST | `/request-reset-email/` | `email, redirect_url?` | Tiklash havolasini email orqali yuborish |
| GET | `/password-reset/<uidb64>/<token>/` | — | Havoladagi tokenni tekshirish |
| POST | `/password-reset-complete` | `password, token, uidb64` | Yangi parolni saqlash |

## 3. Buyurtmalar

### Bosh sahifa

| Method | Endpoint | Tavsif |
|---|---|---|
| GET | `/Home/` | Bosh sahifadagi umumiy ma'lumot/aloqa formasi uchun (`Home` modeli) |

### Mijozning tarjima buyurtmasi (`OrderCilent`)

| Method | Endpoint | So'rov tanasi | Tavsif |
|---|---|---|---|
| POST | `/user/order/` | `type_w (lawyer/outlawyer), type_t (prose/frs), from_l, to_l, file_order, pages?, commit?, price?` | Yangi buyurtma yaratish — hujjat turi, manba/maqsad til, fayl |
| GET | `/user/order/get/` | — | Joriy mijozning barcha buyurtmalari ro'yxati |
| GET | `/user/order/detail/<id>/` | — (PATCH: `rate, comment`) | Buyurtma tafsiloti; bajarilgach mijoz baho va izoh qoldirishi mumkin |

### Tarjimon tomonidan bajarish (`TranslatorOrders`)

| Method | Endpoint | So'rov tanasi | Tavsif |
|---|---|---|---|
| GET/PUT | `/trans/order/<id>/` | `file_trans` | Natija faylini yuklash/yangilash |
| GET | `/trans/order/` | — | Tarjimonga tegishli barcha ishlar ro'yxati (`file_trans_size` bilan) |

### Yurist tomonidan bajarish (`LawyerOrders`)

| Method | Endpoint | So'rov tanasi | Tavsif |
|---|---|---|---|
| GET/PUT | `/lawyer/order/<id>/` | `file_lawyer` | Natija faylini yuklash/yangilash |
| GET | `/lawyer/order/` | — | Yuristga tegishli barcha ishlar ro'yxati |

## 4. Bildirishnomalar

Buyurtma yaratilganda yoki natija yuklanganda Django signal orqali avtomatik yaratiladi.

| Method | Endpoint | Tavsif |
|---|---|---|
| GET | `/user/client/notification/` | Mijozning bildirishnomalari ro'yxati |
| GET | `/tanslator/notification/` | Tarjimonning bildirishnomalari ro'yxati |
| GET | `/user/client/notification/<id>/` | Bitta bildirishnoma tafsiloti |
| POST | `/user/client/notification/mark-as-read/` | Mijoz bildirishnomalarini ommaviy o'qilgan deb belgilash |
| GET | `/tanslator/notification/mark-as-read/<id>/` | Tarjimon bildirishnomasini o'qilgan deb belgilash |
| POST | `/tanslator/notification/mark-as-read/` | Tarjimon bildirishnomalarini ommaviy o'qilgan deb belgilash |

Bildirishnoma javobi (`to_representation` orqali generatsiya qilinadi):
```json
{
  "id": 12,
  "title": "Yangi xabar",
  "text": "Sizda someone@example.com tomonidan xabar bor!"
}
```

## 5. Chat — WebSocket

REST orqali chat endpointlari (`chat/urls.py`) hozircha kodda izohga olingan (ishlatilmaydi). Chat faqat WebSocket orqali ishlaydi:

**Ulanish:** `ws://<host>/chat/chat/?token=<jwt_access_token>`

**Serverga yuboriladigan xabar (guruhni tanlash):**
```json
{ "action": "select-group", "group_id": 5 }
```
Javob — tanlangan guruh nomi va shu guruhdagi barcha xabarlar tarixi.

**Serverga yuboriladigan xabar (xabar jo'natish):**
```json
{ "action": "send-message", "group_id": 5, "text": "Salom!" }
```
Xabar bazaga saqlanadi (`Message` modeli) va guruhdagi barcha ulangan foydalanuvchilarga real vaqtda yetkaziladi.

**Ulanish paytida serverdan keladigan boshlang'ich xabar:**
```json
{
  "message": "User connected",
  "user": "3",
  "groups": [ { "id": 5, "name": "...", "translator": 2, "lawyer": 4, "client": 3 } ]
}
```

---

## Autentifikatsiya oqimi

1. `POST /user/register/` (yoki `/trans/register/`, `/lawyer/register/`) → hisob yaratiladi
2. `POST /dj-rest-auth/login/` → email + parol orqali login, JWT `access_token` cookie (`AUTH_COOKIE = 'access_token'`) sifatida o'rnatiladi
3. Keyingi so'rovlarda cookie avtomatik yuboriladi, yoki `Authorization: Bearer <token>` header orqali ham uzatish mumkin
4. WebSocket ulanishida token query-parametr sifatida uzatiladi: `?token=<access_token>`