import sys
import os
current_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(current_dir)
from backend.handler import * 

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

if __name__ == '__main__':
    print(banca_min())