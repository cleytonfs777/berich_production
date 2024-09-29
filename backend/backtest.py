from backend.handler import get_one_data
from datetime import datetime
import sys
from iqoptionapi.stable_api import IQ_Option
from dotenv import load_dotenv
import pandas as pd
from time import time
from backend.utils import get_one_data, normalize_entry, myround
import os
from backend.functionBacktest import back_bollinger_bands

load_dotenv()


def paridades_open(api_conn: IQ_Option):

    typecoin = get_one_data('typecoin')
    par = api_conn.get_all_open_time()
    binario = []
    digital = []

    if typecoin == 'binario':
        for paridade in par['turbo']:
            if par['turbo'][paridade]['open'] == True:
                binario.append(paridade)
        return binario

    elif typecoin == 'digital':
        for paridade in par['digital']:
            if par['digital'][paridade]['open'] == True:
                digital.append(paridade)
        return digital


def formatatms(tms):
    return datetime.fromtimestamp(tms).strftime('%H:%M:%S')


def obter_dados_velas(api_conn, par, timeframe, periods):
    # Obter as velas da API
    velas = api_conn.get_candles(par, timeframe * 60, periods, time())

    # Criar uma lista de dicionários com os dados desejados
    candles_all = {
        'open': [],
        'close': [],
        'min': [],
        'max': [],
        'volume': [],
        'time': []  # Nova coluna para armazenar os horários
    }

    # Preencher os dados das velas
    for vela in velas:
        candles_all['open'].append(vela['open'])
        candles_all['close'].append(vela['close'])
        candles_all['min'].append(vela['min'])
        candles_all['max'].append(vela['max'])
        candles_all['volume'].append(vela['volume'])

        # Converte o campo 'from' para um formato legível e adiciona à lista 'time'
        candles_all['time'].append(formatatms(vela['from']))

    return candles_all


def backtest_maker(coins, timeframe, period, strateg, lmt, banca=None, personsdatas=None):
    print("####################################")
    print("Iniciando a função backtest_maker")
    print("####################################")
    API = IQ_Option(os.getenv('EMAIL_IQPTION'), os.getenv('PASSWORD_IQPTION'))
    API.connect()

    if API.check_connect():
        print(' Conectado com sucesso!')
    else:
        print(' Erro ao conectar')
        input('\n\n Aperte enter para sair')
        sys.exit()

    if not banca:
        banca = myround(API.get_balance())

    lmt = int(lmt)

    print(f"Total de {period} períodos")

    timeframe_n, period_n = normalize_entry(timeframe, period)
    tipo_entrada = get_one_data('tipo_entrada')
    resultado_f = []

    if coins == 'TODOS':
        # insere na variavel coin uma list com os pares abertos
        coins = paridades_open(API)

    else:
        coins = list([coins])

    for coin in coins:
        # Estratégia de Backtest
        if strateg == 'bollinger_bands':
            print("Ininciando a estratégia bollinger_bands")
            candles_all = obter_dados_velas(
                API, coin, timeframe_n, period_n)
            print("Candles all:", candles_all)
            qtd_wins, qtd_loss, list_win, list_loss, q_banca, luc_prej, arr_q = back_bollinger_bands(
                candles_all, banca)

            print(f"__***BACKTEST PARA O PAR {coin}***__\n**PERIODO** : {period_n}\n**TIMEFRAME **: {timeframe_n}  \n**QTD WINS** : {qtd_wins}\n**QTD LOSS**: {qtd_loss}  \n**LUCRO/PREJUIZO** : U$ {luc_prej}\n\n**LISTA DE WINS:**\n{list_win}\n\n**LISTA DE LOSS:**\n{list_loss}\n\n**BANCAS QUEBRADAS:**\n{q_banca}")

            resultado_f.append(
                f"__***BACKTEST PARA O PAR {coin}***__\n**PERIODO** : {period_n}\n**TIMEFRAME **: {timeframe_n}  \n**QTD WINS** : {qtd_wins}\n**QTD LOSS**: {qtd_loss}  \n**LUCRO/PREJUIZO** : U$ {luc_prej}\n\n**LISTA DE WINS:**\n{list_win}\n\n**LISTA DE LOSS:**\n{list_loss}\n\n**BANCAS QUEBRADAS:**\n{q_banca}")

        else:
            return "Falha na recuperação dos dados"

    return resultado_f


if __name__ == '__main__':

    backtest_maker('EURUSD-OTC', '5m', '6h', 'tres_cavaleiros',
                   3, 300, '14/10/2023;09:40-14/10/2023;11:00')
