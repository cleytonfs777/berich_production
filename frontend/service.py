import json
import os
from dotenv import load_dotenv
from iqoptionapi.stable_api import IQ_Option
import sys
current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_dir)
from backend.handler import *

load_dotenv()

# Encontre o caminho do diretório atual



# Construa o caminho do arquivo db.json
db_path = os.path.join(current_dir, '..', 'backend', 'database.json')


def banca():

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
        return

    return round(API.get_balance(), 2)


def banca_min():

    lista = [[1, 2.5], [6.25, 15.62], [39.05, 97.62]]


    print(lista)
    # Contar o total de elementos em todas as listas
    num_elementos = sum(len(sublista) for sublista in lista)

    print("Número de elementos:", num_elementos)
    
    # Definir o fator
    fator = float(get_one_data('fator_martingale'))
    
    # Calcular o valor total
    init = 0
    total = 0
    for _ in range(num_elementos):
        if init == 0:
            init = 1
            total += init
        else:
            init = round(init * fator, 2)       
            total += init
            total = round(total, 2)
        print("Valor de init:", init)
        print("Valor de total:", total)
    return total

def atualiza_banca():
    atual = banca()
    alter_config('banca', atual)
    return atual


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
    return partes_banca, sum(partes_banca)


def ligar_desligar():
    sinal = get_one_data('status')

    # Alterando o valor
    sinal = "on" if sinal == "off" else "off"

    # Escrevendo no arquivo JSON
    alter_config('status', sinal)

    if sinal == "on":
        return "✅ Robô ligado com sucesso!! ✅"
    else:
        return "☑ Robô desligado com sucesso!! ☑"


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


def agrupar_pares(lista):
    lista_pares = []
    for i in range(0, len(lista) - 1, 2):  # Avança de dois em dois
        lista_pares.append([lista[i], lista[i + 1]])

    if len(lista) % 2 != 0:  # Se a lista tem um número ímpar de elementos
        lista_pares.append([lista[-1]])  # Adiciona o último elemento como uma lista de um único elemento
        
    return lista_pares


def calibrar_entrada()-> str:

    # Recupera o valor da chave "valor_por_ciclo"
    valor_por_ciclo = get_one_data('valor_por_ciclo')

    # Executa a função banca e salva na variável "banca_value"
    banca_value = banca()
    get_one_data("tipo_entrada")

    print(f"Banca: {banca_value}")
    ciclos, valor_t = ajuste_entrada(banca_value)

    if int(ciclos[0]) < 1:

        return f"Para que seja possivel realizar {ciclos} ciclos é necessario ter no minimo banca de U$ {entrada_min(ciclos)}"
    
    lista_fim = agrupar_pares(ciclos)

    # Alterando o valor
    lista_fim[-1][-1] = round(lista_fim[-1][-1], 2)

    alter_config('valor_por_ciclo', lista_fim)

    # Ajusta o valor da banca
    alter_config('banca', banca_value)

    return "Dados ajustados com sucesso!!"


if __name__ == "__main__":
    banca_min()
