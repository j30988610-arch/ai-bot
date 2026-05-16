import logging
import google.generativeai as genai
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = "8933292637:AAEyGdm88IsFowsMqEwZS2kdlokJj_ox-_I"
GEMINI_KEY = "AIzaSyAxN_AZC-bHn9ZPTbLdBFcF7fst4hCjmfI"
ADMIN_CHAT_ID = 1314440253
PAYME = "5614 6829 1940 6548"
CLICK = "5614 6829 1940 6548"
UZUM = "+998 91 772 72 31"
OWNER = "Rashitkxodjaeva Zuxra"

logging.basicConfig(level=logging.INFO)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")
balances = {}
pending = {}
KB = ReplyKeyboardMarkup([["Текст", "Фото"], ["Купить", "Баланс"]], resize_keyboard=True)

def spend(uid):
    if balances.get(uid, 0) > 0:
        balances[uid] -= 1
        return True
    return False

async def start(u, c):
    await u.message.reply_text("НейроДетектив\nЦена: 35000 сум\nНажмите Купить!", reply_markup=KB)

async def balance(u, c):
    await u.message.reply_text(f"Баланс: {balances.get(u.effective_user.id, 0)} проверок")

async def buy(u, c):
    btns = [[InlineKeyboardButton("Payme", callback_data="pay_payme"), InlineKeyboardButton("Click", callback_data="pay_click")], [InlineKeyboardButton("Uzum", callback_data="pay_uzum")]]
    await u.message.reply_text("Выберите оплату:", reply_markup=InlineKeyboardMarkup(btns))

async def pay_show(u, c):
    q = u.callback_query
    await q.answer()
    m = q.data.split("_")[1]
    pending[u.effective_user.id] = {"method": m}
    if m == "payme": txt = f"Payme\n{PAYME}\n{OWNER}\n35000 сум"
    elif m == "click": txt = f"Click\n{CLICK}\n{OWNER}\n35000 сум"
    else: txt = f"Uzum\n{UZUM}\n35000 сум"
    await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Оплатил", callback_data=f"sent_{m}")]]))

async def pay_sent(u, c):
    q = u.callback_query
    await q.answer()
    m = q.data.split("_")[1]
    pending[u.effective_user.id] = {"method": m, "wait": True}
    await q.edit_message_text("Отправьте скриншот чека")

async def photo(u, c):
    uid = u.effective_user.id
    user = u.effective_user
    if pending.get(uid, {}).get("wait"):
        del pending[uid]
        await u.message.reply_text("Чек получен! Ожидайте.")
        btns = InlineKeyboardMarkup([[InlineKeyboardButton("Подтвердить", callback_data=f"ok_{uid}"), InlineKeyboardButton("Отклонить", callback_data=f"no_{uid}")]])
        try:
            await c.bot.forward_message(ADMIN_CHAT_ID, u.effective_chat.id, u.message.message_id)
            await c.bot.send_message(ADMIN_CHAT_ID, f"Оплата!\n{user.full_name}\n{uid}", reply_markup=btns)
        except Exception as e: logging.error(e)
        return
    if not spend(uid):
        await u.message.reply_text("Нет проверок. Купите!")
        return
    msg = await u.message.reply_text("Анализирую...")
    try:
        p = u.message.photo[-1]
        file = await c.bot.get_file(p.file_id)
        img = await file.download_as_bytearray()
        r = model.generate_content(["AI или реальное фото? Дай вердикт и признаки.", {"mime_type": "image/jpeg", "data": bytes(img)}])
        await msg.edit_text(f"Результат:\n{r.text}\nОсталось: {balances.get(uid, 0)}")
    except Exception as e:
        logging.error(e)
        balances[uid] = balances.get(uid, 0) + 1
        await msg.edit_text("Ошибка. Проверка возвращена.")

async def admin(u, c):
    q = u.callback_query
    if u.effective_user.id != ADMIN_CHAT_ID:
        await q.answer("Нет прав", show_alert=True); return
    await q.answer()
    parts = q.data.split("_")
    act, tid = parts[0], int(parts[1])
    await q.edit_message_reply_markup(reply_markup=None)
    if act == "ok":
        balances[tid] = balances.get(tid, 0) + 1
        try: await c.bot.send_message(tid, "Оплата подтверждена! Отправьте текст или фото.")
        except: pass
    else:
        try: await c.bot.send_message(tid, "Оплата не подтверждена.")
        except: pass

async def text(u, c):
    t = u.message.text.strip()
    if t in ["Текст", "Фото", "Купить", "Баланс"]: return
    uid = u.effective_user.id
    if pending.get(uid, {}).get("wait"):
        await u.message.reply_text("Жду скриншот."); return
    if len(t) < 50:
        await u.message.reply_text("Минимум 50 символов."); return
    if not spend(uid):
        await u.message.reply_text("Нет проверок. Купите!"); return
    msg = await u.message.reply_text("Анализирую...")
    try:
        r = model.generate_content(f"AI или человек написал? Дай вердикт, вероятность, признаки. Текст: {t}")
        await msg.edit_text(f"Результат:\n{r.text}\nОсталось: {balances.get(uid, 0)}")
    except Exception as e:
        logging.error(e)
        balances[uid] = balances.get(uid, 0) + 1
        await msg.edit_text("Ошибка. Проверка возвращена.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^Купить$"), buy))
    app.add_handler(MessageHandler(filters.Regex("^Баланс$"), balance))
    app.add_handler(MessageHandler(filters.Regex("^Текст$"), lambda u, c: u.message.reply_text("Отправьте текст:")))
    app.add_handler(MessageHandler(filters.Regex("^Фото$"), lambda u, c: u.message.reply_text("Отправьте фото:")))
    app.add_handler(CallbackQueryHandler(pay_show, pattern="^pay_"))
    app.add_handler(CallbackQueryHandler(pay_sent, pattern="^sent_"))
    app.add_handler(CallbackQueryHandler(admin, pattern="^(ok|no)_"))
    app.add_handler(MessageHandler(filters.PHOTO, photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))
    print("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
