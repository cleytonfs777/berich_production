import json
import os
from datetime import datetime
from iqoptionapi.stable_api import IQ_Option
from dotenv import load_dotenv
import pandas as pd
from time import sleep, time
from backend.handler import alter_config, get_one_data, alter_ana_config, get_one_ana, all_ana_configs
import sys
import numpy as np

load_dotenv()


class ListaControladora:
    def __init__(self, lista_maior):
        self.lista_maior = lista_maior
        self.x = len(lista_maior) - 1
        if lista_maior:
            self.y = len(lista_maior[-1]) - 1
        else:
            self.y = -1

        self.pos_atual_x = 0
        self.pos_atual_y = 0

    def proxima_posicao(self):
        # Caso a lista maior esteja vazia
        if self.x < 0 or self.y < 0:
            return (0, 0)

        # Retorna a posição atual
        resultado = (self.pos_atual_x, self.pos_atual_y)

        # Atualiza para a próxima posição
        if self.pos_atual_y < len(self.lista_maior[self.pos_atual_x]) - 1:
            self.pos_atual_y += 1
        elif self.pos_atual_x < self.x:
            self.pos_atual_x += 1
            self.pos_atual_y = 0
        else:
            # Se a lista menor da última posição da lista maior tiver tamanho 1
            if len(self.lista_maior[self.x]) == 1 and self.pos_atual_y == 0:
                self.pos_atual_x = 0
                self.pos_atual_y = 0
            # Se atingir o limite máximo
            elif self.pos_atual_y == self.y:
                self.pos_atual_x = 0
                self.pos_atual_y = 0
            else:
                self.pos_atual_y += 1

        return resultado

    def reset(self):

        self.pos_atual_x = 0
        self.pos_atual_y = 0


class IteradorPosicoes:
    def __init__(self, lista):
        self.lista = lista
        self.num_listas, self.elementos_ultima_lista = self.analisa_listas(
            lista)
        self.i = 0
        self.j = 0

    def analisa_listas(self, lista_principal):
        if not lista_principal:
            return (0, 0)
        numero_de_listas = len(lista_principal)
        elementos_ultima_lista = len(lista_principal[-1])
        return (numero_de_listas, elementos_ultima_lista)

    def proxima_posicao(self):
        if self.i < self.num_listas:
            posicao_atual = (self.i, self.j)
            self.j += 1
            if self.j >= len(self.lista[self.i]):
                self.j = 0
                self.i += 1
                if self.i >= self.num_listas:
                    self.i = 0
            return posicao_atual
        else:
            self.reset()
            return self.proxima_posicao()

    def reset(self):
        self.i = 0
        self.j = 0


def myround(value):
    return float("{:.2f}".format(round(value * 100) / 100))


def formatatms(tms):
    return datetime.fromtimestamp(tms).strftime('%H:%M:%S')


def banca(API):
    return round(API.get_balance(), 2)


def entrada_min():
    # Recupera o valor de ciclos e fator_martingale
    ciclos = get_one_data('qtd_ciclos')
    fator = get_one_data('fator_martingale')

    initial = 1
    total_banca = initial
    print(f"Entrada: {initial}")
    print(f"Total: {total_banca}")
    for i in range(1, ciclos):
        total_banca += round(initial * fator, 2)
        initial = round(initial * fator, 2)
        print(f"Entrada: {initial}")
        print(f"Total: {total_banca}")
    return round(total_banca, 2)


def normalize_timeframe(timeframe):
    if isinstance(timeframe, int):
        timeframe = str(timeframe)

    # Extrai apenas os números do timeframe
    timeframe_value = int(
        ''.join(char for char in timeframe if char.isdigit()))

    # Se o timeframe tiver 'h' depois do número, deve remover o 'h' e multiplicar o número por 60
    if 'h' in timeframe:
        timeframe_value *= 60

    # Se o timeframe tiver 'd' depois do número, deve remover o 'm' e multiplicar o número por 1440
    if 'd' in timeframe:
        timeframe_value *= 1440

    return timeframe_value


def normalize_entry(timeframe, period):

    if isinstance(timeframe, int):
        timeframe = str(timeframe)

    if isinstance(period, int):
        period = str(period)

    # Extrai apenas os números do timeframe
    timeframe_value = int(
        ''.join(char for char in timeframe if char.isdigit()))

    # Extrai apenas os números do period
    period_value = int(
        ''.join(char for char in period if char.isdigit()))

    # Se o timeframe tiver 'h' depois do número, deve remover o 'h' e multiplicar o número por 60
    if 'h' in timeframe:
        timeframe_value *= 60

    # Se o timeframe tiver 'd' depois do número, deve remover o 'm' e multiplicar o número por 1440
    if 'd' in timeframe:
        timeframe_value *= 1440

    # Se o timeframe tiver 'h' depois do número, deve remover o 'h' e multiplicar o número por 60
    if 'h' in period:
        period_value *= 60

    # Se o timeframe tiver 'd' depois do número, deve remover o 'm' e multiplicar o número por 1440
    if 'd' in period:
        period_value *= 1440

    period_f = period_value/timeframe_value
    period_f = round(period_f)

    print(f"Meu timeframe filtrado: {timeframe_value}")
    print(f"Meus periodos filtrado: {period_f}")

    result = []
    result.append(timeframe_value)
    result.append(period_f)

    return result


def permited_time(strategie):

    exact_second = 59

    if strategie == 'general_permissions':
        timef = get_one_data('timeframe')
        hour, min, seg = (datetime.now().strftime("%H:%M:%S")).split(':')

        if timef == '1m':
            if int(seg) >= exact_second:
                return True
            else:
                return False

        elif timef == '2m':
            min = min[-1]
            if (int(seg) >= exact_second) and (int(min) % 2 == 1):
                return True
            else:
                return False

        elif timef == '5m':
            min = min[-1]
            if (int(seg) >= exact_second) and (int(min) == 4 or int(min) == 9):
                return True
            else:
                return False

        elif timef == '15m':
            if (int(seg) >= exact_second) and (int(min) == 14 or int(min) == 29 or int(min) == 44 or int(min) == 59):
                return True
            else:
                return False

        elif timef == '30m':
            if (int(seg) >= exact_second) and (int(min) == 29 or int(min) == 59):
                return True
            else:
                return False

        elif timef == '1h':
            if (int(seg) >= exact_second) and (int(min) == 59):
                return True
            else:
                return False

        elif timef == '4h':
            if (int(seg) >= exact_second) and (int(min) == 59) and ((int(hour)+1) % 4 == 0):
                return True
            else:
                return False

        else:
            return False

    elif strategie == 'tres_cavaleiros':
        hour, min, seg = (datetime.now().strftime("%H:%M:%S")).split(':')
        if int(seg) >= exact_second and int(min) == 14 or int(seg) >= exact_second and int(min) == 29 or int(seg) >= exact_second and int(min) == 44 or int(seg) >= exact_second and int(min) == 59:
            return True
        else:
            return False

    elif strategie == 'end_of_second':
        hour, min, seg = (datetime.now().strftime("%H:%M:%S")).split(':')
        min = min[-1]
        if int(seg) >= exact_second and int(min) == 0 or int(seg) >= exact_second and int(min) == 5:
            return True
        else:
            return False

####################################


def ajuste_entrada(banca, ciclos=6, fator=2.5):
    # Recupera o valor de ciclos e fator_martingale a partir de variáveis externas
    ciclos = int(get_one_data('qtd_ciclos'))
    fator = float(get_one_data('fator_martingale'))

    # Calcular a soma da série geométrica
    soma_serie = sum(fator ** i for i in range(ciclos))

    # Calcular a primeira parte da banca
    primeira_parte = round(banca / soma_serie, 2)

    # Inicializar a lista de partes da banca com a primeira parte calculada
    partes_banca = [primeira_parte]

    # Calcular as partes restantes da banca, multiplicando progressivamente pelo fator
    for i in range(1, ciclos):
        partes_banca.append(round(partes_banca[-1] * fator, 2))

    # Verificar se a soma das partes é igual à banca, ajustando a última parte se necessário
    soma_partes = round(sum(partes_banca), 2)
    if soma_partes != banca:
        partes_banca[-1] += round(banca - soma_partes, 2)

    print(f"Partes da banca: {partes_banca}")

    # Retornar a lista de partes da banca
    return partes_banca


def agrupar_pares(lista):
    lista_pares = []
    for i in range(0, len(lista) - 1, 2):  # Avança de dois em dois
        lista_pares.append([lista[i], lista[i + 1]])

    if len(lista) % 2 != 0:  # Se a lista tem um número ímpar de elementos
        # Adiciona o último elemento como uma lista de um único elemento
        lista_pares.append([lista[-1]])

    return lista_pares


def portentagem_necessaria(banca, qtd_martingale, fator):
    n = qtd_martingale + 1  # Número total de divisões
    S = banca  # A soma total que queremos é o valor da banca

    # Calculando o primeiro termo
    a = S * (1 - fator) / (1 - fator**n)

    # Retornando a porcentagem do primeiro termo em relação à banca
    return round((a/banca) * 100, 2)


def banca_necessaria(qtd_martingale, fator, porcentagem):
    # Começamos assumindo um valor inicial de 1 para a primeira aposta
    primeiro_valor = 1
    resultado = [primeiro_valor]

    # Adicionando os próximos valores multiplicados pelo fator
    for i in range(qtd_martingale):
        proximo_valor = round(resultado[-1] * fator, 2)
        resultado.append(proximo_valor)

    # Agora, a soma total de resultado será o valor total que será descontado da banca
    # Dado que esse valor total é igual à porcentagem da banca, podemos encontrar a banca total
    total_necessario = round(sum(resultado), 2)

    return total_necessario


def ajuste_gale(martingale, fator, porcentagem, banca):
    # Calculando o primeiro valor baseado na porcentagem da banca
    primeiro_valor = myround((porcentagem / 100) * banca)
    print("Primeiro valor: ", primeiro_valor)
    if primeiro_valor < 1:
        return f"Erro: O primeiro valor é menor que 1! Para seus parametros é necessária uma banca de no mínimo U$ {banca_necessaria(martingale, fator, porcentagem)}"

    resultado = [primeiro_valor]

    # Adicionando os próximos valores multiplicados pelo fator
    for i in range(martingale):
        proximo_valor = round(resultado[-1] * fator, 2)
        resultado.append(proximo_valor)

    # Verificando se a soma dos valores em resultado não ultrapassa a banca
    if sum(resultado) > banca:
        return f"Erro: A soma dos valores ultrapassa a banca!\nValores: {resultado}\nBanca: {banca}\n Voce pode ajustar sua porcentagem para {round(portentagem_necessaria(banca, martingale, fator),2)}%"

    return resultado


def calibrar_entrada(API=None) -> str:
    if not API:

        API = IQ_Option(os.getenv('EMAIL_IQPTION'),
                        os.getenv('PASSWORD_IQPTION'))
        API.connect()

        API.change_balance(get_one_data('tipo_conta'))  # PRACTICE / REAL

        if API.check_connect():
            print(' Conectado com sucesso!')
        else:
            print(' Erro ao conectar')
            input('\n\n Aperte enter para sair')
            sys.exit()

    banca_value = banca(API)

    # Vefirica se a chave 'tipo_entrada' é igual a ciclo
    if get_one_data('tipo_entrada') == 'ciclo':
        # Executa a função banca e salva na variável "banca_value"
        print(f"Banca: {banca_value}")
        ciclos = ajuste_entrada(banca_value)

        if int(ciclos[0]) < 1:

            return f"Para que seja possivel realizar {ciclos} ciclos é necessario ter no minimo banca de U$ {entrada_min(ciclos)}"

        lista_fim = agrupar_pares(ciclos)

        # Alterando o valor
        lista_fim[-1][-1] = myround(lista_fim[-1][-1])

        alter_config('valor_por_ciclo', lista_fim)

        # Ajusta o valor da banca
        alter_config('banca', banca_value)

        return "Dados ajustados com sucesso!!"

    elif get_one_data('tipo_entrada') == 'martingale':

        # Inicia buscando quantidade de martingale, fator de martingale e porcentagem de entrada

        martingale = get_one_data('qtd_martingale')
        fator = get_one_data('fator_martingale')
        porcentagem = get_one_data('pct_entrada')

        list_gale = ajuste_gale(martingale, fator, porcentagem, banca_value)

        if int(list_gale[0]) < 1:

            return f"Para que seja possivel realizar {list_gale} gales é necessario ter no minimo banca de U$ {banca_necessaria(martingale, fator, porcentagem)}"

        lista_fim = agrupar_pares(list_gale)

        # Alterando o valor
        lista_fim[-1][-1] = round(lista_fim[-1][-1], 2)

        alter_config('valor_por_ciclo', lista_fim)

        # Ajusta o valor da banca
        alter_config('banca', banca_value)

        return "Dados ajustados com sucesso!!"


def calcular_bandas_bollinger(dados, periodo=14, nbdevup=2.0, nbdevdn=2.0):
    """
    Calcula as Bandas de Bollinger para um conjunto de dados de ações.

    Parâmetros:
    dados (dict): Dicionário contendo arrays NumPy para os preços de abertura, alta, baixa, fechamento e volume.
    periodo (int): Número de períodos para a média móvel.
    nbdevup (float): Número de desvios padrão para a banda superior.
    nbdevdn (float): Número de desvios padrão para a banda inferior.

    Retorna:
    dict: Dicionário original com arrays adicionais para as Bandas de Bollinger.
    """
    fechamento = dados['close']
    media_movel = np.convolve(
        fechamento, np.ones(periodo)/periodo, mode='valid')
    desvio_padrao = np.array([np.std(fechamento[i-periodo:i])
                             for i in range(periodo, len(fechamento) + 1)])

    upper_band = media_movel + (desvio_padrao * nbdevup)
    lower_band = media_movel - (desvio_padrao * nbdevdn)

    # Preparar os arrays para terem o mesmo tamanho dos dados originais
    n = len(fechamento)
    dados['upper_band'] = np.concatenate(
        [np.full(n - len(upper_band), np.nan), upper_band])
    dados['lower_band'] = np.concatenate(
        [np.full(n - len(lower_band), np.nan), lower_band])
    dados['ma'] = np.concatenate(
        [np.full(n - len(media_movel), np.nan), media_movel])

    return dados


def paratimestamp(data='01/01/2023', tempo="10:30"):
    full_data = f"{data} {tempo}"
    retultado = datetime.strptime(full_data, "%d/%m/%Y %H:%M")
    resultado1 = datetime.timestamp(retultado)

    return resultado1


def is_ana_time_permited():
    hora = datetime.now().strftime("%H:%M:%S")
    if int(hora[-2:]) >= 1 and int(hora[-5:-3]) == 0:
        print("Atualizando configurações...")
        print("Segundo: ", hora[-2:])
        print("Minuto: ", hora[-5:-3])
        return True
    else:
        return False


def min_time_ana():
    hora = datetime.now().strftime("%H:%M:%S")
    if int(hora[-2:]) <= 30 and int(hora[-5:-3]) <= 2:
        print("Tempo permitido")
        print("Segundo: ", hora[-2:])
        print("Minuto: ", hora[-5:-3])
        return True
    else:
        return False
###################################################################### STRATEGIES ######################################################################


def check_IA_bollinger(api_cn, par, timeframe, velas_q=100):
    timeframe = normalize_timeframe(timeframe)
    print('Verificando as bandas de bollinger...')
    print(f"""
    Paridade: {par}
    Timeframe: {timeframe}
    Velas: {velas_q}
    """)

    velas1 = api_cn.get_candles(par, timeframe*60, 2, time())
    print("Resultado das Velas", velas1)
    dec = 7 - len(str(velas1[-1]['close']).split('.')[0])

    velas_q += 1  # Pegando velas adicionais para monitorar sequência
    valores_bandas = []  # Array para armazenar os valores das bandas e candles

    while True:
        # Verifica o momento certo para rodar a função
        if not permited_time("general_permissions"):
            sleep(1)
            continue

        # Pega os dados das velas para calcular as bandas de bollinger
        velas = api_cn.get_candles(par, timeframe * 60, velas_q, time())

        dados_f = {
            'open': np.empty(velas_q),
            'high': np.empty(velas_q),
            'low': np.empty(velas_q),
            'close': np.empty(velas_q),
            'volume': np.empty(velas_q)
        }

        for x in range(0, velas_q):
            dados_f['open'][x] = velas[x]['open']
            dados_f['high'][x] = velas[x]['max']
            dados_f['low'][x] = velas[x]['min']
            dados_f['close'][x] = velas[x]['close']
            dados_f['volume'][x] = velas[x]['volume']

        dados_f_total = calcular_bandas_bollinger(dados_f)
        banda_sup = round(dados_f_total['upper_band'][-1], dec)
        banda_inf = round(dados_f_total['lower_band'][-1], dec)

        # Armazenando os valores das bandas e candles no array
        valores_bandas.append({
            'open': round(velas[-1]['open'], dec),
            'close': round(velas[-1]['close'], dec),
            'high': round(velas[-1]['max'], dec),
            'low': round(velas[-1]['min'], dec),
            'banda_sup': banda_sup,
            'banda_inf': banda_inf
        })

        # Print dos valores das bandas e candles armazenados
        print(f"""
        Candle Atual:
        Abertura: {velas[-1]['open']}
        Fechamento: {velas[-1]['close']}
        Máxima: {velas[-1]['max']}
        Mínima: {velas[-1]['min']}
        Banda Superior: {banda_sup}
        Banda Inferior: {banda_inf}
        """)

        # Verifica se temos pelo menos dois candles para comparação
        if len(valores_bandas) >= 2:
            candle_anterior = valores_bandas[-2]
            candle_atual = valores_bandas[-1]

            # Print para verificar os valores do candle anterior e atual
            print(f"""
            Analisando padrão...
            Candle Anterior - Abertura: {candle_anterior['open']}, Fechamento: {candle_anterior['close']}, Banda Superior: {candle_anterior['banda_sup']}, Banda Inferior: {candle_anterior['banda_inf']}
            Candle Atual - Abertura: {candle_atual['open']}, Fechamento: {candle_atual['close']}, Banda Superior: {candle_atual['banda_sup']}, Banda Inferior: {candle_atual['banda_inf']}
            """)

            # Verifica o padrão para a banda inferior (Call)
            if candle_anterior['close'] < candle_anterior['banda_inf']:  # Fechou fora
                # Fechou dentro
                if candle_atual['close'] > candle_atual['banda_inf']:
                    print("Padrão para 'CALL' detectado.")
                    return True, 'call'

            # Verifica o padrão para a banda superior (Put)
            elif candle_anterior['close'] > candle_anterior['banda_sup']:  # Fechou fora
                # Fechou dentro
                if candle_atual['close'] < candle_atual['banda_sup']:
                    print("Padrão para 'PUT' detectado.")
                    return True, 'put'

        sleep(3)  # Pausa para evitar processamento excessivo


def actly_values(API, par, timeframe, velas_q=100):

    h1 = 60
    h4 = 240

    timeframe = normalize_timeframe(timeframe)

    configs_h1 = all_ana_configs()["h1"]
    configs_h4 = all_ana_configs()["h4"]

    # print("Configurações de H1", configs_h1)
    # print("Configurações de H4", configs_h4)

    velas_h4 = API.get_candles(par, h4 * 60, 2, time())
    velas_h1 = API.get_candles(par, h1 * 60, 4, time())
    sup_h1_1 = velas_h1[-2]['max']
    configs_h1["sup"][0] = sup_h1_1
    sup_h1_2 = velas_h1[-3]['max']
    configs_h1["sup"][1] = sup_h1_2
    sup_h1_3 = velas_h1[-4]['max']
    configs_h1["sup"][2] = sup_h1_3
    inf_h1_1 = velas_h1[-2]['min']
    configs_h1["inf"][0] = inf_h1_1
    inf_h1_2 = velas_h1[-3]['min']
    configs_h1["inf"][1] = inf_h1_2
    inf_h1_3 = velas_h1[-4]['min']
    configs_h1["inf"][2] = inf_h1_3
    sup_h4_1 = velas_h4[-2]['max']
    configs_h4["sup"] = sup_h4_1
    inf_h4_1 = velas_h4[-2]['min']
    configs_h4["inf"] = inf_h4_1

    alter_ana_config("h1", configs_h1)
    alter_ana_config("h4", configs_h4)
    alter_ana_config("firstis", False)


if __name__ == '__main__':

    API = IQ_Option(os.getenv('EMAIL_IQPTION'), os.getenv('PASSWORD_IQPTION'))
    API.connect()

    actly_values(API, 'EURUSD-OTC', 5)
