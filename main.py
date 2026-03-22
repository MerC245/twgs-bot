import os
import logging
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, filters, ContextTypes
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN      = os.environ.get("BOT_TOKEN")
ADMIN_GROUP_ID = int(os.environ.get("ADMIN_GROUP_ID", "0"))
OWNER_ID       = int(os.environ.get("OWNER_ID", "0"))

PRODUCTS = {
    "mlbb": {
        "name": "💎 Mobile Legends (MLBB)",
        "uid_prompt": "MLBB Player ID နှင့် Server ID ထည့်ပါ\nဥပမာ — 123456789 (1234)",
        "packages": {
            "dia_86":   {"label": "86 Diamonds",         "price": 5300,   "cost": 4834},
            "dia_172":  {"label": "172 Diamonds",        "price": 10500,  "cost": 9197},
            "dia_257":  {"label": "257 Diamonds",        "price": 15500,  "cost": 13378},
            "dia_343":  {"label": "343 Diamonds",        "price": 21000,  "cost": 18018},
            "dia_429":  {"label": "429 Diamonds",        "price": 26500,  "cost": 20906},
            "dia_514":  {"label": "514 Diamonds",        "price": 32000,  "cost": 26767},
            "dia_600":  {"label": "600 Diamonds",        "price": 38000,  "cost": 31391},
            "dia_706":  {"label": "706 Diamonds",        "price": 44000,  "cost": 36192},
            "dia_878":  {"label": "878 Diamonds",        "price": 55000,  "cost": 45391},
            "dia_1049": {"label": "1049 Diamonds",       "price": 66000,  "cost": 54213},
            "dia_1412": {"label": "1412 Diamonds",       "price": 87000,  "cost": 72384},
            "dia_2195": {"label": "2195 Diamonds",       "price": 128000, "cost": 109556},
            "dia_3688": {"label": "3688 Diamonds",       "price": 210000, "cost": 182729},
            "weekly":   {"label": "Weekly Diamond Pass", "price": 6500,   "cost": 5730},
        },
    },
    "pubg": {
        "name": "🔵 PUBG Mobile (UC)",
        "uid_prompt": "PUBG Player ID ထည့်ပါ\nဥပမာ — 5123456789",
        "packages": {
            "uc_60":   {"label": "60 UC",   "price": 5000,   "cost": 3800},
            "uc_120":  {"label": "120 UC",  "price": 10000,  "cost": 7400},
            "uc_385":  {"label": "385 UC",  "price": 27000,  "cost": 21900},
            "uc_660":  {"label": "660 UC",  "price": 43500,  "cost": 35500},
            "uc_720":  {"label": "720 UC",  "price": 49500,  "cost": 40000},
            "uc_985":  {"label": "985 UC",  "price": 65500,  "cost": 54100},
            "uc_2195": {"label": "2195 UC", "price": 132000, "cost": 108000},
        },
    },
    "hok": {
        "name": "⚔️ Honor of Kings (HOK)",
        "uid_prompt": "HOK Player ID ထည့်ပါ\nဥပမာ — HOK123456789",
        "packages": {
            "hok_66":  {"label": "66 Tokens",  "price": 5000,  "cost": 3900},
            "hok_132": {"label": "132 Tokens", "price": 10000, "cost": 7800},
            "hok_330": {"label": "330 Tokens", "price": 25000, "cost": 19500},
            "hok_660": {"label": "660 Tokens", "price": 48000, "cost": 38000},
        },
    },
}

PAYMENT_METHODS = {
    "kbz":  "🏦 KBZPay",
    "wave": "🌊 Wave Money",
    "aya":  "🏧 AYA Pay",
}

PAYMENT_ACCOUNTS = {
    "kbz":  "KBZPay — 09 7XX XXX XXX (Taw Win)",
    "wave": "Wave Money — 09 9XX XXX XXX (Taw Win)",
    "aya":  "AYA Pay — 09 2XX XXX XXX (Taw Win)",
}

CHOOSE_GAME, CHOOSE_PACKAGE, ENTER_UID, CHOOSE_PAYMENT, UPLOAD_SCREENSHOT, CONFIRM_ORDER = range(6)


def get_next_order_id():
    try:
        with open("counter.txt", "r") as f:
            n = int(f.read().strip()) + 1
    except Exception:
        n = 1001
    with open("counter.txt", "w") as f:
        f.write(str(n))
    return f"TWGS-{n}"


def save_order(order):
    try:
        profit = order["price"] - order["cost"]
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        line = (
            f"{order['order_id']},{now},{order['game_name']},"
            f"{order['package_label']},{order['uid']},"
            f"{order['payment_method']},{order['price']},"
            f"{order['cost']},{profit},{order['customer_username']}\n"
        )
        with open("orders.csv", "a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        logger.error(f"Save order error: {e}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    keyboard = [
        [InlineKeyboardButton("💎 Mobile Legends (MLBB)", callback_data="game_mlbb")],
        [InlineKeyboardButton("🔵 PUBG Mobile (UC)",      callback_data="game_pubg")],
        [InlineKeyboardButton("⚔️ Honor of Kings (HOK)",  callback_data="game_hok")],
    ]
    await update.message.reply_text(
        "🎮 *TAW WIN GAMING STORE*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "မင်္ဂလာပါ! လျှင်မြန်စွာ Top-up ဝန်ဆောင်မှု ပေးနေပါသည် 🚀\n\n"
        "👇 *ဂိမ်းတစ်ခု ရွေးချယ်ပါ*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return CHOOSE_GAME


async def choose_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    game_key = query.data.replace("game_", "")
    game = PRODUCTS[game_key]
    context.user_data["game_key"] = game_key
    context.user_data["game_name"] = game["name"]

    pkgs = list(game["packages"].items())
    keyboard = []
    for i in range(0, len(pkgs), 2):
        row = []
        for key, pkg in pkgs[i : i + 2]:
            row.append(
                InlineKeyboardButton(
                    f"{pkg['label']} — {pkg['price']:,} ကျပ်",
                    callback_data=f"pkg_{key}",
                )
            )
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("⬅️ နောက်သို့", callback_data="back_start")])

    await query.edit_message_text(
        f"{game['name']}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👇 *Package တစ်ခု ရွေးချယ်ပါ*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return CHOOSE_PACKAGE


async def choose_package(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pkg_key = query.data.replace("pkg_", "")
    game_key = context.user_data["game_key"]
    pkg = PRODUCTS[game_key]["packages"][pkg_key]
    context.user_data.update(
        {
            "pkg_key": pkg_key,
            "package_label": pkg["label"],
            "price": pkg["price"],
            "cost": pkg["cost"],
        }
    )
    await query.edit_message_text(
        f"✅ *{pkg['label']}* — {pkg['price']:,} ကျပ်\n\n"
        f"📝 {PRODUCTS[game_key]['uid_prompt']}",
        parse_mode="Markdown",
    )
    return ENTER_UID


async def enter_uid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["uid"] = update.message.text.strip()
    keyboard = [
        [InlineKeyboardButton(v, callback_data=f"pay_{k}")]
        for k, v in PAYMENT_METHODS.items()
    ]
    await update.message.reply_text(
        f"✅ Player ID — `{context.user_data['uid']}`\n\n"
        "💳 *ငွေပေးချေမှု နည်းလမ်း ရွေးချယ်ပါ*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return CHOOSE_PAYMENT


async def choose_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pay_key = query.data.replace("pay_", "")
    context.user_data["payment_method"] = PAYMENT_METHODS[pay_key]
    price = context.user_data["price"]
    await query.edit_message_text(
        f"💳 *{PAYMENT_METHODS[pay_key]}*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 ပေးရမည့် ငွေ — *{price:,} ကျပ်*\n\n"
        f"📲 {PAYMENT_ACCOUNTS[pay_key]}\n\n"
        "📸 *ငွေလွှဲပြီးပါက screenshot ပို့ပေးပါ*",
        parse_mode="Markdown",
    )
    return UPLOAD_SCREENSHOT


async def upload_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data["screenshot"] = update.message.photo[-1].file_id
    elif update.message.text and update.message.text.lower() in ["paid", "ပြီးပြီ", "done"]:
        context.user_data["screenshot"] = None
    else:
        await update.message.reply_text(
            "📸 Screenshot ပို့ပေးပါ သို့မဟုတ် *ပြီးပြီ* လို့ ရိုက်ပါ",
            parse_mode="Markdown",
        )
        return UPLOAD_SCREENSHOT

    ud = context.user_data
    keyboard = [
        [
            InlineKeyboardButton("✅ အတည်ပြုမည်", callback_data="confirm_yes"),
            InlineKeyboardButton("❌ ပယ်ဖျက်မည်", callback_data="confirm_no"),
        ]
    ]
    await update.message.reply_text(
        "📋 *အော်ဒါ အသေးစိတ်*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎮 ဂိမ်း — {ud['game_name']}\n"
        f"📦 Package — {ud['package_label']}\n"
        f"🆔 Player ID — `{ud['uid']}`\n"
        f"💳 ငွေပေးချေမှု — {ud['payment_method']}\n"
        f"💰 စုစုပေါင်း — *{ud['price']:,} ကျပ်*\n\n"
        "မှန်ကန်ပါသလား?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return CONFIRM_ORDER


async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "confirm_no":
        await query.edit_message_text(
            "❌ ပယ်ဖျက်လိုက်ပါပြီ။ /start နှိပ်၍ ပြန်စနိုင်သည်။"
        )
        return ConversationHandler.END

    order_id = get_next_order_id()
    ud = context.user_data
    user = query.from_user
    ud["order_id"] = order_id
    ud["customer_id"] = user.id
    ud["customer_username"] = f"@{user.username}" if user.username else user.first_name
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    await query.edit_message_text(
        "🎉 *အော်ဒါ တင်ပြီးပါပြီ!*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔖 Order ID — `{order_id}`\n"
        f"⏰ အချိန် — {now}\n\n"
        "Staff မှ မကြာမီ Top-up လုပ်ပေးပါမည် ✅\n"
        "ပြီးဆုံးပါက message ပြန်ပို့မည်ဖြစ်သည်\n\n"
        "_ပုံမှန် ကြာချိန် — မိနစ် ၅ မှ ၁၅_",
        parse_mode="Markdown",
    )

    admin_msg = (
        f"🔔 *အော်ဒါ အသစ် — {order_id}*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🕐 အချိန် — {now}\n"
        f"🎮 ဂိမ်း — {ud['game_name']}\n"
        f"📦 Package — {ud['package_label']}\n"
        f"💰 ဈေးနှုန်း — {ud['price']:,} ကျပ်\n"
        f"🆔 Player ID — `{ud['uid']}`\n"
        f"💳 ငွေပေးချေမှု — {ud['payment_method']}\n"
        f"👤 Customer — {ud['customer_username']}\n"
        f"📸 Screenshot — {'✅ ပို့ပြီ' if ud.get('screenshot') else '⚠️ မပါ'}"
    )

    admin_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ လက်ခံမည်", callback_data=f"adm_accept_{order_id}_{user.id}"),
                InlineKeyboardButton("🏁 ပြီးပြီ",   callback_data=f"adm_done_{order_id}_{user.id}"),
            ],
            [
                InlineKeyboardButton("❌ Cancel",   callback_data=f"adm_cancel_{order_id}_{user.id}"),
                InlineKeyboardButton("📞 Customer", url=f"tg://user?id={user.id}"),
            ],
        ]
    )

    if ud.get("screenshot"):
        await context.bot.send_photo(
            chat_id=ADMIN_GROUP_ID,
            photo=ud["screenshot"],
            caption=admin_msg,
            parse_mode="Markdown",
            reply_markup=admin_keyboard,
        )
    else:
        await context.bot.send_message(
            chat_id=ADMIN_GROUP_ID,
            text=admin_msg,
            parse_mode="Markdown",
            reply_markup=admin_keyboard,
        )

    context.bot_data[order_id] = dict(ud)
    return ConversationHandler.END


async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split("_")
    action = parts[1]
    order_id = parts[2]
    customer_id = int(parts[3])
    staff = query.from_user.first_name
    now = datetime.datetime.now().strftime("%H:%M")
    orig = query.message.text or query.message.caption or ""

    if action == "accept":
        new_text = orig + f"\n\n⚡ *{staff}* မှ လက်ခံပြီ ({now})"
        new_kb = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🏁 ပြီးပြီ",  callback_data=f"adm_done_{order_id}_{customer_id}"),
                    InlineKeyboardButton("❌ Cancel", callback_data=f"adm_cancel_{order_id}_{customer_id}"),
                ]
            ]
        )
        if query.message.photo:
            await query.edit_message_caption(caption=new_text, parse_mode="Markdown", reply_markup=new_kb)
        else:
            await query.edit_message_text(text=new_text, parse_mode="Markdown", reply_markup=new_kb)
        await context.bot.send_message(
            chat_id=customer_id,
            text=f"⚡ *Order {order_id} လက်ခံပြီ!*\nTop-up လုပ်နေပါသည် — ခဏ စောင့်ပါ 🔄",
            parse_mode="Markdown",
        )

    elif action == "done":
        new_text = orig + f"\n\n🏁 *{staff}* မှ ပြီးစီးပြီ ({now})"
        if query.message.photo:
            await query.edit_message_caption(caption=new_text, parse_mode="Markdown", reply_markup=None)
        else:
            await query.edit_message_text(text=new_text, parse_mode="Markdown", reply_markup=None)

        order_data = context.bot_data.get(order_id, {})
        save_order(order_data)

        await context.bot.send_message(
            chat_id=customer_id,
            text=(
                f"🎉 *Top-up ပြီးပါပြီ!*\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                f"✅ Order {order_id} ပြီးစီးပါပြီ!\n"
                f"🎮 {order_data.get('game_name', '')}\n"
                f"📦 {order_data.get('package_label', '')}\n\n"
                "TAW WIN GAMING ကို ယုံကြည်အားပေးသည့်အတွက် ကျေးဇူးတင်ပါသည် 🙏\n"
                "/start နှိပ်၍ ထပ်မံ order တင်နိုင်ပါသည်"
            ),
            parse_mode="Markdown",
        )

    elif action == "cancel":
        new_text = orig + f"\n\n❌ *{staff}* မှ ပယ်ဖျက်ပြီ ({now})"
        if query.message.photo:
            await query.edit_message_caption(caption=new_text, parse_mode="Markdown", reply_markup=None)
        else:
            await query.edit_message_text(text=new_text, parse_mode="Markdown", reply_markup=None)
        await context.bot.send_message(
            chat_id=customer_id,
            text=(
                f"❌ *Order {order_id} ပယ်ဖျက်ခဲ့သည်*\n\n"
                "Admin ထံ တိုက်ရိုက် ဆက်သွယ်ပါ သို့မဟုတ် /start နှိပ်ပါ"
            ),
            parse_mode="Markdown",
        )


async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    try:
        with open("orders.csv", "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        lines = []

    today = datetime.date.today()
    args = context.args
    filter_type = args[0] if args else "month"
    prefix = today.strftime("%Y-%m-%d") if filter_type == "today" else today.strftime("%Y-%m")
    filtered = [l for l in lines if l.startswith(prefix)]

    if not filtered:
        await update.message.reply_text("📊 Data မရှိသေးပါ")
        return

    total_revenue = 0
    total_profit = 0
    game_profits = {}

    for line in filtered:
        parts = line.strip().split(",")
        if len(parts) >= 9:
            price  = int(parts[6])
            cost   = int(parts[7])
            profit = int(parts[8])
            game   = parts[2]
            total_revenue += price
            total_profit  += profit
            game_profits[game] = game_profits.get(game, 0) + profit

    breakdown = "\n".join([f"  {g}: {p:,} ကျပ်" for g, p in game_profits.items()])
    label = "ဒီနေ့" if filter_type == "today" else today.strftime("%B %Y")

    await update.message.reply_text(
        f"📊 *{label} Report*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📦 Orders — {len(filtered)}\n"
        f"💵 Revenue — {total_revenue:,} ကျပ်\n"
        f"💰 *Profit — {total_profit:,} ကျပ်*\n\n"
        f"ဂိမ်းအလိုက် —\n{breakdown}",
        parse_mode="Markdown",
    )


async def setrate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    args = context.args
    if len(args) < 4:
        await update.message.reply_text(
            "အသုံးပြုပုံ —\n`/setrate mlbb dia_343 21000 18000`",
            parse_mode="Markdown",
        )
        return
    game_key, pkg_key, price, cost = args[0], args[1], int(args[2]), int(args[3])
    if game_key in PRODUCTS and pkg_key in PRODUCTS[game_key]["packages"]:
        old = PRODUCTS[game_key]["packages"][pkg_key]["price"]
        PRODUCTS[game_key]["packages"][pkg_key]["price"] = price
        PRODUCTS[game_key]["packages"][pkg_key]["cost"]  = cost
        await update.message.reply_text(
            f"✅ *Rate ပြောင်းပြီ!*\n{game_key} / {pkg_key}\n"
            f"ရောင်းဈေး: {old:,} → {price:,} ကျပ်",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text("❌ Game သို့မဟုတ် Package မတွေ့ပါ")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ ပယ်ဖျက်လိုက်ပါပြီ။ /start နှိပ်ပါ")
    return ConversationHandler.END


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_GAME:       [CallbackQueryHandler(choose_game,    pattern="^game_")],
            CHOOSE_PACKAGE:    [CallbackQueryHandler(choose_package, pattern="^pkg_")],
            ENTER_UID:         [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_uid)],
            CHOOSE_PAYMENT:    [CallbackQueryHandler(choose_payment, pattern="^pay_")],
            UPLOAD_SCREENSHOT: [
                MessageHandler(filters.PHOTO, upload_screenshot),
                MessageHandler(filters.TEXT & ~filters.COMMAND, upload_screenshot),
            ],
            CONFIRM_ORDER:     [CallbackQueryHandler(confirm_order,  pattern="^confirm_")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^adm_"))
    app.add_handler(CommandHandler("report",  report))
    app.add_handler(CommandHandler("setrate", setrate))

    logger.info("🎮 TWGS Bot စတင်ပြီ...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
