import os
import sys
from asyncio import run
from time import sleep

from dotenv import load_dotenv
from iqoptionapi.stable_api import IQ_Option
from pyrogram import Client
from handler import get_one_data

load_dotenv()  # take environment variables from .env.


def mensagem(msg):

    app = Client(
        "BeRichBot",
        api_id=os.environ['TELEGRAM_API_ID'],
        api_hash=os.environ['TELEGRAM_API_HASH'],
        bot_token=os.environ['TELEGRAM_BOT_TOKEN'],

    )

    # Faz com que o bot envie determinada mensagem a partir de um comando
    async def main():
        await app.start()
        await app.send_message(msg)
        await app.stop()

    app.run(main())


def paridades():

    API = IQ_Option(os.environ['EMAIL_IQPTION'], os.environ['PASSWORD_IQPTION'])
    API.connect()
    typeacount = get_one_data("tipo_conta")
    API.change_balance(typeacount)  # PRACTICE / REAL

    if API.check_connect():
        print(' Conectado com sucesso!')
    else:
        print(' Erro ao conectar')
        input('\n\n Aperte enter para sair')
        sys.exit()

    par = API.get_all_open_time()
    binario = []
    digital = []

    for paridade in par['turbo']:
        if par['turbo'][paridade]['open'] == True:
            binario.append(paridade)

    for paridade in par['digital']:
        if par['digital'][paridade]['open'] == True:
            digital.append(paridade)

    binario_final = '\n'.join(binario)
    digital_final = '\n'.join(digital)

    return f"""
    **Paridades Binarias:** \n{binario_final}\n**Paridades Digitais:** \n{digital_final}\n
    """


if __name__ == '__main__':

    print(paridades())
