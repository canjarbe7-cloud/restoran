# 🍽 LazzatHaus — Restoran Buyurtma Tizimi

Django asosida qurilgan to'liq restoran veb-sayti.

## ✨ Imkoniyatlar

- 🎨 **Chiroyli menyu** — kategoriyalar va taomlar kartochkalari
- 🔐 **Ro'yxatdan o'tish** — email/parol yoki Google OAuth2
- 🛒 **Buyurtma berish** — miqdor, manzil, izoh bilan
- 📋 **Buyurtmalar tarixi** — statuslar bilan
- 🤖 **Telegram Bot** — bot orqali ham buyurtma berish
- 📬 **Admin xabarlari** — har yangi buyurtma Telegramga keladi
- 🛠 **Admin panel** — taomlar, kategoriyalar, buyurtmalar boshqaruvi

---

## 🚀 O'rnatish

### 1. Virtual muhit
```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate.bat     # Windows
```

### 2. Kutubxonalar
```bash
pip install -r requirements.txt
```

### 3. .env fayli
```bash
cp .env.example .env
# .env faylini tahrirlang
```

### 4. Ma'lumotlar bazasi
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Ishga tushirish
```bash
python manage.py runserver
```

Sayt: http://127.0.0.1:8000

---

## 🔑 Google OAuth2 sozlash

1. [Google Cloud Console](https://console.cloud.google.com/) ga kiring
2. Yangi loyiha yarating
3. **APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID**
4. Application type: **Web application**
5. Authorized redirect URIs:
   ```
   http://127.0.0.1:8000/accounts/complete/google-oauth2/
   ```
6. Client ID va Secret ni `.env` ga qo'ying

---

## 🤖 Telegram Bot sozlash

1. [@BotFather](https://t.me/BotFather) ga yozing
2. `/newbot` → nom va username bering
3. Token ni `.env` ga qo'ying: `TELEGRAM_BOT_TOKEN=...`
4. Admin chat ID: [@userinfobot](https://t.me/userinfobot) ga yozing
5. `TELEGRAM_ADMIN_CHAT_ID=...` ga qo'ying
6. Botni ishga tushiring:
   ```bash
   python bot/telegram_bot.py
   ```

Bot buyruqlari:
- `/start` — xush kelibsiz
- `/menyu` — barcha taomlar ro'yxati
- `/buyurtma` — buyurtma berish

---

## 🍽 Taom qo'shish

Admin panelga kiring: http://127.0.0.1:8000/admin

1. **Kategoriyalar** → qo'shing (emoji va nom)
2. **Taomlar** → nom, narx, tavsif, rasm, kategoriya

---

## 📁 Loyiha tuzilmasi

```
restoran/
├── core/           # Django sozlamalar
├── menu/           # Asosiy ilova (taomlar, buyurtmalar)
├── accounts/       # Autentifikatsiya
├── bot/            # Telegram bot
├── templates/      # HTML shablonlar
├── requirements.txt
├── .env.example
└── manage.py
```
