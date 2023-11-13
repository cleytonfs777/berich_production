import requests
import os
from dotenv import load_dotenv

def enviar_mensagem_telegram(*msgs):
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('USERNAME_TELEGRAM')
    base_url = f"https://api.telegram.org/bot{token}/sendMessage"

    for msg in msgs:
        payload = {
            'chat_id': chat_id,
            'text': msg
        }
        response = requests.post(base_url, data=payload)
        # Você pode adicionar algum tratamento de erro aqui, se necessário





