from handler import get_one_data
from datetime import datetime, timedelta
import sys
from iqoptionapi.stable_api import IQ_Option
from dotenv import load_dotenv
import pandas as pd
from time import time
from utils import ListaControladora, get_one_data, normalize_entry, myround
import os
from functionBacktest import back_sequencia_cinco, back_tres_cavaleiros, back_quatro_jump_2, back_end_of_second

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

def timestamp_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp)

def datetime_to_timestamp(datetime_value):
    return datetime_value.timestamp()

def parse_datetime(input_string):
    try:
        date_str, time_str = input_string.split(';')
        day, month, year = map(int, date_str.split('/'))
        hour, minute = map(int, time_str.split(':'))
        return datetime(year, month, day, hour, minute)
    except ValueError:
        raise ValueError("Formato de data/hora inválido. Use o formato 'dd/mm/aaaa;hh:mm'.")

def count_timeframes_between(dh_inicio, dh_fim, timeframe):
    if timeframe not in {1, 2, 5, 15}:
        raise ValueError("O valor do 'timeframe' deve ser 1, 2, 5 ou 15 minutos.")

    count = 0
    current_time = dh_fim

    while current_time > dh_inicio:
        if timeframe == 1 or (timeframe == 2 and current_time.minute % 2 == 0) or \
           (timeframe == 5 and current_time.minute % 5 == 0) or \
           (timeframe == 15 and current_time.minute % 15 == 0):
            count += 1

        current_time -= timedelta(minutes=1)

    return count

def test_time_return(API, par, timeframe_n, dh_inicio, dh_fim):

    dh_inicio = parse_datetime(dh_inicio)
    dh_fim = parse_datetime(dh_fim)

    print("Data/hora de início parseada:", dh_inicio)
    print("Data/hora de fim parseada:", dh_fim)

    # Verifica se data/hora de início é menor que a data/hora de fim
    if dh_inicio >= dh_fim:
        raise ValueError("A data/hora de início deve ser menor que a data/hora de fim.")

    periodo = count_timeframes_between(dh_inicio, dh_fim, timeframe_n) + 1

    print(periodo)
    
    # Pega os dados do par e do timeframe
    velas = API.get_candles(par, timeframe_n * 60, periodo, datetime_to_timestamp(dh_fim))
    print("pegou as velas...")

    df = pd.DataFrame(velas)
    df.rename(columns={"max": "high", "min": "low"}, inplace=True)

    # Pega a coluna from e converte para formatatms e insere no lugar do valor
    df['from'] = df['from'].apply(formatatms)

    df['direct'] = df.apply(lambda row: ('green',row['from']) if (row['close'] - row['open'])
                            > 0 else ('red',row['from']) if (row['close'] - row['open']) < 0 else ('grey',row['from']), axis=1)

    LISTA_EST = list(df.apply(
        lambda row: row['direct'], axis=1))
    
    return LISTA_EST

def teste_gera_candle(par, timeframe, periods=15):

    API = IQ_Option(os.getenv('EMAIL_IQPTION'),os.getenv('PASSWORD_IQPTION'))
    API.connect()

    if API.check_connect():
        print(' Conectado com sucesso!')
    else:
        print(' Erro ao conectar')
        input('\n\n Aperte enter para sair')
        sys.exit()

    velas = API.get_candles(par, timeframe * 60, periods, time())

    df = pd.DataFrame(velas)
    df.rename(columns={"max": "high", "min": "low"}, inplace=True)

    # Pega a coluna from e converte para formatatms e insere no lugar do valor
    df['from'] = df['from'].apply(formatatms)

    # Pega a coluna to e converte para formatatms e insere no lugar do valor
    df['to'] = df['to'].apply(formatatms)

    df['direct'] = df.apply(lambda row: ('green',row['from'][:-3]) if (row['close'] - row['open'])
                            > 0 else ('red',row['from'][:-3]) if (row['close'] - row['open']) < 0 else ('grey',row['from'][:-3]), axis=1)

    LISTA_EST = list(df.apply(
        lambda row: row['direct'], axis=1))

    return LISTA_EST

def sequencia_backtest(api_conn, par, timeframe, periods=6, tempo_my=time()):

    print("Pegando as velas")
    velas = api_conn.get_candles(par, timeframe * 60, periods, tempo_my)
    print("Peguei as velas")

    df = pd.DataFrame(velas)
    df.rename(columns={"max": "high", "min": "low"}, inplace=True)

    # Pega a coluna from e converte para formatatms e insere no lugar do valor
    df['from'] = df['from'].apply(formatatms)

    # Pega a coluna to e converte para formatatms e insere no lugar do valor
    df['to'] = df['to'].apply(formatatms)

    df['direct'] = df.apply(lambda row: ('green',row['from'][:-3]) if (row['close'] - row['open'])
                            > 0 else ('red',row['from'][:-3]) if (row['close'] - row['open']) < 0 else ('grey',row['from'][:-3]), axis=1)

    LISTA_EST = list(df.apply(
        lambda row: row['direct'], axis=1))

    return LISTA_EST

def backtest_maker(coins, timeframe, period, strateg, lmt, banca=None, personsdatas=None):
    print("####################################")
    print("Iniciando a função backtest_maker")
    print("####################################")
    API = IQ_Option(os.getenv('EMAIL_IQPTION'),os.getenv('PASSWORD_IQPTION'))
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
        if strateg == 'sequencia_cinco':

            if personsdatas:
                dh_inicial, dh_final = personsdatas.split('-')
                print("Data hora inicial:", dh_inicial)
                print("Data hora final:", dh_final)
                candles_all = test_time_return(API, coin, timeframe_n, dh_inicial, dh_final)
            else:
                candles_all = sequencia_backtest(API, coin, timeframe_n, period_n)

            # Recupera todos os candles do period

            qtd_wins, qtd_loss, list_win, list_loss, q_banca, luc_prej, arr_q  = back_sequencia_cinco(candles_all, banca, tipo_entrada, lmt)

            print(f"__***BACKTEST PARA O PAR {coin}***__\n**PERIODO** : {period_n}\n**TIMEFRAME **: {timeframe_n}  \n**QTD WINS** : {qtd_wins}\n**QTD LOSS**: {qtd_loss}  \n**LUCRO/PREJUIZO** : U$ {luc_prej}\n\n**LISTA DE WINS:**\n{list_win}\n\n**LISTA DE LOSS:**\n{list_loss}\n\n**BANCAS QUEBRADAS:**\n{q_banca}")

            resultado_f.append(f"__***BACKTEST PARA O PAR {coin}***__\n**PERIODO** : {period_n}\n**TIMEFRAME **: {timeframe_n}  \n**QTD WINS** : {qtd_wins}\n**QTD LOSS**: {qtd_loss}  \n**LUCRO/PREJUIZO** : U$ {luc_prej}\n\n**LISTA DE WINS:**\n{list_win}\n\n**LISTA DE LOSS:**\n{list_loss}\n\n**BANCAS QUEBRADAS:**\n{q_banca}")
        
        elif strateg == 'tres_cavaleiros':

            if personsdatas:
                dh_inicial, dh_final = personsdatas.split('-')
                print("Data hora inicial:", dh_inicial)
                print("Data hora final:", dh_final)
                candles_all = test_time_return(API, coin, timeframe_n, dh_inicial, dh_final)
            else:
                candles_all = sequencia_backtest(API, coin, timeframe_n, period_n)

            qtd_wins, qtd_loss, list_win, list_loss, q_banca, luc_prej, arr_q  = back_tres_cavaleiros(candles_all, banca, tipo_entrada)
            
            print(f"__***BACKTEST PARA O PAR {coin}***__\n**PERIODO** : {period_n}\n**TIMEFRAME **: {timeframe_n}  \n**QTD WINS** : {qtd_wins}\n**QTD LOSS**: {qtd_loss}  \n**LUCRO/PREJUIZO** : U$ {luc_prej}\n\n**LISTA DE WINS:**\n{list_win}\n\n**LISTA DE LOSS:**\n{list_loss}\n\n**BANCAS QUEBRADAS:**\n{q_banca}**LISTA BANCAS QUEBRADAS:**\n{arr_q}")

            resultado_f.append(f"__***BACKTEST PARA O PAR {coin}***__\n**PERIODO** : {period_n}\n**TIMEFRAME **: {timeframe_n}  \n**QTD WINS** : {qtd_wins}\n**QTD LOSS**: {qtd_loss}  \n**LUCRO/PREJUIZO** : U$ {luc_prej}\n\n**LISTA DE WINS:**\n{list_win}\n\n**LISTA DE LOSS:**\n{list_loss}\n\n**BANCAS QUEBRADAS:**\n{q_banca}")

        elif strateg == 'end_of_second':

            if personsdatas:
                dh_inicial, dh_final = personsdatas.split('-')
                print("Data hora inicial:", dh_inicial)
                print("Data hora final:", dh_final)
                candles_all = test_time_return(API, coin, timeframe_n, dh_inicial, dh_final)
            else:
                candles_all = sequencia_backtest(API, coin, timeframe_n, period_n)

            qtd_wins, qtd_loss, list_win, list_loss, q_banca, luc_prej, arr_q  = back_end_of_second(candles_all, banca, tipo_entrada)
            
            print(f"__***BACKTEST PARA O PAR {coin}***__\n**PERIODO** : {period_n}\n**TIMEFRAME **: {timeframe_n}  \n**QTD WINS** : {qtd_wins}\n**QTD LOSS**: {qtd_loss}  \n**LUCRO/PREJUIZO** : U$ {luc_prej}\n\n**LISTA DE WINS:**\n{list_win}\n\n**LISTA DE LOSS:**\n{list_loss}\n\n**BANCAS QUEBRADAS:**\n{q_banca}**LISTA BANCAS QUEBRADAS:**\n{arr_q}")

            resultado_f.append(f"__***BACKTEST PARA O PAR {coin}***__\n**PERIODO** : {period_n}\n**TIMEFRAME **: {timeframe_n}  \n**QTD WINS** : {qtd_wins}\n**QTD LOSS**: {qtd_loss}  \n**LUCRO/PREJUIZO** : U$ {luc_prej}\n\n**LISTA DE WINS:**\n{list_win}\n\n**LISTA DE LOSS:**\n{list_loss}\n\n**BANCAS QUEBRADAS:**\n{q_banca}")

        elif strateg == 'quatro_jump_2':

            if personsdatas:
                dh_inicial, dh_final = personsdatas.split('-')
                print("Data hora inicial:", dh_inicial)
                print("Data hora final:", dh_final)
                candles_all = test_time_return(API, coin, timeframe_n, dh_inicial, dh_final)
            else:
                candles_all = sequencia_backtest(API, coin, timeframe_n, period_n)

            qtd_wins, qtd_loss, list_win, list_loss, q_banca, luc_prej, arr_q  = back_quatro_jump_2(candles_all, banca, tipo_entrada)
            
            print(f"__***BACKTEST PARA O PAR {coin}***__\n**PERIODO** : {period_n}\n**TIMEFRAME **: {timeframe_n}  \n**QTD WINS** : {qtd_wins}\n**QTD LOSS**: {qtd_loss}  \n**LUCRO/PREJUIZO** : U$ {luc_prej}\n\n**LISTA DE WINS:**\n{list_win}\n\n**LISTA DE LOSS:**\n{list_loss}\n\n**BANCAS QUEBRADAS:**\n{q_banca}**LISTA BANCAS QUEBRADAS:**\n{arr_q}")

            resultado_f.append(f"__***BACKTEST PARA O PAR {coin}***__\n**PERIODO** : {period_n}\n**TIMEFRAME **: {timeframe_n}  \n**QTD WINS** : {qtd_wins}\n**QTD LOSS**: {qtd_loss}  \n**LUCRO/PREJUIZO** : U$ {luc_prej}\n\n**LISTA DE WINS:**\n{list_win}\n\n**LISTA DE LOSS:**\n{list_loss}\n\n**BANCAS QUEBRADAS:**\n{q_banca}")

        else:
            return "Falha na recuperação dos dados"

    return resultado_f

if __name__ == '__main__':

    backtest_maker('EURUSD-OTC', '5m', '6h', 'tres_cavaleiros', 3, 300, '14/10/2023;09:40-14/10/2023;11:00')

    # lista = teste_gera_candle('EURUSD-OTC', 5, 50)
    # win_count, loss_count, list_win, list_loss, quebra_banca, luc_prej = analise_maioria(filtro_tempo(lista), get_one_data('qtd_ciclos'))
    # print("Minha Lista:")
    # print("********************************************")
    # print(lista)
    # print("********************************************")
    # print("win_count:", win_count)
    # print("loss_count:", loss_count)
    # print("list_win:", list_win)
    # print("list_loss:", list_loss)
    # print("Quebra banca:", quebra_banca)
    # print("Lucro/Prejuízo:", luc_prej)
