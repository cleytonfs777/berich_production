import json
import os
from datetime import datetime
from iqoptionapi.stable_api import IQ_Option
from dotenv import load_dotenv
import pandas as pd
from time import sleep, time
from handler import alter_config, get_one_data
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
        self.num_listas, self.elementos_ultima_lista = self.analisa_listas(lista)
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
    for i in range(1,ciclos):
        total_banca += round(initial * fator,2)
        initial = round(initial * fator,2)
        print(f"Entrada: {initial}")
        print(f"Total: {total_banca}")
    return round(total_banca, 2)

def sequencia_cinco(api_conn, par, timeframe, periods=6):
    timeframe_n, period_n = normalize_entry(timeframe, periods)
    
    # Printar todos os parametros recebidos
    print(f"Meu par: {par}")
    print(f"Meu timeframe: {timeframe}")
    print(f"Meu timeframe novo: {timeframe_n}")
    print(f"Meus periods: {period_n}")

    # Pega os dados do par e do timeframe
    velas = api_conn.get_candles(par, timeframe_n * 60, period_n, time())
    print("pegou as velas...")

    df = pd.DataFrame(velas)
    df.rename(columns={"max": "high", "min": "low"}, inplace=True)

    df['direct'] = df.apply(lambda row: 'green' if (row['close'] - row['open'])
                            > 0 else 'red' if (row['close'] - row['open']) < 0 else 'grey', axis=1)

    LISTA_EST = list(df.apply(
        lambda row: row['direct'], axis=1))

    return LISTA_EST

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

    print(f"Meu timeframe filtrado: {timeframe_value}")
    print(f"Meus periodos filtrado: {period_f}")

    result = []
    result.append(timeframe_value)
    result.append(round(period_f))

    return result

def check_colors(my_list, strategie):
    print("Entrou em checkcolors...")

    if strategie == 'sequencia_cinco':
        if all(item == 'red' for item in my_list):
            return True, 'call'
        elif all(item == 'green' for item in my_list):
            return True, 'put'
        else:
            return False, 'nothing'

    elif strategie == 'quatro_jump_2':
    # Verifica se os quatro primeiros elementos da lista my_list são iguais
        if my_list[0] == my_list[1] == my_list[2] == my_list[3]:
            # Verifica se o primeiro elemento da lista é 'red'
            if my_list[0] == 'red':
                return True, 'put'
            # Verifica se o primeiro elemento da lista é 'green'
            elif my_list[0] == 'green':
                return True, 'call'
            # Se não for nem 'red' nem 'green', retorna False e 'nothing'
            else:
                return False, 'nothing'
        else:
            return False, 'nothing'
        
    elif strategie == 'end_of_second':
        print("Essa é a minha lista: ", my_list )
        if my_list[0] == "green":
            return True, 'call'
        
        elif my_list[0] == "red":
            return True, 'put'
        else:
            return False, 'nothing'


    elif strategie == 'tres_cavaleiros':

        if 'grey' in my_list:
            return False, 'nothing'
        if my_list[0] == my_list[1] or my_list[0] == my_list[2]:
            return True, 'call' if my_list[0] == 'green' else 'put'
        else:
            return True, 'call' if my_list[1] == 'green' else 'put'

def permited_time(strategie):

    if strategie == 'general_permissions':
        timef = get_one_data('timeframe')
        hour, min, seg = (datetime.now().strftime("%H:%M:%S")).split(':')

        if timef == '1m':
            if int(seg) >= 58:
                return True
            else:
                return False
            
        elif timef == '2m':
            min = min[-1]
            if (int(seg) >= 58) and (int(min) % 2 == 1):
                return True
            else:
                return False
            
        elif timef == '5m':
            min = min[-1]
            if (int(seg) >= 58) and (int(min) == 4 or int(min) == 9):
                return True
            else:
                return False
            
        elif timef == '15m':
            if (int(seg) >= 58) and (int(min) == 14 or int(min) == 29 or int(min) == 44 or int(min) == 59):
                return True
            else:
                return False
            
        elif timef == '30m':
            if (int(seg) >= 58) and (int(min) == 29 or int(min) == 59):
                return True
            else:
                return False
            
        elif timef == '1h':
            if (int(seg) >= 58) and (int(min) == 59):
                return True
            else:
                return False
            
        elif timef == '4h':
            if (int(seg) >= 58) and (int(min) == 59) and ((int(hour)+1) % 4 == 0):
                return True
            else:
                return False
            
        else:
            return False

    elif strategie == 'tres_cavaleiros':
        hour, min, seg = (datetime.now().strftime("%H:%M:%S")).split(':')
        if int(seg) >= 58 and int(min) == 14 or int(seg) >= 58 and int(min) == 29 or int(seg) >= 58 and int(min) == 44 or int(seg) >= 58 and int(min) == 59:
            return True
        else:
            return False
        
    elif strategie == 'end_of_second':
        hour, min, seg = (datetime.now().strftime("%H:%M:%S")).split(':')
        min = min[-1]
        if int(seg) >= 58 and int(min) == 0 or int(seg) >= 58 and int(min) == 5:
            return True
        else:
            return False

def ajustable_time():
    timef = get_one_data('timeframe')
    hour, min, seg = (datetime.now().strftime("%H:%M:%S")).split(':')

    if timef == '1m':
        if int(seg) >= 1 and int(seg) <= 2:
            return True
    elif timef == '5m':
        min = min[-1]
        if int(seg) >= 1 and int(seg) <= 2 and (int(min) == 5 or int(min) == 0):
            return True
        else:
            return False
    elif timef == '15m':
        if int(seg) >= 1 and int(seg) <= 2 and (int(min) == 15 or int(min) == 30 or int(min) == 45 or int(min) == 0):
            return True
        else:
            return False
    elif timef == '30m':
        if int(seg) >= 1 and int(seg) <= 2 and (int(min) == 30 or int(min) == 0):
            return True
        else:
            return False
    elif timef == '1h':
        if int(seg) >= 1 and int(seg) <= 2 and (int(min) == 0):
            return True
        else:
            return False
    elif timef == '4h':
        if int(seg) >= 1 and int(seg) <= 2 and (int(min) == 0) and ((int(hour)+1) % 4 == 0):
            return True
        else:
            return False
    else:
        return False

def autociclo_run(banca=0, min_value=1, positions=6):

    lista = [round(min_value * 2.5 ** x, 2) for x in range(6)]
    if banca < lista:
        return False
    else:
        #     cicle_new = [ x for x]
        print(lista)

####################################

def ajuste_entrada(banca, ciclos=6, fator=2.5):
    # Recupera o valor de ciclos e fator_martingale
    ciclos = int(get_one_data('qtd_ciclos'))
    fator = float(get_one_data('fator_martingale'))

    # Calcular a soma da série geométrica
    soma_serie = sum([fator ** i for i in range(ciclos)])
    
    # Calcular a primeira parte da banca
    primeira_parte = round(banca / soma_serie, 2)
    
    # Inicializar a lista de partes da banca
    partes_banca = [primeira_parte]
    
    # Calcular as partes restantes da banca
    for i in range(1, ciclos):
        partes_banca.append(round(partes_banca[-1] * fator, 2))
    
    # Verificar se a soma das partes é igual à banca
    # Se não for, ajustar a última parte
    soma_partes = sum(partes_banca)
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
        lista_pares.append([lista[-1]])  # Adiciona o último elemento como uma lista de um único elemento
        
    return lista_pares

def portentagem_necessaria(banca, qtd_martingale, fator):
    n = qtd_martingale + 1  # Número total de divisões
    S = banca  # A soma total que queremos é o valor da banca
    
    # Calculando o primeiro termo
    a = S * (1 - fator) / (1 - fator**n)
    
    # Retornando a porcentagem do primeiro termo em relação à banca
    return round((a/banca) * 100,2)

def banca_necessaria(qtd_martingale, fator, porcentagem):
    # Começamos assumindo um valor inicial de 1 para a primeira aposta
    primeiro_valor = 1
    resultado = [primeiro_valor]

    # Adicionando os próximos valores multiplicados pelo fator
    for i in range(qtd_martingale):
        proximo_valor = round(resultado[-1] * fator,2)
        resultado.append(proximo_valor)

    # Agora, a soma total de resultado será o valor total que será descontado da banca
    # Dado que esse valor total é igual à porcentagem da banca, podemos encontrar a banca total
    total_necessario = round(sum(resultado),2)


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
        proximo_valor = round(resultado[-1] * fator,2)
        resultado.append(proximo_valor)

    # Verificando se a soma dos valores em resultado não ultrapassa a banca
    if sum(resultado) > banca:
        return f"Erro: A soma dos valores ultrapassa a banca!\nValores: {resultado}\nBanca: {banca}\n Voce pode ajustar sua porcentagem para {round(portentagem_necessaria(banca, martingale, fator),2)}%"
    
    return resultado

def calibrar_entrada(API=None)-> str:
    if not API:
        
        API = IQ_Option(os.getenv('EMAIL_IQPTION'),os.getenv('PASSWORD_IQPTION'))
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

###################################################################### STRATEGIES ######################################################################

def check_bolinger_bands(API, par, timeframe, velas_q=100):
    velas1 = API.get_candles(par, 60, 2, time())
    dec = 7 - len(str(velas1[-1]['close']).split('.')[0])
    while True:
        # Pega os dados das velas para calcular as bandas de bollinger
        velas = API.get_candles(par, 60, velas_q, time())
        dados_f = {
            'open': np.empty(velas_q),
            'high': np.empty(velas_q),
            'low': np.empty(velas_q),
            'close': np.empty(velas_q),
            'volume': np.empty(velas_q)
	    }



if __name__ == '__main__':
    # Exemplo
    banca = 100
    qtd_martingale = 5
    fator = 2
    pct_entrada = 1.58
    print(ajuste_gale(qtd_martingale, fator, pct_entrada, banca))
    # print(portentagem_necessaria(banca, qtd_martingale, fator))  # Isso imprimirá a porcentagem da primeira divisão em relação à banca
