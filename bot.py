
import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API = "https://api.coingecko.com/api/v3"

logging.basicConfig(level=logging.INFO)

COINS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "LINK": "chainlink",
    "NEAR": "near",
    "XRP": "ripple",
    "BNB": "binancecoin",
    "DOGE": "dogecoin",
    "ADA": "cardano",
    "AVAX": "avalanche-2",
    "DOT": "polkadot",
    "ATOM": "cosmos",
    "TAO": "bittensor",
    "TRX": "tron"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! ربات تحلیلگر رشدینو فعال شد.\n\n"
        "/price BTC قیمت ارز\n"
        "/scan بررسی بازار\n"
        "/help راهنما"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "نمونه دستور:\n"
        "/price BTC\n"
        "/price NEAR\n"
        "/scan"
    )

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("مثال: /price BTC")
        return

    symbol = context.args[0].upper()
    coin_id = COINS.get(symbol)

    if not coin_id:
        await update.message.reply_text("فعلاً این نماد در فهرست اولیه نیست.")
        return

    try:
        response = requests.get(
            f"{API}/simple/price",
            params={
                "ids": coin_id,
                "vs_currencies": "usd",
                "include_24hr_change": "true"
            },
            timeout=20
        )
        response.raise_for_status()
        data = response.json()[coin_id]

        await update.message.reply_text(
            f"ارز: {symbol}\n"
            f"قیمت: ${data['usd']}\n"
            f"تغییر ۲۴ ساعته: {data.get('usd_24h_change', 0):.2f}%"
        )

    except Exception:
        await update.message.reply_text("دریافت قیمت ناموفق بود. بعداً تلاش کن.")

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("در حال بررسی بازار...")

    try:
        response = requests.get(
            f"{API}/coins/markets",
            params={
                "vs_currency": "usd",
                "order": "volume_desc",
                "per_page": 100,
                "page": 1,
                "price_change_percentage": "24h,7d"
            },
            timeout=30
        )
        response.raise_for_status()
        coins = response.json()

        results = []

        for coin in coins:
            change = coin.get("price_change_percentage_24h") or 0
            change7 = coin.get("price_change_percentage_7d_in_currency") or 0
            volume = coin.get("total_volume") or 0

            if 2 <= change <= 8 and change7 > 3 and volume > 10000000:
                results.append(
                    f"{coin['symbol'].upper()} | "
                    f"${coin['current_price']}\n"
                    f"تغییر روزانه: {change:.2f}%"
                )

        if results:
            message = "فرصت‌های قابل بررسی:\n\n"
            message += "\n\n".join(results[:10])
        else:
            message = "در این بررسی فرصتی مطابق معیارها پیدا نشد."

        message += "\n\nاین گزارش پیشنهاد قطعی خرید نیست."
        await update.message.reply_text(message)

    except Exception:
        await update.message.reply_text("خطا در بررسی بازار.")

def main():
    if not TOKEN:
        raise ValueError("توکن تلگرام تنظیم نشده است.")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("scan", scan))

    app.run_polling()

if __name__ == "__main__":
    main()
