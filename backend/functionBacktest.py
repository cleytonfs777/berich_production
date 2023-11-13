
from utils import ListaControladora, get_one_data, normalize_entry, myround
import datetime
import random


def analise_maioria(lista, banca):
    ciclos = get_one_data('qtd_ciclos')
    win_count = 0
    loss_count = 0
    list_win = []
    list_loss = []
    seq_loss = 0
    quebra_banca = 0
    entradas = get_one_data('valor_por_ciclo')
    luc_prej = 0
    lc = ListaControladora(entradas)
    pct_ganho = 0.89
    arr_qb = []
    i = 0
    j = 0
    qtd_martingale = get_one_data('qtd_martingale')
    permited_gale = True

    while i < len(lista) - 3:
        print("\n")

        tres_primeiros = lista[i:i+3]
        quarto = lista[i+3]
        
        # Conta quantas vezes cada cor aparece nos três primeiros
        count_red = sum(1 for cor, _ in tres_primeiros if cor == "red")
        count_green = sum(1 for cor, _ in tres_primeiros if cor == "green")
        
        # Verifica a cor da maioria
        if count_red > count_green:
            maior_cor = "red"
        elif count_red < count_green:
            maior_cor = "green"
        else:
            maior_cor = None

        if(maior_cor):

            while qtd_martingale >= j:
                try:
                    quarto = lista[i+j+3]
                    # Compara a cor da maioria com a cor do quarto elemento
                    if maior_cor == quarto[0]:
                        win_count += 1
                        list_win.append(quarto)
                        seq_loss = 0
                        posicao = lc.proxima_posicao()
                        lc.pos_atual_x = 0
                        lc.pos_atual_y = 0
                        luc_prej += entradas[posicao[0]][posicao[1]] * pct_ganho
                        luc_prej = myround(luc_prej)
                        print(f"Valor da entrada: {entradas[posicao[0]][posicao[1]]} - {quarto}")
                        print(f"Valor do retorno: {myround(entradas[posicao[0]][posicao[1]] * pct_ganho)}")
                        print(f"Valor do lucro/prejuízo: {luc_prej}")
                        j=0
                        print("Teste do segundo while: ", j < qtd_martingale)
                        print("Valor do j:", j)
                        print("Valor do qtd_martingale:", qtd_martingale)
                        break

                    else:
                        loss_count += 1
                        list_loss.append(quarto)
                        seq_loss += 1
                        posicao = lc.proxima_posicao()
                        luc_prej -= entradas[posicao[0]][posicao[1]]
                        luc_prej = myround(luc_prej)
                        print(f"Valor da entrada: {entradas[posicao[0]][posicao[1]]}  - {quarto}")
                        print(f"Valor do retorno: {entradas[posicao[0]][posicao[1]]*-1}")
                        print(f"Valor do lucro/prejuízo: {luc_prej}")
                        j+=1
                        if luc_prej * -1 > banca:
                            quebra_banca += 1
                            arr_qb.append(quarto)
                            seq_loss = 0
                        print("Teste do segundo while: ", j < qtd_martingale)
                        print("Valor do j:", j)
                        print("Valor do qtd_martingale:", qtd_martingale)
                except:
                    break

        # Avança para o quarto elemento para a próxima análise
        j = 0
        i += 3
        print("Teste do primeiro while: ", i < len(lista) - 3)

    return win_count, loss_count, list_win, list_loss, quebra_banca, round(luc_prej), arr_qb

def filtro_tempo(lista):
    # Valores válidos após os :
    validos = ["00", "15", "30", "45"]

    # Itera sobre a lista de tuplas
    for i, (cor, tempo) in enumerate(lista):
        minuto = tempo.split(':')[1]
        if minuto in validos:
            print(lista[i:])
            return lista[i:]
    print([])
    return []

def back_sequencia_cinco(candles_all, banca, tipo_entrada='ciclo', lmt=1):
   
    lmt = int(lmt) if lmt else 1
    entradas = get_one_data('valor_por_ciclo')
    lc = ListaControladora(entradas)
    qtd_martingale = get_one_data('qtd_martingale')
    luc_prej = 0
    q_banca = 0
    is_entry = 'False'
    placar = [0,0]
    count = 1
    count_mtg = 0
    quebra_banca = [False,[]]
    win_count = 0
    loss_count = 0
    list_win = []
    list_loss = []
    for candle in candles_all:
        print(f"Valor de count_mtg na {count} vez:", count_mtg)
        if is_entry == 'Truegreen':
            print(f"Acumulou {placar[0]} verdes na {count}ª Vez - Candle: {candle}")

            posicao = lc.proxima_posicao() 
            coin_entry = entradas[posicao[0]][posicao[1]]
            coin_entry = myround(coin_entry)

            print("Valor da entrada: ", coin_entry)
            if candle[0] == 'red':
                luc_prej += myround(coin_entry * 0.8)
                luc_prej = myround(luc_prej)
                print(f"Lucro de {coin_entry} na {count}ª Vez")
                print(f"Lucro/Prejuízo: {luc_prej} na {count}ª Vez - Candle: {candle}")
                win_count += 1
                list_win.append(candle)

                is_entry = 'False'
                print("Dentro de Win")
                print(f"Contagem de Margingale: {count_mtg}")
                print(f"Quantidade de Margingale: {qtd_martingale}")
                count_mtg = 0
                lc.pos_atual_x = 0
                lc.pos_atual_y = 0

            elif candle[0] == 'green':
                print("Dentro de Loss")
                print(f"Contagem de Margingale: {count_mtg}")
                print(f"Quantidade de Margingale: {qtd_martingale}")
                
                if count_mtg >= qtd_martingale:
                    print("count_mtg >= qtd_martingale:", count_mtg >= qtd_martingale)
                    count_mtg = 0
                    print("Valor de count_mtg:", count_mtg)
                    placar = [0, 0]
                    is_entry = 'False'
                else:
                    count_mtg += 1
                    print("Valor de count_mtg:", count_mtg)

                luc_prej -= coin_entry
                luc_prej = myround(luc_prej)

                if (luc_prej * -1) > banca:
                    quebra_banca[0] = True
                    quebra_banca[1].append(candle)

                loss_count += 1
                list_loss.append(candle)

                print(f"Prejuízo de {coin_entry} na {count}ª Vez - Candle: {candle}"
                )
                print(f"Lucro/Prejuízo: {luc_prej} na {count}ª Vez")



        elif is_entry == 'Truered':

            print(f"Acumulou {placar[1]} vermelhos na {count}ª Vez - Candle: {candle}") 
            posicao = lc.proxima_posicao() 
            coin_entry = entradas[posicao[0]][posicao[1]]
            coin_entry = myround(coin_entry)

            print("Valor da entrada: ", coin_entry)
            if candle[0] == 'green':
                luc_prej += myround(coin_entry * 0.8)
                luc_prej = myround(luc_prej)
                print(f"Lucro de {myround(coin_entry * 0.8)} na {count}ª Vez")
                print(f"Lucro/Prejuízo: {luc_prej} na {count}ª Vez - Candle: {candle}")
                win_count += 1
                list_win.append(candle)
                is_entry = 'False'
                print("Dentro de Win")
                print(f"Contagem de Margingale: {count_mtg}")
                print(f"Quantidade de Margingale: {qtd_martingale}")
                count_mtg = 0
                lc.pos_atual_x = 0
                lc.pos_atual_y = 0

            elif candle[0] == 'red':
                print("Dentro de Loss")
                print(f"Contagem de Margingale: {count_mtg}")
                print(f"Quantidade de Margingale: {qtd_martingale}")
                print("count_mtg >= qtd_martingale:", count_mtg >= qtd_martingale)
                if count_mtg >= qtd_martingale:
                    count_mtg = 0
                    print("Valor de count_mtg:", count_mtg)
                    placar = [0, 0]
                    is_entry = 'False'

                luc_prej -= myround(coin_entry)
                luc_prej = myround(luc_prej)


                if (luc_prej * -1) > banca:
                    quebra_banca[0] = True
                    quebra_banca[1].append(candle)

                loss_count += 1
                list_loss.append(candle)

                print(f"Prejuízo de {coin_entry} na {count}ª Vez - Candle: {candle}"
                )
                print(f"Lucro/Prejuízo: {luc_prej} na {count}ª Vez")
                count_mtg += 1

        if candle[0] == 'green':
            placar[0] += 1
            placar[1] = 0
        elif candle[0] =='red':
            placar[1] += 1
            placar[0] = 0
        print(f"Valor de lmt: {lmt}")
        if placar[0] >= lmt:
            is_entry = 'Truegreen'
        elif placar[1] >= lmt:
            is_entry = 'Truered'

        print(f"is_entry: {is_entry}")
        count += 1
        print(f"Placar: {placar}")
        
    return win_count, loss_count, list_win, list_loss, quebra_banca, myround(luc_prej), []
        
def back_tres_cavaleiros(candles_all, banca, tipo_entrada='ciclo'):
    # candles_all = teste_gera_candle('EURUSD-OTC', 5, 50)
    return analise_maioria(filtro_tempo(candles_all), banca)

def back_quatro_jump_2(candles_all, banca, tipo_entrada='ciclo', lmt=4):

    def retorna_valor(lc: ListaControladora, entradas: list = None):
        ind = lc.proxima_posicao()
        return entradas[ind[0]][ind[1]]

    def reset_lc(lc: ListaControladora):
        lc.reset()

    def sumvalues(lst):
        return sum(sum(sublst) for sublst in lst)

    def teste_operacao(j, lc, entradas, qtd_mtg, activate, luc_prej):
        nonlocal candles_all
        nonlocal qtd_wins
        nonlocal qtd_loss
        nonlocal list_win
        nonlocal list_loss

        count_mtg = 0
        while count_mtg <= qtd_mtg:
            entrada = retorna_valor(lc, entradas)
            print(f"Entrada no valor de {entrada} no candle {candles_all[j]}")
            if candles_all[j][0] == activate:
                result = myround(entrada * 0.7)
                print(f"Lucro de {result}")
                list_win.append(candles_all[j])
                j += 1
                luc_prej += result
                reset_lc(lc)
                qtd_wins += 1
                break
            else:
                result = myround(entrada) * -1
                luc_prej += result
                list_loss.append(candles_all[j])
                print(f"Prejuízo de {result}")
                count_mtg += 1
                j += 1
                qtd_loss += 1

        return j, luc_prej
    
    semaforo = [0,0] # a posição 0 irá catalogar os 'greens' e a posição 1 os 'reds'

    entradas = get_one_data("valor_por_ciclo")
    lc = ListaControladora(entradas)
    counter_value = [False, 0]
    activate = None
    i = 0
    qtd_mtg = get_one_data('qtd_martingale')
    luc_prej = 0
    qtd_wins = 0
    qtd_loss = 0
    list_win, list_loss, q_banca, arr_q = [], [], 0, []
    print(f"""
        #### INICIANDO O BOT ####
        Banca: {banca}
        Quantidade de Martingales: {qtd_mtg}\n\n\n""")
    while i < len(candles_all):

        print("Candle: ", candles_all[i])

        if counter_value[1] == 2:
            i, luc_prej = teste_operacao(i, lc, entradas, qtd_mtg, activate, luc_prej)
            luc_prej = myround(luc_prej)
            print(f"Lucro/Prejuízo Total: {luc_prej}")
            print(f"O valor da banca é {banca} e o valor de lucro e prejuizo é {luc_prej}, portanto a sentença luc_prej >= banca é {(luc_prej * -1) >= banca}")
            if (luc_prej * -1) >= banca:
                q_banca += 1
                print(f"Quebrou a banca. Quantidade de quebras de banca é: {q_banca}")
                arr_q.append(candles_all[i])
            counter_value = [False, 0]
            activate = None
            continue

        if activate == 'green' or activate == 'red':
            counter_value[0] = True
            counter_value[1] += 1
            print(f"Esse é o {counter_value[1]}º candle")

        else:

            # Conferencia de cores
            if candles_all[i][0] == 'green':
                semaforo[0] += 1
                semaforo[1] = 0

            elif candles_all[i][0] == 'red':
                semaforo[1] += 1
                semaforo[0] = 0

            elif candles_all[i][0] == 'grey':
                semaforo = [0,0]

            if semaforo[0] == lmt:
                print("Entrou no green")
                activate = 'green'
                semaforo = [0,0]

            elif semaforo[1] == lmt:
                print("Entrou no red")
                activate = 'red'
                semaforo = [0,0]


        print("Placar: ", semaforo)
        i += 1



    return qtd_wins, qtd_loss, list_win, list_loss, q_banca, luc_prej, arr_q

def back_end_of_second(candles_all, banca, tipo_entrada='ciclo', lmt=4):

    def retorna_valor(lc: ListaControladora, entradas: list = None):
        ind = lc.proxima_posicao()
        return entradas[ind[0]][ind[1]]

    def reset_lc(lc: ListaControladora):
        lc.reset()

    def teste_operacao(j, lc, entradas, qtd_mtg, luc_prej):

        nonlocal candles_all
        nonlocal qtd_wins
        nonlocal qtd_loss
        nonlocal list_win
        nonlocal list_loss
        k=j
        count_mtg = 0
        while count_mtg <= qtd_mtg:
            entrada = retorna_valor(lc, entradas)
            print(f"Entrada no valor de {entrada} no candle {candles_all[j+2]}")
            print("Comparando o candle ", candles_all[k], " com o candle ", candles_all[j + 2])
            if candles_all[k][0] == candles_all[j + 2][0]:
                result = myround(entrada * 0.7)
                print(f"Lucro de {result}")
                list_win.append(candles_all[j+2])
                j += 2
                luc_prej += result
                reset_lc(lc)
                qtd_wins += 1
                break
            else:
                result = myround(entrada) * -1
                luc_prej += result
                list_loss.append(candles_all[j])
                print(f"Prejuízo de {result}")
                count_mtg += 1
                j += 1
                qtd_loss += 1
    
        

        return j, luc_prej
    

    entradas = get_one_data("valor_por_ciclo")
    lc = ListaControladora(entradas)
    counter_value = [False, 0]
    activate = None
    i = 0
    qtd_mtg = get_one_data('qtd_martingale')
    luc_prej = 0
    qtd_wins = 0
    qtd_loss = 0
    list_win, list_loss, q_banca, arr_q = [], [], 0, []
    print(f"""
        #### INICIANDO O END OF SECOND ####
        Banca: {banca}
        Quantidade de Martingales: {qtd_mtg}
        Lista de Entradas: {entradas}
        \n\n\n""")
    
    new_candles_all = [(cor, horario[:-3]) for cor, horario in candles_all]
    print("Candles All N: ", new_candles_all)
    
    while i < len(new_candles_all):
        try:
            print("Candle: ", new_candles_all[i])
            if int(new_candles_all[i][1][-1:]) == 9 or int(new_candles_all[i][1][-1:]) == 4:
                print(" Analisando o candle ", new_candles_all[i])
                i, luc_prej = teste_operacao(i, lc, entradas, qtd_mtg, luc_prej)


            i += 1
        except:
            break


    return qtd_wins, qtd_loss, list_win, list_loss, q_banca, round(luc_prej, 2), arr_q

def generate_time_sequence(hour_init: str, hour_end: str) -> list:
    # Converte as strings de horário para objetos datetime
    start_time = datetime.datetime.strptime(hour_init, "%H:%M")
    end_time = datetime.datetime.strptime(hour_end, "%H:%M")

    print(start_time)
    print(end_time)
    minutes = 1
    # Lista que armazenará as tuplas
    result = []

    # Loop para gerar a lista de tuplas
    while start_time <= end_time:
        # Escolhe aleatoriamente entre 'red' e 'green'
        color = random.choice(['red', 'green'])
        
        # Adiciona a tupla (cor, horário) à lista
        result.append((color, start_time.strftime("%H:%M")))
        
        # Incrementa o horário em 5 minutos
        start_time += datetime.timedelta(minutes=minutes)

    return result

if __name__ == '__main__':
    lista = [('red', '06:00'), ('red', '06:01'), ('red', '06:02'), ('red', '06:03'), ('green', '06:04'), ('red', '06:05'), ('green', '06:06'), ('green', '06:07'), ('green', '06:08'), ('green', '06:09'), ('green', '06:10'), ('red', '06:11'), ('green', '06:12'), ('red', '06:13'), ('red', '06:14'), ('green', '06:15'), ('red', '06:16'), ('red', '06:17'), ('red', '06:18'), ('green', '06:19'), ('red', '06:20'), ('green', '06:21'), ('red', '06:22'), ('red', '06:23'), ('green', '06:24'), ('red', '06:25'), ('green', '06:26'), ('green', '06:27'), ('green', '06:28'), ('green', '06:29'), ('red', '06:30'), ('green', '06:31'), ('green', '06:32'), ('red', '06:33'), ('red', '06:34'), ('red', '06:35'), ('green', '06:36'), ('green', '06:37'), ('green', '06:38'), ('green', '06:39'), ('red', '06:40'), ('green', '06:41'), ('red', '06:42'), ('green', '06:43'), ('red', '06:44'), ('red', '06:45'), ('green', '06:46'), ('green', '06:47'), ('green', '06:48'), ('red', '06:49'), ('red', '06:50'), ('green', '06:51'), ('red', '06:52'), ('green', '06:53'), ('red', '06:54'), ('green', '06:55'), ('red', '06:56'), ('red', '06:57'), ('red', '06:58'), ('green', '06:59'), ('red', '07:00')]

    print("Estou dentro da função...")

    print("RESULTADOS...", back_end_of_second(lista , 280))


