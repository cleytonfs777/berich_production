import os
import sys
from time import sleep, time
import pandas as pd
from dotenv import load_dotenv
from handler import *
from iqoptionapi.stable_api import IQ_Option
from senderbot import mensagem
from utils import check_colors, normalize_timeframe, calibrar_entrada, myround, ListaControladora
from datetime import datetime
from messeger import enviar_mensagem_telegram
from threading import Thread
import random



# Nesse módulo serão descritas as principais estratégias a ser utilizadas em opções binárias

load_dotenv()

def all_entry(lc):
    lista = get_one_data('valor_por_ciclo')
    i = lc.proxima_posicao()
    elemento = lista[i[0]][i[1]]

    return elemento

def sequencia_cinco_teste():
    return True, 'call'

def banca(API):
    return round(API.get_balance(), 2)

def enviar_mensagem_em_thread(*mensagens):
    t = Thread(target=enviar_mensagem_telegram, args=mensagens)
    t.start()


# def media_simples(api_conn, par, timeframe):
    
#     def get_data(par, timeframe, periods = 200):

#         velas = api_conn.get_candles(par, timeframe * 60, periods, time())

#         df = pd.DataFrame(velas)
#         df.rename(columns={"max": "high", "min": "low"}, inplace=True)

#         return df


#     periods = 14
#     tyme_avg = 'SMA'

#     dec1 = get_data(par, timeframe, 2)
#     dec = 7 - len(str(dec1.iloc[-1]['close']).split('.')[0])
#     print('\n')



#     while True:

#         dfg = get_data(par, timeframe, 200)

#         print(dec)
#         print("******************************************")

#         if tyme_avg == 'SMA':
#             nnp = TA.SMA(dfg,periods)
#         elif tyme_avg == 'EMA':
#             nnp = TA.EMA(dfg,periods)
#         else:
#             raise Exception("Erro ao obter tipo de média...")

#         MEDIAM_AT = round(nnp.iloc[-1], dec)
#         ATUAL_T = round(dfg.iloc[-1]['close'], dec)



#         print('Média Movel: ',MEDIAM_AT,
#                 '| Taxa Atual: ', ATUAL_T,

#         )
#         sleep(1)

def sequencia_cinco(api_conn, par, timeframe, periods=6):
    # Printar todos os parametros recebidos
    print(f"Meu par: {par}")
    print(f"Meu timeframe: {timeframe}")
    print(f"Meus periods: {periods}")

    timeframe = normalize_timeframe(timeframe)
    # Pega os dados do par e do timeframe
    velas = api_conn.get_candles(par, timeframe * 60, periods, time())

    df = pd.DataFrame(velas)
    df.rename(columns={"max": "high", "min": "low"}, inplace=True)

    df['direct'] = df.apply(lambda row: 'green' if (row['close'] - row['open'])
                            > 0 else 'red' if (row['close'] - row['open']) < 0 else 'grey', axis=1)

    LISTA_EST = list(df.apply(
        lambda row: row['direct'], axis=1))

    print(LISTA_EST)

    return LISTA_EST

def tres_cavaleiros(api_conn, par, timeframe, periods=3):
    # Printar todos os parametros recebidos
    print(f"Meu par: {par}")
    print(f"Meu timeframe: {timeframe}")
    print(f"Meus periods: {periods}")

    timeframe = normalize_timeframe(timeframe)
    # Pega os dados do par e do timeframe
    velas = api_conn.get_candles(par, timeframe * 60, periods, time())

    df = pd.DataFrame(velas)
    df.rename(columns={"max": "high", "min": "low"}, inplace=True)

    df['direct'] = df.apply(lambda row: 'green' if (row['close'] - row['open'])
                            > 0 else 'red' if (row['close'] - row['open']) < 0 else 'grey', axis=1)

    LISTA_EST = list(df.apply(
        lambda row: row['direct'], axis=1))

    # remove o ultimo icone da lista

    print(LISTA_EST)

    return LISTA_EST

def end_of_second(api_conn, par, timeframe, periods=2):

    timeframe = normalize_timeframe(timeframe)
    if timeframe != 1:
        print("Timeframe inválido...Apenas pode ser utilizado o timeframe de 1 minuto")
        enviar_mensagem_telegram("Timeframe inválido...Apenas pode ser utilizado o timeframe de 1 minuto")
        return

    # Printar todos os parametros recebidos
    print(f"Meu par: {par}")
    print(f"Meu timeframe: {timeframe}")
    print(f"Meus periods: {periods}")

    # Pega os dados do par e do timeframe
    velas = api_conn.get_candles(par, timeframe * 60, periods, time())

    df = pd.DataFrame(velas)
    df.rename(columns={"max": "high", "min": "low"}, inplace=True)

    df['direct'] = df.apply(lambda row: 'green' if (row['close'] - row['open'])
                            > 0 else 'red' if (row['close'] - row['open']) < 0 else 'grey', axis=1)

    LISTA_EST = list(df.apply(
        lambda row: row['direct'], axis=1))

    # remove o ultimo icone da lista

    print(LISTA_EST)

    return LISTA_EST


def paridades(API, type_d):
    par = API.get_all_open_time()
    binario = []
    digital = []

    if type_d == 'binario':

        for paridade in par['turbo']:
            if par['turbo'][paridade]['open'] == True:
                binario.append(paridade)
        return binario

    if type_d == 'digital':
        for paridade in par['digital']:
            if par['digital'][paridade]['open'] == True:
                digital.append(paridade)
        return digital

    # Sobe um ciclo

def entrega_valor(lc):
    print("Escalando valor...")
    i_s = list(lc.proxima_posicao())
    print(f"Posição atual: {i_s}")
    alter_config("stage_ciclo", i_s)
    coin_n = get_one_data("valor_por_ciclo")[i_s[0]][i_s[1]]
    alter_config("valor_entry", coin_n)
    # alter_config("valor_entry", coin_n)
    return get_one_data("valor_entry")

def scale(itr):
    alter_config("stage_ciclo", list(itr.proxima_posicao()))
    ind_x = get_one_data("stage_ciclo")[0]
    ind_y = get_one_data("stage_ciclo")[1]
    alter_config("valor_entry", get_one_data("valor_por_ciclo")[ind_x][ind_y])
    print()
    print(f"Valor de entrada: {get_one_data('valor_entry')}")
    print()
    
def resetar(irt):
    irt.reset()
    alter_config("valor_entry", get_one_data("valor_por_ciclo")[0][0])
    alter_config("stage_ciclo", [0, 0])
    print()
    print(f"Valor de entrada: {get_one_data('valor_entry')}")
    print()
    print(f"Posição atual: {get_one_data('stage_ciclo')}")
    print()

def gerar_numero_aleatorio_float():
    # Gera um número float aleatório entre -1000 e 1000
    numero = get_one_data("valor_entry") * -1
    sleep(3)
    return myround(numero)

def operation_start(API, par_n, dir_n, durt, tipo_entrada, typecoin, lc):
    # Cria variavel mtg com valor 1
    mtg = -1

    # Pega o valor de qtd_martingale
    qtd_martingale = get_one_data("qtd_martingale")

    # Realiza entrada na paridade Binária (Turbo)
    def entrada_b(coin_n, par_n, dir_n, durt):
        status, id_code = API.buy(coin_n, par_n, dir_n, durt)
        luc_p = get_one_data("luc_prej")
        print(f"Entrada realizada no valor de: {coin_n}")
        print("\n************\n")
        print(f"Lucro/Prejuízo acumulado: {luc_p}")
        print("\n************\n")
        sleep(1)
        if status:
            print('Aguardando resultado...')
            print('\n')
            while True:
                check_close, win_money = API.check_win_v4(id_code)
                if check_close:
                    if float(win_money) > 0:
                        win_money = ("%.2f" % (win_money))
                        print("you win", win_money, "money")
                    else:
                        print(f"you loose {win_money}")
                    return float(win_money)
                    break

    # Realiza entrada na paridade Digital
    def entrada_d(coin_n, par_n, dir_n, durt):
        print(f"Entrada digital realizada..........1,2,3 - {datetime.now().strftime('%H:%M:%S')}")
        status, order_id = API.buy_digital_spot_v2(par_n, coin_n, dir_n, durt)
        print(f"Entrada realizada no valor de: {coin_n} - - {datetime.now().strftime('%H:%M:%S')}")
        print("\n************\n")
        print(f"Lucro/Prejuízo acumulado:{get_one_data('luc_prej')}")
        print("\n************\n")
        sleep(1)
        if status:
            print('Aguardando resultado...')
            print('\n')
            while True:
                check_close, win_money = API.check_win_digital_v2(order_id)
                if check_close:
                    if float(win_money) > 0:
                        win_money = ("%.2f" % (win_money))
                        print("you win", win_money, "money")
                    else:
                        print(f"you loose -{win_money}")
                    return float(win_money)
                    break

    # # Reseta o ciclo
    # def clear_all_steps():
    #     lc.pos_atual_x = 0
    #     lc.pos_atual_y = 0
    #     alter_config("stage_ciclo", [0, 0])
    #     alter_config("valor_entry", get_one_data("valor_por_ciclo")[0][0])
   
    print("---------------------- INICIO DA OPERAÇÃO -------------------")

    if typecoin == 'digital':
        print(f"Do tipo digital... - - {datetime.now().strftime('%H:%M:%S')}")

        scale(lc)
        while mtg <= qtd_martingale:
            print(f"Antes da entrada... - - {datetime.now().strftime('%H:%M:%S')}")
            result = entrada_d(get_one_data("valor_entry"), par_n, dir_n, durt)
            # result = gerar_numero_aleatorio_float()
            print("Resultado:", result)
            if result < 0:
                mtg += 1
                tot_luc_prej = round(get_one_data("luc_prej") + result,2)
                alter_config("luc_prej", myround(tot_luc_prej))
                print(f"🔴 Operação perdida no par {par_n} com direção {dir_n} | Martingale nº {mtg}🔴", f"Banca atual: {banca(API)} | Lucro/Prejuízo: {get_one_data('luc_prej')} | Valor de entrada: {get_one_data('valor_entry')}")
                enviar_mensagem_em_thread(f"🔴 Operação perdida no par {par_n} com direção {dir_n} | Martingale nº {mtg - 1}🔴", f"Banca atual: {banca(API)} | Lucro/Prejuízo: {get_one_data('luc_prej')} | Valor de entrada: {get_one_data('valor_entry')}")
                if not mtg == qtd_martingale:
                    scale(lc)
                else:
                    break


            elif result > 0:
    #           # Reseta o ciclo
                resetar(lc)
                mtg = 0
                tot_luc_prej = round(get_one_data("luc_prej") + result,2)
                alter_config("luc_prej", myround(tot_luc_prej))
                
                print(f"🟢 Operação ganha no par {par_n} com direção {dir_n} | Martingale nº {mtg}🟢", f"Banca atual: {banca(API)} | Lucro/Prejuízo: {get_one_data('luc_prej')} | Valor de entrada: {get_one_data('valor_entry')}")
                enviar_mensagem_em_thread(f"🟢 Operação ganha no par {par_n} com direção {dir_n} | Martingale nº {mtg}🟢", f"Banca atual: {banca(API)} | Lucro/Prejuízo: {get_one_data('luc_prej')} | Valor de entrada: {get_one_data('valor_entry')}")
                calibrar_entrada(API)
                break
            else:
                print(f"⚪ Operação empatada no par {par_n} com direção {dir_n} | Martingale nº {mtg} ⚪", f"Banca atual: {banca(API)} | Lucro/Prejuízo: {get_one_data('luc_prej')} | Valor de entrada: {get_one_data('valor_entry')}")
                enviar_mensagem_em_thread(f"⚪ Operação empatada no par {par_n} com direção {dir_n} | Martingale nº {mtg} ⚪", f"Banca atual: {banca(API)} | Lucro/Prejuízo: {get_one_data('luc_prej')} | Valor de entrada: {get_one_data('valor_entry')}")


if __name__ == '__main__':
    API = IQ_Option(os.getenv('EMAIL_IQPTION'),os.getenv('PASSWORD_IQPTION'))
    API.connect()
    typeacount = get_one_data("tipo_conta")
    API.change_balance(typeacount)  # PRACTICE / REAL

    if API.check_connect():
        print(' Conectado com sucesso!')
    else:
        print(' Erro ao conectar')
        input('\n\n Aperte enter para sair')
        sys.exit()

    # par_n, dir_n, durt, tipo_entrada, typecoin = 'EURUSD', 'call', 1, 'ciclo', 'digital'

    
    # print("Iniciando a população de Lista conttroladora")
    # lc = ListaControladora(get_one_data('valor_por_ciclo'))
    # print("Fim da população de Lista conttroladora")
    # operation_start(API, par_n, dir_n, durt, tipo_entrada, typecoin, lc)
    # while True:
    #     print(entrega_valor(lc))
    #     sleep(2)
    # print()
    # print(end_of_second(API, par_n, durt, 2))