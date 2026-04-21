“””
GoldBot Telegram - Versione senza pandas (Python 3.14 compatibile)
“””

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import requests
from datetime import datetime
import os

TOKEN   = os.environ.get(“TOKEN”, “8214986826:AAE-GawbrfPtCCpDmZsPaeBLrm9US1b1wn4”)
CHAT_ID = “5906253706”

def get_gold_data():
try:
url = “https://query1.finance.yahoo.com/v8/finance/chart/GC=F?interval=15m&range=5d”
headers = {“User-Agent”: “Mozilla/5.0”}
r = requests.get(url, headers=headers, timeout=10)
data = r.json()
closes = [x for x in data[‘chart’][‘result’][0][‘indicators’][‘quote’][0][‘close’] if x is not None]
highs  = [x for x in data[‘chart’][‘result’][0][‘indicators’][‘quote’][0][‘high’]  if x is not None]
lows   = [x for x in data[‘chart’][‘result’][0][‘indicators’][‘quote’][0][‘low’]   if x is not None]
return closes, highs, lows
except Exception as e:
print(f”Errore dati: {e}”)
return None, None, None

def ema(values, period):
k = 2 / (period + 1)
e = [values[0]]
for v in values[1:]:
e.append(v * k + e[-1] * (1 - k))
return e

def rsi(values, period=14):
gains, losses = [], []
for i in range(1, len(values)):
d = values[i] - values[i-1]
gains.append(max(d, 0))
losses.append(max(-d, 0))
if len(gains) < period:
return 50.0
avg_gain = sum(gains[-period:]) / period
avg_loss = sum(losses[-period:]) / period
if avg_loss == 0:
return 100.0
rs = avg_gain / avg_loss
return round(100 - (100 / (1 + rs)), 1)

def atr(highs, lows, closes, period=14):
trs = []
for i in range(1, len(closes)):
tr = max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1]))
trs.append(tr)
return round(sum(trs[-period:]) / period, 2) if trs else 0

def analyze():
closes, highs, lows = get_gold_data()
if not closes or len(closes) < 55:
return None

```
ema20 = ema(closes, 20)
ema50 = ema(closes, 50)
rsi_val = rsi(closes)
atr_val = atr(highs, lows, closes)

# Segnali
ma_buy  = ema20[-2] > ema50[-2] and ema20[-3] <= ema50[-3]
ma_sell = ema20[-2] < ema50[-2] and ema20[-3] >= ema50[-3]

prev_rsi = rsi(closes[:-1])
rsi_buy  = prev_rsi < 30 and rsi_val >= 30
rsi_sell = prev_rsi > 70 and rsi_val <= 70

lookback_h = highs[-22:-2]
lookback_l = lows[-22:-2]
highest = max(lookback_h)
lowest  = min(lookback_l)
bo_buy  = closes[-2] > highest * 1.0005
bo_sell = closes[-2] < lowest  * 0.9995

buy_score  = int(ma_buy)  + int(rsi_buy)  + int(bo_buy)
sell_score = int(ma_sell) + int(rsi_sell) + int(bo_sell)

if   buy_score  >= 2: signal = "📈 BUY"
elif sell_score >= 2: signal = "📉 SELL"
else:                 signal = "⏳ NEUTRO"

rsi_label = "⚡ Ipervenduto" if rsi_val < 30 else ("🔥 Ipercomprato" if rsi_val > 70 else "➡️ Neutro")
trend     = "📈 Rialzista" if ema20[-2] > ema50[-2] else "📉 Ribassista"

return {
    "price":      round(closes[-1], 2),
    "ema20":      round(ema20[-2], 2),
    "ema50":      round(ema50[-2], 2),
    "rsi":        rsi_val,
    "atr":        atr_val,
    "highest":    round(highest, 2),
    "lowest":     round(lowest, 2),
    "signal":     signal,
    "buy_score":  buy_score,
    "sell_score": sell_score,
    "rsi_label":  rsi_label,
    "trend":      trend,
}
```

# ── COMANDI ──────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
keyboard = [
[InlineKeyboardButton(“🔍 Analisi”,      callback_data=“analisi”),
InlineKeyboardButton(“💵 Prezzo”,       callback_data=“prezzo”)],
[InlineKeyboardButton(“🎯 Segnale”,      callback_data=“segnale”),
InlineKeyboardButton(“📈 Trend”,        callback_data=“trend”)],
[InlineKeyboardButton(“⚠️ Livelli”,      callback_data=“livelli”),
InlineKeyboardButton(“❓ Help”,         callback_data=“help”)],
]
await update.message.reply_text(
“🥇 *GoldBot — Segnali Gold*\n\nCiao Ibra! Cosa vuoi vedere?”,
parse_mode=“Markdown”,
reply_markup=InlineKeyboardMarkup(keyboard)
)

async def cmd_analisi(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
msg = await update.message.reply_text(“⏳ Analisi in corso…”)
a = analyze()
if not a:
await msg.edit_text(“❌ Errore dati. Riprova tra poco.”)
return
text = build_analisi(a)
kb = [[InlineKeyboardButton(“🔄 Aggiorna”, callback_data=“analisi”),
InlineKeyboardButton(“🏠 Menu”, callback_data=“menu”)]]
await msg.edit_text(text, parse_mode=“Markdown”, reply_markup=InlineKeyboardMarkup(kb))

async def cmd_segnale(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
a = analyze()
if not a:
await update.message.reply_text(“❌ Errore dati”)
return
await update.message.reply_text(
f”🎯 *SEGNALE GOLD M15*\n{a[‘signal’]}\nPrezzo: ${a[‘price’]}\nBUY:{a[‘buy_score’]}/3 SELL:{a[‘sell_score’]}/3\n🕐 {datetime.now().strftime(’%H:%M’)}”,
parse_mode=“Markdown”
)

async def cmd_prezzo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
closes, _, _ = get_gold_data()
if not closes:
await update.message.reply_text(“❌ Errore dati”)
return
price = round(closes[-1], 2)
prev  = round(closes[-2], 2)
diff  = round(price - prev, 2)
emoji = “📈” if diff >= 0 else “📉”
await update.message.reply_text(
f”💵 *GOLD*\n{emoji} *${price}*\nVariazione: {’+’ if diff>=0 else ‘’}{diff}\n🕐 {datetime.now().strftime(’%H:%M:%S’)}”,
parse_mode=“Markdown”
)

async def cmd_trend(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
a = analyze()
if not a:
await update.message.reply_text(“❌ Errore dati”)
return
await update.message.reply_text(
f”📊 *TREND GOLD*\n{a[‘trend’]}\nEMA20: {a[‘ema20’]}\nEMA50: {a[‘ema50’]}\nRSI: {a[‘rsi’]} {a[‘rsi_label’]}”,
parse_mode=“Markdown”
)

async def cmd_livelli(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
a = analyze()
if not a:
await update.message.reply_text(“❌ Errore dati”)
return
await update.message.reply_text(
f”⚠️ *LIVELLI CHIAVE*\n🔴 Resistenza: *${a[‘highest’]}*\n💵 Prezzo: *${a[‘price’]}*\n🟢 Supporto: *${a[‘lowest’]}*\n📏 ATR: {a[‘atr’]}”,
parse_mode=“Markdown”
)

async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(
“📖 *COMANDI*\n/start /analisi /prezzo /segnale /trend /livelli /help”,
parse_mode=“Markdown”
)

def build_analisi(a):
return (
f”🔍 *ANALISI GOLD M15*\n”
f”━━━━━━━━━━━━━━━━━━\n”
f”💵 Prezzo: *${a[‘price’]}*\n”
f”EMA20: {a[‘ema20’]} | EMA50: {a[‘ema50’]}\n”
f”Trend: {a[‘trend’]}\n”
f”RSI: {a[‘rsi’]} — {a[‘rsi_label’]}\n”
f”🔴 Res: ${a[‘highest’]} | 🟢 Sup: ${a[‘lowest’]}\n”
f”ATR: {a[‘atr’]}\n”
f”━━━━━━━━━━━━━━━━━━\n”
f”🎯 *{a[‘signal’]}*\n”
f”BUY:{a[‘buy_score’]}/3 | SELL:{a[‘sell_score’]}/3\n”
f”🕐 {datetime.now().strftime(’%d/%m %H:%M’)}”
)

# ── BOTTONI ──────────────────────────────

async def button_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()
data  = query.data

```
kb_back = [[InlineKeyboardButton("🔄 Aggiorna", callback_data=data),
            InlineKeyboardButton("🏠 Menu", callback_data="menu")]]

if data == "menu":
    keyboard = [
        [InlineKeyboardButton("🔍 Analisi",  callback_data="analisi"),
         InlineKeyboardButton("💵 Prezzo",   callback_data="prezzo")],
        [InlineKeyboardButton("🎯 Segnale",  callback_data="segnale"),
         InlineKeyboardButton("📈 Trend",    callback_data="trend")],
        [InlineKeyboardButton("⚠️ Livelli",  callback_data="livelli"),
         InlineKeyboardButton("❓ Help",     callback_data="help")],
    ]
    await query.edit_message_text("🥇 *GoldBot — Menu*", parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(keyboard))
    return

a = analyze()
if not a:
    await query.edit_message_text("❌ Errore dati. Riprova.")
    return

if data == "analisi":
    await query.edit_message_text(build_analisi(a), parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(kb_back))
elif data == "prezzo":
    closes, _, _ = get_gold_data()
    price = round(closes[-1], 2)
    diff  = round(closes[-1] - closes[-2], 2)
    emoji = "📈" if diff >= 0 else "📉"
    await query.edit_message_text(
        f"💵 *GOLD*\n{emoji} *${price}*\nVariazione: {'+' if diff>=0 else ''}{diff}\n🕐 {datetime.now().strftime('%H:%M')}",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb_back))
elif data == "segnale":
    await query.edit_message_text(
        f"🎯 *SEGNALE*\n{a['signal']}\n${a['price']}\n🕐 {datetime.now().strftime('%H:%M')}",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb_back))
elif data == "trend":
    await query.edit_message_text(
        f"📊 *TREND*\n{a['trend']}\nEMA20:{a['ema20']} EMA50:{a['ema50']}\nRSI:{a['rsi']} {a['rsi_label']}",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb_back))
elif data == "livelli":
    await query.edit_message_text(
        f"⚠️ *LIVELLI*\n🔴 ${a['highest']}\n💵 ${a['price']}\n🟢 ${a['lowest']}\nATR:{a['atr']}",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb_back))
elif data == "help":
    await query.edit_message_text(
        "📖 /start /analisi /prezzo /segnale /trend /livelli",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Menu", callback_data="menu")]]))
```

# ── MAIN ─────────────────────────────────

def main():
print(“🥇 GoldBot avviato!”)
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler(“start”,   cmd_start))
app.add_handler(CommandHandler(“analisi”, cmd_analisi))
app.add_handler(CommandHandler(“prezzo”,  cmd_prezzo))
app.add_handler(CommandHandler(“segnale”, cmd_segnale))
app.add_handler(CommandHandler(“trend”,   cmd_trend))
app.add_handler(CommandHandler(“livelli”, cmd_livelli))
app.add_handler(CommandHandler(“help”,    cmd_help))
app.add_handler(CallbackQueryHandler(button_callback))
app.run_polling(drop_pending_updates=True)

if **name** == “**main**”:
main()
