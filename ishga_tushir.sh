#!/bin/bash

# ============================================
#   LazzatHaus — Avtomatik ishga tushirish
# ============================================

echo ""
echo "🍽  LazzatHaus ishga tushmoqda..."
echo "=================================="

# Virtual muhit yaratish (agar yo'q bo'lsa)
if [ ! -d "venv" ]; then
  echo "📦 Virtual muhit yaratilmoqda..."
  python3 -m venv venv
fi

# Virtual muhitni yoqish
source venv/bin/activate

# .env fayl yaratish (agar yo'q bo'lsa)
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "⚙️  .env fayl yaratildi"
fi

# Kutubxonalarni o'rnatish
echo "📥 Kutubxonalar o'rnatilmoqda..."
pip install -r requirements.txt -q

# Migrate
echo "🗄️  Baza sozlanmoqda..."
python3 manage.py migrate -q

# Superuser (agar yo'q bo'lsa)
echo "👤 Admin tekshirilmoqda..."
python3 manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin1234')
    print('✅ Admin yaratildi: login=admin  parol=admin1234')
else:
    print('✅ Admin mavjud')
" 2>/dev/null

echo ""
echo "=================================="
echo "✅ Hammasi tayyor!"
echo ""
echo "🌐 Brauzerda oching:"
echo "   http://127.0.0.1:8000"
echo ""
echo "🔐 Admin panel:"
echo "   http://127.0.0.1:8000/admin"
echo "   Login: admin"
echo "   Parol: admin1234"
echo ""
echo "⛔ To'xtatish uchun: Ctrl+C"
echo "=================================="
echo ""

# Serverni ishga tushirish
python3 manage.py runserver
