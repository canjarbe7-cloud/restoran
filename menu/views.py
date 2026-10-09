from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import Taom, Kategoriya, Buyurtma
import threading


def send_telegram(text):
    """Telegram botga xabar yuborish (fon oqimida)"""
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_ADMIN_CHAT_ID
    if not token or not chat_id:
        return

    def _send():
        try:
            import urllib.request, urllib.parse, json
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = urllib.parse.urlencode({
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML',
            }).encode()
            urllib.request.urlopen(url, data, timeout=5)
        except Exception:
            pass

    threading.Thread(target=_send, daemon=True).start()


def menu(request):
    kategoriyalar = Kategoriya.objects.prefetch_related('taomlar').all()
    taomlar = Taom.objects.filter(mavjud=True).select_related('kategoriya')
    tanlangan_kat = request.GET.get('kategoriya')
    if tanlangan_kat:
        taomlar = taomlar.filter(kategoriya__id=tanlangan_kat)
    return render(request, 'menu/menu.html', {
        'taomlar': taomlar,
        'kategoriyalar': kategoriyalar,
        'tanlangan_kat': tanlangan_kat,
    })


@login_required
def buyurtma(request, taom_id):
    taom = get_object_or_404(Taom, id=taom_id, mavjud=True)
    if request.method == 'POST':
        mijoz = request.POST.get('mijoz', '').strip()
        telefon = request.POST.get('telefon', '').strip()
        manzil = request.POST.get('manzil', '').strip()
        izoh = request.POST.get('izoh', '').strip()
        miqdor = int(request.POST.get('miqdor', 1))

        if not mijoz or not telefon:
            messages.error(request, "Ism va telefon raqamini kiriting!")
            return render(request, 'menu/buyurtma.html', {'taom': taom})

        if miqdor < 1:
            miqdor = 1

        b = Buyurtma.objects.create(
            foydalanuvchi=request.user,
            taom=taom,
            mijoz=mijoz,
            telefon=telefon,
            manzil=manzil,
            izoh=izoh,
            miqdor=miqdor,
        )

        # Telegram xabari
        msg = (
            f"🍽️ <b>YANGI BUYURTMA #{b.id}</b>\n\n"
            f"👤 Mijoz: {mijoz}\n"
            f"📱 Telefon: {telefon}\n"
            f"🍴 Taom: {taom.nom} x{miqdor}\n"
            f"💰 Jami: {b.jami_narx_formatted()}\n"
            f"📍 Manzil: {manzil or '—'}\n"
            f"📝 Izoh: {izoh or '—'}"
        )
        send_telegram(msg)

        messages.success(request, f"✅ Buyurtmangiz qabul qilindi! #{b.id}")
        return redirect('mening_buyurtmalarim')

    return render(request, 'menu/buyurtma.html', {'taom': taom})


@login_required
def mening_buyurtmalarim(request):
    buyurtmalar = Buyurtma.objects.filter(
        foydalanuvchi=request.user
    ).select_related('taom')
    return render(request, 'menu/mening_buyurtmalarim.html', {
        'buyurtmalar': buyurtmalar
    })
