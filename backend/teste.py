
try:
    import os
    import sys
    sys.path.append(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))
except ModuleNotFoundError:
    ...
from backend.functionBacktest import back_bollinger_bands
from handler import *
from dotenv import load_dotenv
from time import time, sleep
from iqoptionapi.stable_api import IQ_Option
from utils import ListaControladora, normalize_timeframe

load_dotenv()


        
if __name__ == '__main__':
    # API = IQ_Option(os.getenv('EMAIL_IQPTION'),os.getenv('PASSWORD_IQPTION'))
    # API.connect()
    # typeacount = get_one_data("tipo_conta")
    # API.change_balance(typeacount)  # PRACTICE / REAL

    # if API.check_connect():
    #     print(' Conectado com sucesso!')
    # else:
    #     print(' Erro ao conectar')
    #     input('\n\n Aperte enter para sair')
    #     sys.exit()
        
   
    # back_bollinger_bands()

    lista = [[1.25,2.5],[5.55,6.87],[12.24,13.45]]
    elemento = ListaControladora(lista)


    print(elemento.x)
    print(elemento.y)