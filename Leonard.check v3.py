import time
import random
import threading
import os
import sys
from playsound import playsound
from plyer import notification
import telebot
from telebot import types
import requests

# 🔥 НАСТРОЙКИ
TELEGRAM_BOT_TOKEN = 'СЮДА_ТОКЕН_БОТА'
TELEGRAM_USER_ID = 'СЮДА_ТВОЙ_ID'
CRYPTOBOT_API_TOKEN = "СЮДА_ТВОЙ_CRYPTOBOT_API_TOKEN"  # Получи API токен от CryptoBot
SUCCESS_SOUND = 'success.mp3'  # Файл звука успеха

# Глобальные переменные
is_mining = False
total_found = 0
total_amount = 0.0
current_currency = "Bitcoin (BTC)"

# Инициализация бота
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Валюты
currencies = [
    "Bitcoin (BTC)",
    "Tether (USDT)",
    "USD (Dollar)",
    "TON (Toncoin)",
    "Barton (Fictional)",
    "Notcoin (NOT)",
    "Ethereum (ETH)",
    "Litecoin (LTC)",
    "Dogecoin (DOGE)"
]


# Функции
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def logo():
    print("""
██╗     ███████╗ ██████╗ ███╗   ██╗ █████╗ ██████╗ ██████╗  ██████╗██╗  ██╗
██║     ██╔════╝██╔═══██╗████╗  ██║██╔══██╗██╔══██╗██╔══██╗██╔════╝██║ ██╔╝
██║     █████╗  ██║   ██║██╔██╗ ██║███████║██║  ██║██████╔╝██║     █████╔╝ 
██║     ██╔══╝  ██║   ██║██║╚██╗██║██╔══██║██║  ██║██╔═══╝ ██║     ██╔═██╗ 
███████╗███████╗╚██████╔╝██║ ╚████║██║  ██║██████╔╝██║     ██║  ██╗██║  ██╗
╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝

                         Powered by Leonard.check
    """)


def play_success_sound():
    try:
        playsound(SUCCESS_SOUND)
    except Exception as e:
        print(f"[!] Ошибка воспроизведения звука: {e}")


def notify_success(amount, currency):
    notification.notify(
        title="Leonard.check — Найден чек!",
        message=f"{amount} {currency} пойман!",
        timeout=5
    )


def send_telegram_message(message):
    try:
        bot.send_message(TELEGRAM_USER_ID, message)
    except Exception as e:
        log_error(f"Ошибка отправки сообщения в Telegram: {e}")


def save_log(text):
    try:
        with open('logs.txt', 'a', encoding='utf-8') as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} — {text}\n")
    except Exception as e:
        print(f"[!] Ошибка записи в лог: {e}")


def log_error(error_text):
    save_log(f"ERROR: {error_text}")


# Функция для создания CryptoBot чека
def create_crypto_check(amount, currency_code):
    try:
        url = "https://pay.crypt.bot/api/createInvoice"
        headers = {
            "Content-Type": "application/json",
            "Crypto-Pay-API-Token": CRYPTOBOT_API_TOKEN
        }
        payload = {
            "asset": currency_code,
            "amount": str(amount),
            "description": f"Leonard.check автоген",
            "hidden_message": "Сгенерировано Leonard.check",
            "paid_btn_name": "url",
            "paid_btn_url": "https://t.me/LeonardCheckBot"
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            invoice_data = response.json()
            if invoice_data.get("ok"):
                link = invoice_data["result"]["pay_url"]
                return link
            else:
                log_error(f"Ошибка создания чека через CryptoBot: {invoice_data}")
        else:
            log_error(f"Ответ от CryptoBot: {response.status_code}, {response.text}")
    except Exception as e:
        log_error(f"Ошибка создания CryptoBot чека: {e}")
    return None


# Функция для получения валюты из имени
def get_crypto_asset(currency_name):
    mapping = {
        "Bitcoin (BTC)": "BTC",
        "Tether (USDT)": "USDT",
        "USD (Dollar)": "USDT",
        "TON (Toncoin)": "TON",
        "Barton (Fictional)": "TON",  # Можно заглушку
        "Notcoin (NOT)": "TON",  # Пока NOT не поддерживается, можно на TON
        "Ethereum (ETH)": "ETH",
        "Litecoin (LTC)": "LTC",
        "Dogecoin (DOGE)": "DOGE"
    }
    return mapping.get(currency_name, "USDT")


# Главная функция майнинга
def mine_loop():
    global is_mining, total_found, total_amount, current_currency
    send_telegram_message(f"🚀 Начинаю ловлю чеков для {current_currency}!")
    while is_mining:
        time.sleep(random.uniform(0.5, 1.0))
        code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16))
        success = random.choice([False, False, False, True])  # 25% шанс
        if success:
            amount = round(random.uniform(0.1, 10.0), 4)
            crypto_asset = get_crypto_asset(current_currency)  # Получаем нужную валюту
            check_link = create_crypto_check(amount, crypto_asset)

            if check_link:
                message = f"✅ Найден чек: {amount} {current_currency.split()[0]}\n🎟 Чек: {check_link}"
            else:
                message = f"✅ Найден чек: {amount} {current_currency.split()[0]}\n(не удалось создать чек через CryptoBot)"

            send_telegram_message(message)
            play_success_sound()
            notify_success(amount, current_currency.split()[0])
            save_log(message)
            total_found += 1
            total_amount += amount


# Команды бота
@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🚀 Старт ловли")
    btn2 = types.KeyboardButton("🛑 Стоп ловли")
    btn3 = types.KeyboardButton("📈 Статистика")
    btn4 = types.KeyboardButton("🪙 Выбрать валюту")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    bot.send_message(message.chat.id, "Добро пожаловать в Leonard.check!", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def bot_message(message):
    global is_mining, current_currency

    if message.text == "🚀 Старт ловли":
        if not is_mining:
            is_mining = True
            threading.Thread(target=mine_loop).start()
            bot.send_message(message.chat.id, "✅ Ловля чеков запущена.")
        else:
            bot.send_message(message.chat.id, "⚠️ Ловля уже идёт.")

    elif message.text == "🛑 Стоп ловли":
        if is_mining:
            is_mining = False
            bot.send_message(message.chat.id, "🛑 Ловля остановлена.")
        else:
            bot.send_message(message.chat.id, "⚠️ Ловля уже остановлена.")

    elif message.text == "📈 Статистика":
        bot.send_message(message.chat.id,
                         f"📊 Поймано чеков: {total_found}\n💰 Общая сумма: {round(total_amount, 4)} {current_currency.split()[0]}")

    elif message.text == "🪙 Выбрать валюту":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        for currency in currencies:
            markup.add(types.KeyboardButton(currency))
        markup.add(types.KeyboardButton("🔙 Назад"))
        bot.send_message(message.chat.id, "Выберите валюту:", reply_markup=markup)

    elif message.text in currencies:
        current_currency = message.text
        bot.send_message(message.chat.id, f"✅ Вы выбрали валюту: {current_currency}")

    elif message.text == "🔙 Назад":
        start_message(message)

    else:
        bot.send_message(message.chat.id, "⚠️ Неизвестная команда. Используйте кнопки.")


def main():
    clear_screen()
    logo()
    print("\nLeonard.check успешно запущен!")
    print("✅ Ожидание команд в Telegram...")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            log_error(f"Ошибка бота: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
