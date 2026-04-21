“””
GoldBot Telegram - Versione Cloud (iPad friendly)
Gira su Render.com GRATIS - niente PC, niente MT5
Analisi tecnica via API pubblica (Yahoo Finance / Binance)
“””

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import requests
import pandas as pd
import ta
from datetime import datetime
import asyncio
import os

# ─────────────────────────────────────────

TOKEN   = os.environ.get(“TOKEN”, “8214986826:AAE-GawbrfPtCCpDmZsPaeBLrm9US1b1wn4”)
CHAT_ID = “5906253706”
SYMBOL_YF = “GC=F”   # Gold Futures su Yahoo Finance

# ─────────────────────────────────────────

def get_gold_data():
“”“Scarica dati Gold da Yahoo Finance”””
try:
url = f”https://query1.finance.yahoo.com/v8/finance/chart/{SYMBOL_YF}?interval=15m&range=5d”
headers = {“User-Agent”: “Mozilla/5.0”}
r = requests.get(url, headers=headers, timeout=10)
data = r.json()

```
    timestamps = data['chart']['result'][0]['timestamp']
    closes  = data['chart']['result'][0]['indicators']['quote'][0]['close']
    highs   = data['chart']['result'][0]['indicators']['quote'][0]['high']
    lows    = data['chart']['result'][0]['indicators']['quote'][0]['low']

    df = pd.DataFrame({
        'time':  pd.to_datetime(timestamps, unit='s'),
        'close': closes,
        'high':  highs,
        'low':   lows,
    }).dropna()

    return df
except Exception as e:
    print(f"Errore dati: {e}")
    return None
```

def analyze(df):
“”“Calcola indicatori e genera segnale”””
df[‘ema20’] = df[‘close’].ewm(span=20, adjust=False).mean()
df[‘ema50’] = df[‘close’].ewm(span=50, adjust=False).mean()
df[‘rsi’]   = ta.momentum.RSIIndicator(df[‘close’], window=14).rsi()
df[‘atr’]   = ta.volatility.AverageTrueRange(df[‘high’], df[‘low’], df[‘close’], window=14).average_true_range()

```
row  = df.iloc[-2]
prev = df.iloc[-3]

ma_buy  = (row['ema20'] > row['ema50']) and (prev['ema20'] <= prev['ema50'])
ma_sell = (row['ema20'] < row['ema50']) and (prev['ema20'] >= prev['ema50'])
rsi_buy  = (prev['rsi'] < 30) and (row['rsi'] >= 30)
rsi_sell = (prev['rsi'] > 70) and (row['rsi'] <= 70)

lookback = df.iloc[-22:-2]
highest  = lookback['high'].max()
lowest   = lookback['low'].min()
bo_buy   = row['close'] > highest * 1.0005
bo_sell  = row['close'] < lowest  * 0.9995

buy_score  = int(ma_buy)  + int(rsi_buy)  + int(bo_buy)
sell_score = int(ma_sell) + int(rsi_sell) + int(bo_sell)

if   buy_score  >= 2: signal = "📈 BUY"
elif sell_score >= 2: signal = "📉 SELL"
else:                 signal = "⏳ NEUTRO — aspetta"

rsi_label = "⚡ Ipervenduto" if row['rsi'] < 30 else ("🔥 Ipercomprato" if row['rsi'] > 70 else "➡️ Neutro")
trend     = "📈 Rialzista" if row['ema20'] > row['ema50'] else "📉 Ribassista"

return {
    "price":      round(row['close'], 2),
    "ema20":      round(row['ema20'], 2),
    "ema50":      round(row['ema50'], 2),
    "rsi":        round(row['rsi'], 1),
    "atr":        round(row['atr'], 2),
    "highest":    round(highest, 2),
    "lowest":     round(lowest, 2),
    "signal":     signal,
    "buy_score":  buy_score,
    "sell_score": sell_score,
    "rsi_label":  rsi_label,
    "trend":      trend,
}
```

# ─────────────────────────────────────────

# COMANDI

# ─────────────────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
keyboard = [
[InlineKeyboardButton(“🔍 Analisi ora”,    callback_data=“analisi”),
InlineKeyboardButton(“💵 Prezzo Gold”,    callback_data=“prezzo”)],
[InlineKeyboardButton(“📊 Segnale M15”,    callback_data=“segnale”),
InlineKeyboardButton(“📈 Trend”,          callback_data=“trend”)],
[InlineKeyboardButton(“⚠️ Livelli chiave”, callback_data=“livelli”),
InlineKeyboardButton(“❓ Aiuto”,          callback_data=“help”)],
]
await update.message.reply_text(
“🥇 *GoldBot — Segnali Gold*\n\n”
“Ciao Ibra! Scegli cosa vuoi vedere:”,
parse_mode=“Markdown”,
reply_markup=InlineKeyboardMarkup(keyboard)
)

async def cmd_analisi(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
msg = await update.message.reply_text(“⏳ Analisi in corso…”)
df  = get_gold_data()
if df is None:
await msg.edit_text(“❌ Errore nel recupero dati. Riprova.”)
return
a = analyze(df)
text = (
f”🔍 *ANALISI GOLD (XAU/USD) M15*\n”
f”━━━━━━━━━━━━━━━━━━\n”
f”💵 Prezzo attuale: *${a[‘price’]}*\n”
f”━━━━━━━━━━━━━━━━━━\n”
f”📊 *Moving Average*\n”
f”  EMA20: {a[‘ema20’]}\n”
f”  EMA50: {a[‘ema50’]}\n”
f”  Trend: {a[‘trend’]}\n”
f”━━━━━━━━━━━━━━━━━━\n”
f”📉 *RSI(14)*: {a[‘rsi’]} — {a[‘rsi_label’]}\n”
f”━━━━━━━━━━━━━━━━━━\n”
f”💥 *Livelli Breakout*\n”
f”  🔴 Resistenza: ${a[‘highest’]}\n”
f”  🟢 Supporto:   ${a[‘lowest’]}\n”
f”  📏 ATR:        {a[‘atr’]}\n”
f”━━━━━━━━━━━━━━━━━━\n”
f”🎯 *SEGNALE: {a[‘signal’]}*\n”
f”  BUY score:  {a[‘buy_score’]}/3\n”
f”  SELL score: {a[‘sell_score’]}/3\n”
f”━━━━━━━━━━━━━━━━━━\n”
f”🕐 {datetime.now().strftime(’%d/%m %H:%M’)}”
)
keyboard = [[InlineKeyboardButton(“🔄 Aggiorna”, callback_data=“analisi”),
InlineKeyboardButton(“🏠 Menu”, callback_data=“menu”)]]
await msg.edit_text(text, parse_mode=“Markdown”,
reply_markup=InlineKeyboardMarkup(keyboard))

async def cmd_prezzo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
df = get_gold_data()
if df is None:
await update.message.reply_text(“❌ Errore dati”)
return
price = round(df.iloc[-1][‘close’], 2)
prev  = round(df.iloc[-2][‘close’], 2)
diff  = round(price - prev, 2)
emoji = “📈” if diff >= 0 else “📉”
await update.message.reply_text(
f”💵 *GOLD — Prezzo attuale*\n”
f”━━━━━━━━━━━━━━━━━━\n”
f”{emoji} *${price}*\n”
f”Variazione: {’+’ if diff >= 0 else ‘’}{diff}\n”
f”🕐 {datetime.now().strftime(’%H:%M:%S’)}”,
parse_mode=“Markdown”
)

async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(
“📖 *COMANDI*\n”
“━━━━━━━━━━━━━━━━━━\n”
“/start — Menu principale\n”
“/analisi — Analisi tecnica completa\n”
“/prezzo — Prezzo Gold attuale\n”
“/segnale — Solo il segnale BUY/SELL\n”
“/trend — Trend attuale\n”
“/livelli — Supporti e resistenze\n”
“/help — Questo messaggio”,
parse_mode=“Markdown”
)

async def cmd_segnale(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
df = get_gold_data()
if df is None:
await update.message.reply_text(“❌ Errore dati”)
return
a = analyze(df)
await update.message.reply_text(
f”🎯 *SEGNALE GOLD M15*\n”
f”━━━━━━━━━━━━━━━━━━\n”
f”{a[‘signal’]}\n”
f”Prezzo: ${a[‘price’]}\n”
f”BUY: {a[‘buy_score’]}/3 | SELL: {a[‘sell_score’]}/3\n”
f”🕐 {datetime.now().strftime(’%H:%M’)}”,
parse_mode=“Markdown”
)

async def cmd_trend(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
df = get_gold_data()
if df is None:
await update.message.reply_text(“❌ Errore dati”)
return
a = analyze(df)
await update.message.reply_text(
f”📊 *TREND GOLD*\n”
f”━━━━━━━━━━━━━━━━━━\n”
f”Trend M15: {a[‘trend’]}\n”
f”EMA20: {a[‘ema20’]}\n”
f”EMA50: {a[‘ema50’]}\n”
f”RSI: {a[‘rsi’]} — {a[‘rsi_label’]}”,
parse_mode=“Markdown”
)

async def cmd_livelli(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
df = get_gold_data()
if df is None:
await update.message.reply_text(“❌ Errore dati”)
return
a = analyze(df)
await update.message.reply_text(
f”⚠️ *LIVELLI CHIAVE GOLD*\n”
f”━━━━━━━━━━━━━━━━━━\n”
f”🔴 Resistenza: *${a[‘highest’]}*\n”
f”💵 Prezzo ora: *${a[‘price’]}*\n”
f”🟢 Supporto:   *${a[‘lowest’]}*\n”
f”━━━━━━━━━━━━━━━━━━\n”
f”📏 ATR (volatilità): {a[‘atr’]}”,
parse_mode=“Markdown”
)

# ─────────────────────────────────────────

# CALLBACK BOTTONI

# ─────────────────────────────────────────

async def button_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()
data  = query.data

```
df = get_gold_data()
if df is None:
    await query.edit_message_text("❌ Errore dati. Riprova.")
    return

a = analyze(df)

keyboard_back = [[InlineKeyboardButton("🔄 Aggiorna", callback_data=data),
                  InlineKeyboardButton("🏠 Menu", callback_data="menu")]]

if data == "menu":
    keyboard = [
        [InlineKeyboardButton("🔍 Analisi ora",    callback_data="analisi"),
         InlineKeyboardButton("💵 Prezzo Gold",    callback_data="prezzo")],
        [InlineKeyboardButton("📊 Segnale M15",    callback_data="segnale"),
         InlineKeyboardButton("📈 Trend",          callback_data="trend")],
        [InlineKeyboardButton("⚠️ Livelli chiave", callback_data="livelli"),
         InlineKeyboardButton("❓ Aiuto",          callback_data="help")],
    ]
    await query.edit_message_text(
        "🥇 *GoldBot — Menu*\nScegli cosa vuoi vedere:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

elif data == "analisi":
    text = (
        f"🔍 *ANALISI GOLD M15*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💵 Prezzo: *${a['price']}*\n"
        f"EMA20: {a['ema20']} | EMA50: {a['ema50']}\n"
        f"Trend: {a['trend']}\n"
        f"RSI: {a['rsi']} — {a['rsi_label']}\n"
        f"🔴 Res: ${a['highest']} | 🟢 Sup: ${a['lowest']}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🎯 *{a['signal']}*\n"
        f"🕐 {datetime.now().strftime('%H:%M')}"
    )
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(keyboard_back))

elif data == "prezzo":
    price = round(df.iloc[-1]['close'], 2)
    prev  = round(df.iloc[-2]['close'], 2)
    diff  = round(price - prev, 2)
    emoji = "📈" if diff >= 0 else "📉"
    await query.edit_message_text(
        f"💵 *GOLD*\n{emoji} *${price}*\nVariazione: {'+' if diff>=0 else ''}{diff}\n🕐 {datetime.now().strftime('%H:%M')}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard_back)
    )

elif data == "segnale":
    await query.edit_message_text(
        f"🎯 *SEGNALE GOLD M15*\n{a['signal']}\nPrezzo: ${a['price']}\n🕐 {datetime.now().strftime('%H:%M')}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard_back)
    )

elif data == "trend":
    await query.edit_message_text(
        f"📊 *TREND*\n{a['trend']}\nEMA20:{a['ema20']} EMA50:{a['ema50']}\nRSI:{a['rsi']} {a['rsi_label']}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard_back)
    )

elif data == "livelli":
    await query.edit_message_text(
        f"⚠️ *LIVELLI*\n🔴 Resistenza: ${a['highest']}\n💵 Prezzo: ${a['price']}\n🟢 Supporto: ${a['lowest']}\nATR: {a['atr']}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard_back)
    )

elif data == "help":
    await query.edit_message_text(
        "📖 Comandi:\n/start /analisi /prezzo /segnale /trend /livelli",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Menu", callback_data="menu")]])
    )
```

# ─────────────────────────────────────────

# MAIN

# ─────────────────────────────────────────

def main():
print(“🥇 GoldBot avviato!”)
app = Application.builder().token(TOKEN).build()

```
app.add_handler(CommandHandler("start",   cmd_start))
app.add_handler(CommandHandler("analisi", cmd_analisi))
app.add_handler(CommandHandler("prezzo",  cmd_prezzo))
app.add_handler(CommandHandler("segnale", cmd_segnale))
app.add_handler(CommandHandler("trend",   cmd_trend))
app.add_handler(CommandHandler("livelli", cmd_livelli))
app.add_handler(CommandHandler("help",    cmd_help))
app.add_handler(CallbackQueryHandler(button_callback))

app.run_polling(drop_pending_updates=True)
```

if **name** == “**main**”:
main()
