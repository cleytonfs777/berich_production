from backend.handler import get_one_data
from datetime import datetime, timedelta
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


def datetime_to_timestamp(datetime_value):
    return datetime_value.timestamp()


def parse_datetime(input_string):
    try:
        date_str, time_str = input_string.split(';')
        day, month, year = map(int, date_str.split('/'))
        hour, minute = map(int, time_str.split(':'))
        print(f"""
        ano: {year}
        mes: {month}
        dia: {day}
        hora: {hour}
        minuto: {minute}
""")
        return datetime(year, month, day, hour, minute)
    except ValueError:
        raise ValueError(
            "Formato de data/hora inválido. Use o formato 'dd/mm/aaaa;hh:mm'.")


def count_timeframes_between(dh_inicio, dh_fim, timeframe):
    if timeframe not in {1, 2, 5, 15}:
        raise ValueError(
            "O valor do 'timeframe' deve ser 1, 2, 5 ou 15 minutos.")

    count = 0
    current_time = dh_fim

    while current_time > dh_inicio:
        if timeframe == 1 or (timeframe == 2 and current_time.minute % 2 == 0) or \
           (timeframe == 5 and current_time.minute % 5 == 0) or \
           (timeframe == 15 and current_time.minute % 15 == 0):
            count += 1

        current_time -= timedelta(minutes=1)

    return count


def formatatms(tms):
    return datetime.fromtimestamp(tms).strftime('%H:%M:%S')


def obeter_dados_person(api_conn, par, timeframe_n, dh_inicial, dh_final):
    print("Data/hora de início:", dh_inicial)
    print("Data/hora de fim:", dh_final)

    dh_inicio = parse_datetime(dh_inicial)
    dh_fim = parse_datetime(dh_final)

    print("Data/hora de início parseada:", dh_inicio)
    print("Data/hora de fim parseada:", dh_fim)

    # Verifica se data/hora de início é menor que a data/hora de fim
    if dh_inicio >= dh_fim:
        raise ValueError(
            "A data/hora de início deve ser menor que a data/hora de fim.")

    periodo = count_timeframes_between(dh_inicio, dh_fim, timeframe_n) + 1

    print(periodo)

    # Pega os dados do par e do timeframe
    velas = api_conn.get_candles(
        par, timeframe_n * 60, periodo, datetime_to_timestamp(dh_fim))
    print("pegou as velas...")

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
    print("finalizei a normalize")
    tipo_entrada = get_one_data('tipo_entrada')
    resultado_f = []

    print(
        f"Periodo normalizado: {period_n} e timeframe normalizado: {timeframe_n}")

    if coins == 'TODOS':
        # insere na variavel coin uma list com os pares abertos
        coins = paridades_open(API)

    else:
        coins = list([coins])

    print("Coins:", coins)

    for coin in coins:
        print("Essa é minha primeira coin? ", coin)
        # Estratégia de Backtest
        if strateg == 'paula':
            print("Ininciando a estratégia paula")

            # Tratamento de Data e Hora
            if personsdatas:
                dh_inicial, dh_final = personsdatas.split('-')
                print("Data hora inicial:", dh_inicial)
                print("Data hora final:", dh_final)
                candles_all = obeter_dados_person(
                    API, coin, timeframe_n, dh_inicial, dh_final)
            else:
                candles_all = obter_dados_velas(
                    API, coin, timeframe_n, period_n)

            # candles_all = obter_dados_velas(
            #     API, coin, timeframe_n, period_n)
            print("Candles all:", candles_all)
            qtd_wins, qtd_loss, list_win, list_loss, q_banca, luc_prej, arr_q = back_bollinger_bands(
                candles_all, banca)

            print(f"__***BACKTEST PARA O PAR {coin}***__\n**PERIODO** : {period_n}\n**TIMEFRAME **: {timeframe_n}  \n**QTD WINS** : {qtd_wins}\n**QTD LOSS**: {qtd_loss}  \n**LUCRO/PREJUIZO** : U$ {luc_prej}\n\n**LISTA DE WINS:**\n{list_win}\n\n**LISTA DE LOSS:**\n{list_loss}\n\n**BANCAS QUEBRADAS:**\n{q_banca}\n\n**Times de bancas quebradas:**\n{arr_q}")

            resultado_f.append(
                f"__***BACKTEST PARA O PAR {coin}***__\n**PERIODO** : {period_n}\n**TIMEFRAME **: {timeframe_n}  \n**QTD WINS** : {qtd_wins}\n**QTD LOSS**: {qtd_loss}  \n**LUCRO/PREJUIZO** : U$ {luc_prej}\n\n**LISTA DE WINS:**\n{list_win}\n\n**LISTA DE LOSS:**\n{list_loss}\n\n**BANCAS QUEBRADAS:**\n{q_banca}\n\n**Times de bancas quebradas:**\n{arr_q}")

        else:
            return "Falha na recuperação dos dados"

    return resultado_f


if __name__ == '__main__':

    backtest_maker('EURUSD-OTC', '5m', '6h', 'tres_cavaleiros',
                   3, 300, '14/10/2023;09:40-14/10/2023;11:00')
