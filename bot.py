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

def KB(uid):
    return ReplyKeyboardMarkup([["🤖 Проверить текст","🖼 Проверить фото"],["💳 Купить проверку","💰 Баланс"],["📋 История","🆘 Поддержка"]],resize_keyboard=True)

def spend(uid):
    if balances.get(uid,0)>0:
        balances[uid]-=1
        return True
    return False

def add_history(uid,action):
    if uid not in history: history[uid]=[]
    history[uid].append(f"{datetime.now().strftime('%d.%m %H:%M')} — {action}")
    if len(history[uid])>10: history[uid]=history[uid][-10:]

async def start(u,c):
    name=u.effective_user.first_name
    uid=u.effective_user.id
    await u.message.reply_text(f"👋 Привет, {name}!\n\n🤖 Я *НейроДетектив*!\n\n📝 Определяю AI-текст\n🖼 Определяю AI-фото\n\n💰 Цена: *{PRICE:,} сум*\n\nНажмите «💳 Купить проверку»!",reply_markup=KB(uid),parse_mode="Markdown")

async def balance_cmd(u,c):
    uid=u.effective_user.id
    bal=balances.get(uid,0)
    await u.message.reply_text(f"💰 *Баланс:* {bal} проверок\n\n{'✅ Можете проверять!' if bal>0 else '❌ Нажмите Купить проверку'}",parse_mode="Markdown")

async def history_cmd(u,c):
    uid=u.effective_user.id
    h=history.get(uid,[])
    await u.message.reply_text("📋 *История:*\n\n"+"\n".join(h) if h else "📋 История пуста.",parse_mode="Markdown")

async def support_cmd(u,c):
    await u.message.reply_text(f"🆘 *Поддержка*\n\nПо вопросам пишите администратору.\n\n💳 Payme: `{PAYME}`\n💳 Click: `{CLICK}`\n📱 Uzum: `{UZUM}`",parse_mode="Markdown")

async def buy(u,c):
    btns=[[InlineKeyboardButton("💳 Payme",callback_data="pay_payme"),InlineKeyboardButton("💳 Click",callback_data="pay_click")],[InlineKeyboardButton("📱 Uzum",callback_data="pay_uzum")]]
    await u.message.reply_text(f"💳 *Купить проверку — {PRICE:,} сум*\n\nВыберите оплату:",reply_markup=InlineKeyboardMarkup(btns),parse_mode="Markdown")

async def pay_show(u,c):
    q=u.callback_query
    await q.answer()
    m=q.data.split("_")[1]
    pending[u.effective_user.id]={"method":m}
    if m=="payme": txt=f"💳 *Payme*\nКарта: `{PAYME}`\nВладелец: {OWNER}\nСумма: *{PRICE:,} сум*"
    elif m=="click": txt=f"💳 *Click*\nКарта: `{CLICK}`\nВладелец: {OWNER}\nСумма: *{PRICE:,} сум*"
    else: txt=f"📱 *Uzum*\nНомер: `{UZUM}`\nСумма: *{PRICE:,} сум*"
    await q.edit_message_text(txt+"\n\nПосле оплаты 👇",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📸 Оплатил",callback_data=f"sent_{m}")]]),parse_mode="Markdown")

async def pay_sent(u,c):
    q=u.callback_query
    await q.answer()
    m=q.data.split("_")[1]
    pending[u.effective_user.id]={"method":m,"wait":True}
    await q.edit_message_text("📸 Отправьте скриншот чека.")

async def photo(u,c):
    uid=u.effective_user.id
    user=u.effective_user
    if pending.get(uid,{}).get("wait"):
        m=pending[uid].get("method","?").upper()
        del pending[uid]
        await u.message.reply_text("✅ Чек получен! Ожидайте 5-15 минут.")
        btns=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Подтвердить",callback_data=f"ok_{uid}"),InlineKeyboardButton("❌ Отклонить",callback_data=f"no_{uid}")]])
        try:
            await c.bot.send_message(ADMIN_CHAT_ID,f"💰 *Оплата!*\n👤 {user.full_name}\n🆔 `{uid}`\n💳 {m}\n💵 {PRICE:,} сум",reply_markup=btns,parse_mode="Markdown")
            await c.bot.forward_message(ADMIN_CHAT_ID,u.effective_chat.id,u.message.message_id)
        except Exception as e: logging.error(e)
        return
    if not spend(uid):
        await u.message.reply_text("❌ Нет проверок! Нажмите «💳 Купить».")
        return
    msg=await u.message.reply_text("🔍 Анализирую фото...")
    try:
        p=u.message.photo[-1]
        file=await c.bot.get_file(p.file_id)
        img=await file.download_as_bytearray()
        r=model.generate_content(["AI-генерация или реальное фото? Дай ВЕРДИКТ, ВЕРОЯТНОСТЬ AI%, ПРИЗНАКИ, ВЫВОД.",{"mime_type":"image/jpeg","data":bytes(img)}])
        bal=balances.get(uid,0)
        add_history(uid,f"Фото — осталось {bal}")
        await msg.edit_text(f"🖼 *Результат*\n\n{r.text}\n\n💰 Осталось: *{bal}*",parse_mode="Markdown")
    except Exception as e:
        logging.error(e)
        balances[uid]=balances.get(uid,0)+1
        await msg.edit_text("❌ Ошибка. Проверка возвращена.")

async def admin_dec(u,c):
    q=u.callback_query
    if u.effective_user.id!=ADMIN_CHAT_ID:
        await q.answer("❌ Нет прав.",show_alert=True);return
    await q.answer()
    parts=q.data.split("_")
    act,tid=parts[0],int(parts[1])
    await q.edit_message_reply_markup(reply_markup=None)
    if act=="ok":
        balances[tid]=balances.get(tid,0)+1
        add_history(tid,"Оплата подтверждена +1")
        try: await c.bot.send_message(tid,"🎉 *Оплата подтверждена!* Отправьте текст или фото.",parse_mode="Markdown")
        except: pass
    else:
        try: await c.bot.send_message(tid,"❌ *Оплата не подтверждена.* Свяжитесь с администратором.",parse_mode="Markdown")
        except: pass

async def text_handler(u,c):
    t=u.message.text.strip()
    if t in ["🤖 Проверить текст","🖼 Проверить фото","💳 Купить проверку","💰 Баланс","📋 История","🆘 Поддержка"]: return
    uid=u.effective_user.id
    if pending.get(uid,{}).get("wait"):
        await u.message.reply_text("📸 Жду скриншот.");return
    if len(t)<50:
        await u.message.reply_text("⚠️ Минимум 50 символов.");return
    if not spend(uid):
        await u.message.reply_text("❌ Нет проверок! Нажмите «💳 Купить».");return
    msg=await u.message.reply_text("🔍 Анализирую текст...")
    try:
        r=model.generate_content(f"AI или человек написал? Дай ВЕРДИКТ, ВЕРОЯТНОСТЬ AI%, УРОВЕНЬ УВЕРЕННОСТИ, ПРИЗНАКИ, ВЫВОД. Текст: {t}")
        bal=balances.get(uid,0)
        add_history(uid,f"Текст — осталось {bal}")
        await msg.edit_text(f"📝 *Результат*\n\n{r.text}\n\n💰 Осталось: *{bal}*",parse_mode="Markdown")
    except Exception as e:
        logging.error(e)
        balances[uid]=balances.get(uid,0)+1
        await msg.edit_text("❌ Ошибка. Проверка возвращена.")

def main():
    app=Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(MessageHandler(filters.Regex("^💳 Купить проверку$"),buy))
    app.add_handler(MessageHandler(filters.Regex("^💰 Баланс$"),balance_cmd))
    app.add_handler(MessageHandler(filters.Regex("^📋 История$"),history_cmd))
    app.add_handler(MessageHandler(filters.Regex("^🆘 Поддержка$"),support_cmd))
    app.add_handler(MessageHandler(filters.Regex("^🤖 Проверить текст$"),lambda u,c:u.message.reply_text("📝 Отправьте текст (мин. 50 символов):")))
    app.add_handler(MessageHandler(filters.Regex("^🖼 Проверить фото$"),lambda u,c:u.message.reply_text("🖼 Отправьте фото:")))
    app.add_handler(CallbackQueryHandler(pay_show,pattern="^pay_"))
    app.add_handler(CallbackQueryHandler(pay_sent,pattern="^sent_"))
    app.add_handler(CallbackQueryHandler(admin_dec,pattern="^(ok|no)_"))
    app.add_handler(MessageHandler(filters.PHOTO,photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,text_handler))
    print("НейроДетектив запущен!")
    app.run_polling()

if __name__=="__main__":
    main()
