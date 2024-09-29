
import numpy as np
import datetime
import random
from backend.utils import ListaControladora, calcular_bandas_bollinger, get_one_data, myround
import pandas as pd


# #####################       NOVAS FUNÇÕES A IMPLEMENTAR     #######################


def back_bollinger_bands(candles_all, banca):

    # Função para retornar o valor de entrada no ciclo Martingale
    def retorna_valor(lc: ListaControladora, entradas: list = None):
        ind = lc.proxima_posicao()
        return entradas[ind[0]][ind[1]]

    # Função para resetar o ciclo Martingale após vitória
    def reset_lc(lc: ListaControladora):
        lc.reset()

    # Função para testar a operação com Martingale, aplicando a lógica de Bollinger
    def teste_operacao(i, lc, entradas, qtd_mtg, luc_prej, tipo_operacao):

        nonlocal candles_all
        nonlocal qtd_wins
        nonlocal qtd_loss
        nonlocal list_win
        nonlocal list_loss
        nonlocal arr_qb
        count_mtg = 0  # Contador de Martingales
        j = i  # Índice do candle atual para progressão de Martingale

        while count_mtg <= qtd_mtg:
            entrada = retorna_valor(lc, entradas)
            proximo_candle_open = candles_all['open'][j + 2]
            proximo_candle_close = candles_all['close'][j + 2]
            proximo_candle_time = candles_all['time'][j + 2]

            # Verifica o resultado da operação com base no tipo (CALL ou PUT)
            if (tipo_operacao == 'CALL' and proximo_candle_close > proximo_candle_open) or \
               (tipo_operacao == 'PUT' and proximo_candle_close < proximo_candle_open):
                # Vitória na operação
                lucro = myround(entrada * 0.89)
                luc_prej += lucro
                qtd_wins += 1
                list_win.append({
                    'open': proximo_candle_open,
                    'close': proximo_candle_close,
                    'time': proximo_candle_time
                })
                print(
                    f"Vitória com {tipo_operacao}, entrada: {entrada}, lucro: {lucro}")
                reset_lc(lc)
                break
            else:
                # Derrota na operação
                prejuizo = myround(entrada) * -1
                luc_prej += prejuizo
                qtd_loss += 1
                list_loss.append({
                    'open': proximo_candle_open,
                    'close': proximo_candle_close,
                    'time': proximo_candle_time
                })
                print(
                    f"Derrota com {tipo_operacao}, entrada: {entrada}, prejuízo: {prejuizo}")
                count_mtg += 1
                j += 1

            # Verifica se houve quebra de banca
            if luc_prej * -1 >= banca:
                arr_qb.append({
                    'open': proximo_candle_open,
                    'close': proximo_candle_close,
                    'time': proximo_candle_time
                })
                print(f"Banca quebrada no candle {proximo_candle_time}")
                break

        return j, luc_prej

    # Variáveis de controle e configuração
    entradas = get_one_data("valor_por_ciclo")
    lc = ListaControladora(entradas)
    qtd_martingale = get_one_data('qtd_martingale')
    luc_prej = 0  # Acumulador de lucro/prejuízo
    qtd_wins = 0
    qtd_loss = 0
    quebra_banca = 0
    list_win = []
    list_loss = []
    arr_qb = []
    loss_registradas = set()

    print(f"Esse é o Valor de AllCandles: {candles_all}")

    i = 0  # Índice para iterar pelos candles
    while i < len(candles_all['close']) - 1:
        # Extrair os valores dos candles atuais
        candle_anterior_close = candles_all['close'][i]
        candle_atual_close = candles_all['close'][i + 1]
        banda_sup = calcular_bandas_bollinger(candles_all)['upper_band'][i]
        banda_inf = calcular_bandas_bollinger(candles_all)['lower_band'][i]
        candle_time_atual = candles_all['time'][i + 1]

        # Condição de entrada para CALL (banda inferior)
        if candle_anterior_close < banda_inf and candle_atual_close > banda_inf:
            print(f"Analisando operação CALL no candle {candle_time_atual}")
            i, luc_prej = teste_operacao(
                i, lc, entradas, qtd_martingale, luc_prej, 'CALL')

        # Condição de entrada para PUT (banda superior)
        elif candle_anterior_close > banda_sup and candle_atual_close < banda_sup:
            print(f"Analisando operação PUT no candle {candle_time_atual}")
            i, luc_prej = teste_operacao(
                i, lc, entradas, qtd_martingale, luc_prej, 'PUT')

        # Verificar quebra de banca
        if luc_prej * -1 >= banca:
            quebra_banca += 1
            print(f"Banca quebrada no candle {candle_time_atual}")
            break

        # Avançar para o próximo candle
        i += 1

    return qtd_wins, qtd_loss, list_win, list_loss, quebra_banca, round(luc_prej, 2), arr_qb


def analisar_resultado(proximo_candle, direcao):
    if direcao == 'call' and proximo_candle['close'] > proximo_candle['open']:
        return 'vitoria'
    elif direcao == 'put' and proximo_candle['close'] < proximo_candle['open']:
        return 'vitoria'
    else:
        return 'derrota'


if __name__ == '__main__':
    # lista = [('red', '06:00'), ('red', '06:01'), ('red', '06:02'), ('red', '06:03'), ('green', '06:04'), ('red', '06:05'), ('green', '06:06'), ('green', '06:07'), ('green', '06:08'), ('green', '06:09'), ('green', '06:10'), ('red', '06:11'), ('green', '06:12'), ('red', '06:13'), ('red', '06:14'), ('green', '06:15'), ('red', '06:16'), ('red', '06:17'), ('red', '06:18'), ('green', '06:19'), ('red', '06:20'), ('green', '06:21'), ('red', '06:22'), ('red', '06:23'), ('green', '06:24'), ('red', '06:25'), ('green', '06:26'), ('green', '06:27'), ('green', '06:28'), ('green', '06:29'),
    #          ('red', '06:30'), ('green', '06:31'), ('green', '06:32'), ('red', '06:33'), ('red', '06:34'), ('red', '06:35'), ('green', '06:36'), ('green', '06:37'), ('green', '06:38'), ('green', '06:39'), ('red', '06:40'), ('green', '06:41'), ('red', '06:42'), ('green', '06:43'), ('red', '06:44'), ('red', '06:45'), ('green', '06:46'), ('green', '06:47'), ('green', '06:48'), ('red', '06:49'), ('red', '06:50'), ('green', '06:51'), ('red', '06:52'), ('green', '06:53'), ('red', '06:54'), ('green', '06:55'), ('red', '06:56'), ('red', '06:57'), ('red', '06:58'), ('green', '06:59'), ('red', '07:00')]

    # print("Estou dentro da função...")

    # print("RESULTADOS...", back_end_of_second(lista, 280))

    ...
