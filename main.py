from dotenv import load_dotenv, dotenv_values
import psycopg2
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import time

env_config = dotenv_values(".env")

def connect_to_db():
    conn = None
    try:
        conn = psycopg2.connect(
            host=env_config["DATABASE_HOST"],
            database=env_config["DATABASE_NAME"],
            user=env_config["DATABASE_USER"],
            password=env_config["DATABASE_PASSWORD"]
        )
    except Exception as e:
        print(f"Cannot connect to PostgreSQL DB: {e}")
        raise Exception("Failed to connect to the database")
    return conn

def get_crypto_prices(chat_id, db_conn):
    cursor = db_conn.cursor()
    
    cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'crypto_prices')")
    table_exists = cursor.fetchone()[0]
    
    if table_exists:
        cursor.execute("SELECT name, price FROM crypto_prices ORDER BY price DESC LIMIT 10;")
        prices_data = cursor.fetchall()
        
        prices_str = "\n".join([f"{row[0]}: {row[1]}" for row in prices_data])
        bot.send_message(chat_id, prices_str)
    else:
        time.sleep(10)
        get_crypto_prices(chat_id, db_conn)

if __name__ == "__main__":
    try:
        db_conn = connect_to_db()
        
        token = env_config["TOKEN"]
        
        bot = telebot.TeleBot(token)
        
        @bot.message_handler(commands=['start'])
        def send_welcome(message):
            chat_id = message.chat.id
            
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Курс Binance"))
            
            welcome_message = "Нажмите \"Курс Binance\", чтобы получить курс топ-10 криптовалют с Binance.\n\nℹ️ Курс обновляется каждые 5 минут"
            
            bot.send_message(chat_id, welcome_message, reply_markup=keyboard)
        
        @bot.message_handler(func=lambda message: message.text == "Курс Binance")
        def handle_crypto_prices(message):
            chat_id = message.chat.id
            get_crypto_prices(chat_id, db_conn)
        
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error starting bot: {e}")
