import json
import os
from time import sleep

# Encontre o caminho do diretório atual
current_dir = os.path.dirname(os.path.realpath(__file__))

# Construa o caminho do arquivo db.json
db_path_main = os.path.join(current_dir, 'database.json')


def get_one_data(chave):
    # Lendo o arquivo JSON
    with open(db_path_main) as json_file:
        data = json.load(json_file)

    # Imprimindo os dados
    return data[chave]

def all_configs():
    # Lendo o arquivo JSON
    with open(db_path_main) as json_file:
        data = json.load(json_file)

    # Imprimindo os dados
    return data

def alter_config(chave, valor):
    # Lendo o arquivo JSON
    with open(db_path_main) as json_file:
        data = json.load(json_file)

    # Verifica se a chave informada existe
    if chave not in data:
        return False

    # Alterando o valor
    data[chave] = valor

    # Escrevendo no arquivo JSON
    with open(db_path_main, 'w') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    return data

def is_enabled():
    # Lendo o arquivo JSON
    with open(db_path_main) as json_file:
        data = json.load(json_file)

    # Verifica se o bot está habilitado ou não
    if data['status'] == 'on':
        return True
    else:
        return False

def is_changed():
    # Lendo o arquivo JSON
    with open(db_path_main) as json_file:
        data = json.load(json_file)

    # Verifica se o bot está habilitado ou não
    return data['changed']

def changed_on():
    # Lendo o arquivo JSON
    with open(db_path_main) as json_file:
        data = json.load(json_file)

    data['changed'] = True

    # Escrevendo no arquivo JSON
    with open(db_path_main, 'w') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    return data

def changed_off():
    # Lendo o arquivo JSON
    with open(db_path_main) as json_file:
        data = json.load(json_file)

    data['changed'] = False

    # Escrevendo no arquivo JSON
    with open(db_path_main, 'w') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    return data

def scale_one_step():
    # Confere ind_main e ind_sec
    ind_ = get_one_data("valor_por_ciclo")
    ind_main = len(ind_) - 1
    ind_sec = len(ind_[0]) - 1

    print(f"ind_main: {ind_main}")
    print(f"ind_sec: {ind_sec}")

    # Aumenta um nível no ciclo implementado
    # x, y = (0, 0)
    x, y = get_one_data("stage_ciclo")
    if x > 1:
        if y > 0:
            alter_config("stage_ciclo", [0, 0])
            return True
        else:
            y += 1
    else:
        if y > 0:
            x, y = (x + 1, 0)
        else:
            y += 1

    alter_config("stage_ciclo", [x, y])
    return False

def clear_all_steps(lc):
    # Reseta o ciclo para o nivel (0, 0)
    alter_config("stage_ciclo", [0, 0])
    lc.pos_atual_x = 0
    lc.pos_atual_y = 0

def change_special(boolvalue, chave):
    # Lendo o arquivo JSON
    with open(db_path_main) as json_file:
        data = json.load(json_file)

    data['changed'] = boolvalue
    data['target'] = chave

    # Escrevendo no arquivo JSON
    with open(db_path_main, 'w') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    return data

##### HANDLER ANA TRADER

db_ana_database = os.path.join(current_dir, 'ana_database.json')

def get_one_ana(chave):
    # Lendo o arquivo JSON
    with open(db_ana_database) as json_file:
        data = json.load(json_file)

    # Imprimindo os dados
    return data[chave]

def all_ana_configs():
    # Lendo o arquivo JSON
    with open(db_ana_database) as json_file:
        data = json.load(json_file)

    # Imprimindo os dados
    return data

def alter_ana_config(chave, valor):
    # Lendo o arquivo JSON
    with open(db_ana_database) as json_file:
        data = json.load(json_file)

    # Verifica se a chave informada existe
    if chave not in data:
        return False

    # Alterando o valor
    data[chave] = valor

    # Escrevendo no arquivo JSON
    with open(db_ana_database, 'w') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    return data
if __name__ == '__main__':
    while True:
        result = scale_one_step()
        print(result)
        sleep(2)
