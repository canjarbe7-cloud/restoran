"""
Restoran Telegram Boti
----------------------
Ishga tushirish:
  python bot/telegram_bot.py

Bu bot Django loyihasidan mustaqil ishlaydi.
Mijozlar Telegram orqali menyuni ko'radi va buyurtma beradi.

Sozlash (.env):
  TELEGRAM_BOT_TOKEN=1234567890:ABCDefGHiJKlmNOPqrSTuvWXyZ
  TELEGRAM_ADMIN_CHAT_ID=123456789
"""

import os
import sys
import django
import asyncio
from pathlib import Path

# Django sozlamasini yuklash
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, filters, ContextTypes
)
from django.conf import settings
from menu.models import Taom, Kategoriya, Buyurtma
from django.contrib.auth.models import User

# Conversation states
KAT, TAOM, MIJOZ, TELEFON, CONFIRM = range(5)


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Boshlash"""
    name = update.effective_user.first_name
    text = (
        f"🍽 *LazzatHaus*ga xush kelibsiz, {name}!\n\n"
        "Sifatli taomlar — bizning maqsadimiz.\n\n"
        "Buyurtma berish uchun /buyurtma\n"
        "Menyuni ko'rish uchun /menyu"
    )
    await update.message.reply_text(text, parse_mode='Markdown')


async def menyu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Menyuni ko'rsatish"""
    taomlar = Taom.objects.filter(mavjud=True).select_related('kategoriya')
    if not taomlar.exists():
        await update.message.reply_text("😔 Hozircha menyu bo'sh.")
        return

    # Kategoriyalar bo'yicha guruhlash
    kats = {}
    for t in taomlar:
        k = t.kategoriya.nom if t.kategoriya else "Boshqa"
        if k not in kats:
            kats[k] = []
        kats[k].append(t)

    msg = "🍽 *MENYU*\n\n"
    for kat, taomlar_list in kats.items():
        msg += f"*{kat}*\n"
        for t in taomlar_list:
            msg += f"  • {t.nom} — {t.narx_formatted()}\n"
        msg += "\n"

    msg += "\n/buyurtma — Buyurtma berish"
    await update.message.reply_text(msg, parse_mode='Markdown')


async def buyurtma_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Buyurtma jarayonini boshlash — kategoriya tanlash"""
    kategoriyalar = list(Kategoriya.objects.all())
    if not kategoriyalar:
        # Kategoriyasiz barcha taomlarni ko'rsat
        return await show_taomlar(update, ctx, None)

    keyboard = []
    for kat in kategoriyalar:
        keyboard.append([InlineKeyboardButton(
            f"{kat.emoji} {kat.nom}",
            callback_data=f"kat_{kat.id}"
        )])
    keyboard.append([InlineKeyboardButton("🍽 Barchasi", callback_data="kat_all")])

    await update.message.reply_text(
        "📂 Kategoriyani tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return KAT


async def kat_tanlash(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Kategoriya tanlangandan keyin taomlarni ko'rsatish"""
    query = update.callback_query
    await query.answer()

    kat_data = query.data.replace("kat_", "")
    if kat_data == "all":
        taomlar = list(Taom.objects.filter(mavjud=True))
    else:
        taomlar = list(Taom.objects.filter(mavjud=True, kategoriya__id=int(kat_data)))

    if not taomlar:
        await query.edit_message_text("😔 Bu kategoriyada taom yo'q.")
        return ConversationHandler.END

    ctx.user_data['taomlar'] = {str(t.id): t for t in taomlar}
    keyboard = []
    for t in taomlar:
        keyboard.append([InlineKeyboardButton(
            f"{t.nom} — {t.narx_formatted()}",
            callback_data=f"taom_{t.id}"
        )])

    await query.edit_message_text(
        "🍴 Taomni tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return TAOM


async def taom_tanlash(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Taom tanlash"""
    query = update.callback_query
    await query.answer()

    taom_id = int(query.data.replace("taom_", ""))
    try:
        taom = Taom.objects.get(id=taom_id, mavjud=True)
    except Taom.DoesNotExist:
        await query.edit_message_text("❌ Bu taom mavjud emas.")
        return ConversationHandler.END

    ctx.user_data['taom'] = taom
    await query.edit_message_text(
        f"✅ *{taom.nom}* tanlandi — {taom.narx_formatted()}\n\n"
        f"👤 Ismingizni yozing:",
        parse_mode='Markdown'
    )
    return MIJOZ


async def mijoz_ism(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Mijoz ismini olish"""
    ctx.user_data['mijoz'] = update.message.text.strip()
    await update.message.reply_text("📱 Telefon raqamingizni yozing (+998...):")
    return TELEFON


async def telefon_olish(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Telefon raqamini olish va tasdiqlash"""
    telefon = update.message.text.strip()
    ctx.user_data['telefon'] = telefon

    taom = ctx.user_data['taom']
    mijoz = ctx.user_data['mijoz']

    keyboard = [
        [
            InlineKeyboardButton("✅ Tasdiqlash", callback_data="confirm_yes"),
            InlineKeyboardButton("❌ Bekor", callback_data="confirm_no"),
        ]
    ]
    await update.message.reply_text(
        f"📋 *Buyurtmangiz:*\n\n"
        f"🍴 Taom: {taom.nom}\n"
        f"💰 Narx: {taom.narx_formatted()}\n"
        f"👤 Ism: {mijoz}\n"
        f"📱 Telefon: {telefon}\n\n"
        f"Tasdiqlaysizmi?",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CONFIRM


async def tasdiqlash(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Buyurtmani saqlash"""
    query = update.callback_query
    await query.answer()

    if query.data == "confirm_no":
        await query.edit_message_text("❌ Buyurtma bekor qilindi.")
        return ConversationHandler.END

    taom = ctx.user_data['taom']
    mijoz = ctx.user_data['mijoz']
    telefon = ctx.user_data['telefon']
    tg_user = update.effective_user

    b = Buyurtma.objects.create(
        taom=taom,
        mijoz=mijoz,
        telefon=telefon,
        izoh=f"Telegram orqali (ID: {tg_user.id})",
    )

    # Admin ga xabar
    admin_chat = settings.TELEGRAM_ADMIN_CHAT_ID
    if admin_chat:
        try:
            await ctx.bot.send_message(
                chat_id=admin_chat,
                text=(
                    f"🔔 <b>YANGI BUYURTMA #{b.id}</b>\n\n"
                    f"🍴 {taom.nom}\n"
                    f"💰 {b.jami_narx_formatted()}\n"
                    f"👤 {mijoz}\n"
                    f"📱 {telefon}\n"
                    f"📱 Telegram: @{tg_user.username or '—'}"
                ),
                parse_mode='HTML'
            )
        except Exception:
            pass

    await query.edit_message_text(
        f"🎉 *Buyurtmangiz qabul qilindi!*\n\n"
        f"📋 Buyurtma raqami: #{b.id}\n"
        f"⏱ Tez orada bog'lanamiz!\n\n"
        f"Yana buyurtma: /buyurtma",
        parse_mode='Markdown'
    )
    return ConversationHandler.END


async def bekor(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Bekor qilindi. /start")
    return ConversationHandler.END


def main():
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN sozlanmagan! .env faylini tekshiring.")
        return

    app = Application.builder().token(token).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler('buyurtma', buyurtma_start)],
        states={
            KAT:     [CallbackQueryHandler(kat_tanlash, pattern='^kat_')],
            TAOM:    [CallbackQueryHandler(taom_tanlash, pattern='^taom_')],
            MIJOZ:   [MessageHandler(filters.TEXT & ~filters.COMMAND, mijoz_ism)],
            TELEFON: [MessageHandler(filters.TEXT & ~filters.COMMAND, telefon_olish)],
            CONFIRM: [CallbackQueryHandler(tasdiqlash, pattern='^confirm_')],
        },
        fallbacks=[CommandHandler('bekor', bekor)],
    )

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('menyu', menyu))
    app.add_handler(conv)

    print("🤖 Bot ishga tushdi...")
    app.run_polling()


if __name__ == '__main__':
    main()
