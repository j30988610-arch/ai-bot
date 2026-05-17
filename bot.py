import logging
import google.generativeai as genai
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = "8933292637:AAEyGdm88IsFowsMqEwZS2kdlokJj_ox-_I"
GEMINI_KEY = "AIzaSyAxN_AZC-bHn9ZPTbLdBFcF7fst4hCjmfI"
ADMIN_CHAT_ID = 1314440253
PRICE = 35000
PAYME = "5614 6829 1940 6548"
CLICK = "5614 6829 1940 6548"
UZUM = "+998 91 772 72 31"
OWNER = "Rashitkxodjaeva Zuxra"

logging.basicConfig(level=logging.INFO)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")
balances = {}
pending = {}
history = {}
user_lang = {}
tested = set()

TEXTS = {
    "ru": {
        "welcome": "👋 Привет, {name}!\n\n🤖 Я *НейроДетектив*!\n\n📝 Определяю AI-текст\n🖼 Определяю AI-фото\n\n💰 Цена: *{price:,} сум*\n\nНажмите «💳 Купить проверку»!",
        "balance": "💰 *Баланс:* {bal} проверок\n\n{status}",
        "bal_ok": "✅ Можете проверять!",
        "bal_no": "❌ Нажмите Купить проверку",
        "history": "📋 *История:*\n\n{h}",
        "history_empty": "📋 История пуста.",
        "support": "🆘 *Поддержка*\n\nПо вопросам пишите администратору.\n\n💳 Payme: `{payme}`\n💳 Click: `{click}`\n📱 Uzum: `{uzum}`",
        "buy": "💳 *Купить проверку — {price:,} сум*\n\nВыберите оплату:",
        "send_screenshot": "📸 Отправьте скриншот чека.",
        "receipt_received": "✅ Чек получен! Ожидайте 5-15 минут.",
        "no_checks": "❌ Нет проверок! Нажмите «💳 Купить».",
        "analyzing": "🔍 Анализирую...",
        "result_photo": "🖼 *Результат*\n\n{result}\n\n💰 Осталось: *{bal}*",
        "result_text": "📝 *Результат*\n\n{result}\n\n💰 Осталось: *{bal}*",
        "error": "❌ Ошибка. Проверка возвращена.",
        "confirmed": "🎉 *Оплата подтверждена!* Отправьте текст или фото.",
        "rejected": "❌ *Оплата не подтверждена.* Свяжитесь с администратором.",
        "min_chars": "⚠️ Минимум 50 символов.",
        "wait_photo": "📸 Жду скриншот.",
        "choose_lang": "🌐 Выберите язык:",
        "lang_set": "✅ Язык установлен: Русский",
        "test_used": "❌ Вы уже использовали бесплатную проверку.",
        "test_given": "🎁 Вам добавлена 1 бесплатная проверка! Отправьте текст или фото.",
        "buttons": [["🤖 Проверить текст","🖼 Проверить фото"],["💳 Купить проверку","💰 Баланс"],["📋 История","🆘 Поддержка"],["🌐 Язык"]],
    },
    "en": {
        "welcome": "👋 Hi, {name}!\n\n🤖 I'm *NeuroDetective*!\n\n📝 I detect AI-written text\n🖼 I detect AI-generated photos\n\n💰 Price: *{price:,} sum*\n\nPress «💳 Buy check»!",
        "balance": "💰 *Balance:* {bal} checks\n\n{status}",
        "bal_ok": "✅ You can check now!",
        "bal_no": "❌ Press Buy check",
        "history": "📋 *History:*\n\n{h}",
        "history_empty": "📋 History is empty.",
        "support": "🆘 *Support*\n\nContact admin for questions.\n\n💳 Payme: `{payme}`\n💳 Click: `{click}`\n📱 Uzum: `{uzum}`",
        "buy": "💳 *Buy check — {price:,} sum*\n\nChoose payment:",
        "send_screenshot": "📸 Send screenshot of receipt.",
        "receipt_received": "✅ Receipt received! Wait 5-15 minutes.",
        "no_checks": "❌ No checks! Press «💳 Buy».",
        "analyzing": "🔍 Analyzing...",
        "result_photo": "🖼 *Result*\n\n{result}\n\n💰 Remaining: *{bal}*",
        "result_text": "📝 *Result*\n\n{result}\n\n💰 Remaining: *{bal}*",
        "error": "❌ Error. Check returned.",
        "confirmed": "🎉 *Payment confirmed!* Send text or photo.",
        "rejected": "❌ *Payment not confirmed.* Contact admin.",
        "min_chars": "⚠️ Minimum 50 characters.",
        "wait_photo": "📸 Waiting for screenshot.",
        "choose_lang": "🌐 Choose language:",
        "lang_set": "✅ Language set: English",
        "test_used": "❌ You already used your free check.",
        "test_given": "🎁 1 free check added! Send text or photo.",
        "buttons": [["🤖 Check text","🖼 Check photo"],["💳 Buy check","💰 Balance"],["📋 History","🆘 Support"],["🌐 Language"]],
    },
    "uz": {
        "welcome": "👋 Salom, {name}!\n\n🤖 Men *NeyroDetektiv*man!\n\n📝 AI-matnni aniqlayman\n🖼 AI-rasmni aniqlayman\n\n💰 Narxi: *{price:,} so'm*\n\n«💳 Tekshiruv sotib olish» tugmasini bosing!",
        "balance": "💰 *Balans:* {bal} tekshiruv\n\n{status}",
        "bal_ok": "✅ Tekshirishingiz mumkin!",
        "bal_no": "❌ Tekshiruv sotib olish tugmasini bosing",
        "history": "📋 *Tarix:*\n\n{h}",
        "history_empty": "📋 Tarix bo'sh.",
        "support": "🆘 *Qo'llab-quvvatlash*\n\nSavollar uchun adminga yozing.\n\n💳 Payme: `{payme}`\n💳 Click: `{click}`\n📱 Uzum: `{uzum}`",
        "buy": "💳 *Tekshiruv sotib olish — {price:,} so'm*\n\nTo'lov usulini tanlang:",
        "send_screenshot": "📸 Chek skrinshotini yuboring.",
        "receipt_received": "✅ Chek qabul qilindi! 5-15 daqiqa kuting.",
        "no_checks": "❌ Tekshiruv yo'q! «💳 Sotib olish» tugmasini bosing.",
        "analyzing": "🔍 Tahlil qilinmoqda...",
        "result_photo": "🖼 *Natija*\n\n{result}\n\n💰 Qoldi: *{bal}*",
        "result_text": "📝 *Natija*\n\n{result}\n\n💰 Qoldi: *{bal}*",
        "error": "❌ Xatolik. Tekshiruv qaytarildi.",
        "confirmed": "🎉 *To'lov tasdiqlandi!* Matn yoki rasm yuboring.",
        "rejected": "❌ *To'lov tasdiqlanmadi.* Admin bilan bog'laning.",
        "min_chars": "⚠️ Kamida 50 ta belgi.",
        "wait_photo": "📸 Skrinshot kutilmoqda.",
        "choose_lang": "🌐 Tilni tanlang:",
        "lang_set": "✅ Til o'rnatildi: O'zbek",
        "test_used": "❌ Siz allaqachon bepul tekshiruvdan foydalandingiz.",
        "test_given": "🎁 1 ta bepul tekshiruv qo'shildi! Matn yoki rasm yuboring.",
        "buttons": [["🤖 Matn tekshirish","🖼 Rasm tekshirish"],["💳 Tekshiruv sotib olish","💰 Balans"],["📋 Tarix","🆘 Yordam"],["🌐 Til"]],
    }
}

def T(uid, key, **kwargs):
    lang = user_lang.get(uid, "ru")
    text = TEXTS[lang].get(key, "")
    return text.format(**kwargs) if kwargs else text

def KB(uid):
    lang = user_lang.get(uid, "ru")
    return ReplyKeyboardMarkup(TEXTS[lang]["buttons"], resize_keyboard=True)

def spend(uid):
    if balances.get(uid, 0) > 0:
        balances[uid] -= 1
        return True
    return False

def add_history(uid, action):
    if uid not in history: history[uid] = []
    history[uid].append(f"{datetime.now().strftime('%d.%m %H:%M')} — {action}")
    if len(history[uid]) > 10: history[uid] = history[uid][-10:]

async def start(u, c):
    uid = u.effective_user.id
    name = u.effective_user.first_name
    await u.message.reply_text(T(uid,"welcome",name=name,price=PRICE), reply_markup=KB(uid), parse_mode="Markdown")

async def test_cmd(u, c):
    uid = u.effective_user.id
    if uid in tested:
        await u.message.reply_text(T(uid,"test_used"))
        return
    tested.add(uid)
    balances[uid] = balances.get(uid, 0) + 1
    await u.message.reply_text(T(uid,"test_given"))

async def lang_cmd(u, c):
    uid = u.effective_user.id
    btns = [[
        InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"),
        InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz"),
    ]]
    await u.message.reply_text(T(uid,"choose_lang"), reply_markup=InlineKeyboardMarkup(btns))

async def set_lang(u, c):
    q = u.callback_query
    await q.answer()
    uid = u.effective_user.id
    lang = q.data.split("_")[1]
    user_lang[uid] = lang
    await q.edit_message_text(T(uid,"lang_set"))
    await c.bot.send_message(uid, T(uid,"welcome",name=u.effective_user.first_name,price=PRICE), reply_markup=KB(uid), parse_mode="Markdown")

async def balance_cmd(u, c):
    uid = u.effective_user.id
    bal = balances.get(uid, 0)
    status = T(uid,"bal_ok") if bal > 0 else T(uid,"bal_no")
    await u.message.reply_text(T(uid,"balance",bal=bal,status=status), parse_mode="Markdown")

async def history_cmd(u, c):
    uid = u.effective_user.id
    h = history.get(uid, [])
    if h:
        await u.message.reply_text(T(uid,"history",h="\n".join(h)), parse_mode="Markdown")
    else:
        await u.message.reply_text(T(uid,"history_empty"))

async def support_cmd(u, c):
    uid = u.effective_user.id
    await u.message.reply_text(T(uid,"support",payme=PAYME,click=CLICK,uzum=UZUM), parse_mode="Markdown")

async def buy(u, c):
    uid = u.effective_user.id
    btns = [[InlineKeyboardButton("💳 Payme",callback_data="pay_payme"),InlineKeyboardButton("💳 Click",callback_data="pay_click")],[InlineKeyboardButton("📱 Uzum",callback_data="pay_uzum")]]
    await u.message.reply_text(T(uid,"buy",price=PRICE), reply_markup=InlineKeyboardMarkup(btns), parse_mode="Markdown")

async def pay_show(u, c):
    q = u.callback_query
    await q.answer()
    uid = u.effective_user.id
    m = q.data.split("_")[1]
    pending[uid] = {"method": m}
    if m == "payme": txt = f"💳 *Payme*\nКарта: `{PAYME}`\nВладелец: {OWNER}\nСумма: *{PRICE:,} сум*"
    elif m == "click": txt = f"💳 *Click*\nКарта: `{CLICK}`\nВладелец: {OWNER}\nСумма: *{PRICE:,} сум*"
    else: txt = f"📱 *Uzum*\nНомер: `{UZUM}`\nСумма: *{PRICE:,} сум*"
    await q.edit_message_text(txt+"\n\nПосле оплаты 👇", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📸 Оплатил",callback_data=f"sent_{m}")]]), parse_mode="Markdown")

async def pay_sent(u, c):
    q = u.callback_query
    await q.answer()
    uid = u.effective_user.id
    m = q.data.split("_")[1]
    pending[uid] = {"method": m, "wait": True}
    await q.edit_message_text(T(uid,"send_screenshot"))

async def photo(u, c):
    uid = u.effective_user.id
    user = u.effective_user
    if pending.get(uid, {}).get("wait"):
        m = pending[uid].get("method","?").upper()
        del pending[uid]
        await u.message.reply_text(T(uid,"receipt_received"))
        btns = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Подтвердить",callback_data=f"ok_{uid}"),InlineKeyboardButton("❌ Отклонить",callback_data=f"no_{uid}")]])
        try:
            await c.bot.send_message(ADMIN_CHAT_ID,f"💰 *Оплата!*\n👤 {user.full_name}\n🆔 `{uid}`\n💳 {m}\n💵 {PRICE:,} сум",reply_markup=btns,parse_mode="Markdown")
            await c.bot.forward_message(ADMIN_CHAT_ID,u.effective_chat.id,u.message.message_id)
        except Exception as e: logging.error(e)
        return
    if not spend(uid):
        await u.message.reply_text(T(uid,"no_checks"))
        return
    msg = await u.message.reply_text(T(uid,"analyzing"))
    try:
        p = u.message.photo[-1]
        file = await c.bot.get_file(p.file_id)
        img = await file.download_as_bytearray()
        r = model.generate_content(["AI-generated or real photo? Give VERDICT, AI PROBABILITY%, SIGNS, CONCLUSION.",{"mime_type":"image/jpeg","data":bytes(img)}])
        bal = balances.get(uid,0)
        add_history(uid,f"Photo check — {bal} left")
        await msg.edit_text(T(uid,"result_photo",result=r.text,bal=bal), parse_mode="Markdown")
    except Exception as e:
        logging.error(e)
        balances[uid] = balances.get(uid,0)+1
        await msg.edit_text(T(uid,"error"))

async def admin_dec(u, c):
    q = u.callback_query
    if u.effective_user.id != ADMIN_CHAT_ID:
        await q.answer("❌ No access.",show_alert=True); return
    await q.answer()
    parts = q.data.split("_")
    act, tid = parts[0], int(parts[1])
    await q.edit_message_reply_markup(reply_markup=None)
    if act == "ok":
        balances[tid] = balances.get(tid,0)+1
        add_history(tid,"Payment confirmed +1")
        try: await c.bot.send_message(tid, T(tid,"confirmed"), parse_mode="Markdown")
        except: pass
    else:
        try: await c.bot.send_message(tid, T(tid,"rejected"), parse_mode="Markdown")
        except: pass

async def text_handler(u, c):
    uid = u.effective_user.id
    t = u.message.text.strip()
    lang = user_lang.get(uid, "ru")
    all_buttons = []
    for lang_data in TEXTS.values():
        for row in lang_data["buttons"]:
            all_buttons.extend(row)
    all_buttons.extend(["🌐 Язык","🌐 Language","🌐 Til"])
    if t in all_buttons: return
    if pending.get(uid,{}).get("wait"):
        await u.message.reply_text(T(uid,"wait_photo")); return
    if len(t) < 50:
        await u.message.reply_text(T(uid,"min_chars")); return
    if not spend(uid):
        await u.message.reply_text(T(uid,"no_checks")); return
    msg = await u.message.reply_text(T(uid,"analyzing"))
    try:
        r = model.generate_content(f"AI or human wrote this? Give VERDICT, AI PROBABILITY%, CONFIDENCE, SIGNS, CONCLUSION. Text: {t}")
        bal = balances.get(uid,0)
        add_history(uid,f"Text check — {bal} left")
        await msg.edit_text(T(uid,"result_text",result=r.text,bal=bal), parse_mode="Markdown")
    except Exception as e:
        logging.error(e)
        balances[uid] = balances.get(uid,0)+1
        await msg.edit_text(T(uid,"error"))

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test", test_cmd))
    for lang_key in ["ru","en","uz"]:
        for row in TEXTS[lang_key]["buttons"]:
            pass
    app.add_handler(MessageHandler(filters.Regex("💳 Купить проверку|💳 Buy check|💳 Tekshiruv sotib olish"), buy))
    app.add_handler(MessageHandler(filters.Regex("💰 Баланс|💰 Balance|💰 Balans"), balance_cmd))
    app.add_handler(MessageHandler(filters.Regex("📋 История|📋 History|📋 Tarix"), history_cmd))
    app.add_handler(MessageHandler(filters.Regex("🆘 Поддержка|🆘 Support|🆘 Yordam"), support_cmd))
    app.add_handler(MessageHandler(filters.Regex("🌐 Язык|🌐 Language|🌐 Til"), lang_cmd))
    app.add_handler(MessageHandler(filters.Regex("🤖 Проверить текст|🤖 Check text|🤖 Matn tekshirish"), lambda u,c: u.message.reply_text("📝 " + T(u.effective_user.id,"min_chars"))))
    app.add_handler(MessageHandler(filters.Regex("🖼 Проверить фото|🖼 Check photo|🖼 Rasm tekshirish"), lambda u,c: u.message.reply_text("🖼 Send photo:")))
    app.add_handler(CallbackQueryHandler(set_lang, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(pay_show, pattern="^pay_"))
    app.add_handler(CallbackQueryHandler(pay_sent, pattern="^sent_"))
    app.add_handler(CallbackQueryHandler(admin_dec, pattern="^(ok|no)_"))
    app.add_handler(MessageHandler(filters.PHOTO, photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    print("НейроДетектив запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
