import os


def formatCiclo(numeros):
    try:
        # Divida a string pelo delimitador ";"
        grupos = numeros.split(';')

        # Para cada grupo, divida pelo delimitador "," e converta para inteiros
        listas = [[num for num in grupo.split(',')] for grupo in grupos]

        # Retorna a lista de listas
        return listas
    except:
        return False


def is_numeric_point(s):
    try:
        num = float(s)
        return True if num >= 0 else False
    except ValueError:
        return False


def form_ciclo_view(texto):
    print(f"tamanho: {len(texto)}")
    msg_f = ''
    for i in range(len(texto)):
        msg_f += f"{i+1}º C - {texto[i]} "

    return str(msg_f)


def percent_to_float(percent):
    return float(percent.replace('%', '')) / 100


def float_to_percent(float):
    return f"{float * 100}%"


def split_pairs(pairs):
    try:
        return pairs.split(',')
    except:
        return False


if __name__ == '__main__':
    print(os.getcwd())
