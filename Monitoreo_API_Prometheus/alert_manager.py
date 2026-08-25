import logging
import telebot #Librería para mensajes de Telegram
from config import get_config

def send_notification(message):
    try:
        config = get_config()
        telegram_token = str(config["telegram_token"])
        telegram_chat_id = int(config["telegram_chat_id"])
        bot = telebot.TeleBot(telegram_token) #Definimos el bot
        bot.send_message(telegram_chat_id, message)
    except Exception as e:
        logging.error(f"❌ Error al enviar mensaje a Telegram: {e}", exc_info=True)