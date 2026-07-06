import telebot #Librería para mensajes de Telegram

def send_notification(config,message):
    try:
        bot = telebot.TeleBot(config["telegram_token"]) #Definimos el bot
        bot.send_message(config["telegram_chat_id"], message)
    except Exception as e:
        logging.error(f"❌ Error al enviar mensaje a Telegram: {e}")