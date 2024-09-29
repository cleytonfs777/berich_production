try:
    import os
    import sys
    sys.path.append(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))
except ModuleNotFoundError:
    ...
from threading import Thread
from messeger import enviar_mensagem_telegram
from colorama import Fore, init
from utils import *
from strategies import operation_start, sequencia_cinco, tres_cavaleiros, end_of_second, operation_ana_trader
from iqoptionapi.stable_api import IQ_Option
from handler import *
from dotenv import load_dotenv
import pandas as pd
from time import sleep, time
from datetime import datetime

# noqa: E402


# Inicializa o colorama
init(autoreset=True)  # O 'autoreset=True' fará com que cada print volte à cor padr

load_dotenv()


def mainbot():

    def enviar_mensagem_em_thread(*mensagens):
        t = Thread(target=enviar_mensagem_telegram, args=mensagens)
        t.start()

    def get_data(par, timeframe, periods=200):

        velas = API.get_candles(par, timeframe * 60, periods, time())

        df = pd.DataFrame(velas)
        df.rename(columns={"max": "high", "min": "low"}, inplace=True)

        return df

    def formatatms(tms):
        return datetime.fromtimestamp(tms).strftime('%H:%M:%S')

    def banca():
        return round(API.get_balance(), 2)

    def pair_open(API, par, tipo):

        paridades = API.get_all_open_time()
        binario = []
        digital = []

        if tipo == 'binaria':
            for paridade in paridades['turbo']:
                if paridades['turbo'][paridade]['open'] == True:
                    binario.append(paridade)
            if par in binario:
                return True
            else:
                return False
        elif tipo == 'digital':
            for paridade in paridades['digital']:
                if paridades['digital'][paridade]['open'] == True:
                    digital.append(paridade)
            if par in digital:
                return True
            else:
                return False

    ##########################################################################################

    API = IQ_Option(os.getenv('EMAIL_IQPTION'), os.getenv('PASSWORD_IQPTION'))
    API.connect()

    configs = all_configs()

    API.change_balance(configs['tipo_conta'])  # PRACTICE / REAL

    if API.check_connect():
        print(' Conectado com sucesso!')
    else:
        print(' Erro ao conectar')
        input('\n\n Aperte enter para sair')
        sys.exit()

    banca_value = banca()

    value_stop_gain = round(banca_value * configs['porcentagem_stop_win'], 2)
    value_stop_loss = round(
        banca_value * configs['porcentagem_stop_loss'], 2) * -1

    alter_config('banca', banca_value)
    changed_on()
    # Insere o valor inicial de entrada
    alter_config('valor_entry', get_one_data('valor_por_ciclo')[0][0])
    alter_config('luc_prej', 0)
    alter_config('firstis', True)

    INITIAL_LOOP = True
    par = configs['pares_favoritos'][0]
    timeframe = normalize_timeframe(configs['timeframe'])
    if configs['estrategia_principal'] == 'media_simples':
        periods = 14
        tyme_avg = 'SMA'
        dfg = get_data(par, timeframe, 500)
        dec = 7 - len(str(dfg.iloc[-1]['close']).split('.')[0])
    print(Fore.YELLOW + f"""
                            ┌────────────────────────────────────────────────────────────────┐
                            │░█░█░█▀█░█░░░█░█░█▀▀░█▀▀░░░█▀▄░█▀▀░█▀▄░▀█▀░█▀▀░█░█░░░█▀▄░█▀█░▀█▀│
                            │░█▄█░█░█░█░░░▀▄▀░█▀▀░▀▀█░░░█▀▄░█▀▀░█▀▄░░█░░█░░░█▀█░░░█▀▄░█░█░░█░│
                            │░▀░▀░▀▀▀░▀▀▀░░▀░░▀▀▀░▀▀▀░░░▀▀░░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀░▀░░░▀▀░░▀▀▀░░▀░│
                            └────────────────────────────────────────────────────────────────┘
                #########################################################################################
                #   BANCA : {banca_value}  #   GAIN : {value_stop_gain}   #   LOSS: {value_stop_loss}   #
                #                                                                                       #
                #########################################################################################
    """)
    # Inicial reset. Deve ser resetado valor_entry e stage_ciclo
    calibrar_entrada(API)
    alter_config("valor_entry", get_one_data("valor_por_ciclo")[0][0])
    alter_config("stage_ciclo", [0, 0])

    # Semaforo para a estratégia da Banda de Bolinger
    sem_bb = (False, False)

    # Dicionario da Ana Trader
    ana_dict = all_ana_configs()

    inital_config = True
    lista_ll = get_one_data('valor_por_ciclo')
    itr = IteradorPosicoes(lista_ll)
    entrar, direction = (False, 'call')

    while True:

        # Verifica se o bot está habilitado
        if is_enabled():

            if is_changed():
                print("\nAtualiza configurações...")
                # itr = IteradorPosicoes(lista_ll)
                # lista_ll = get_one_data('valor_por_ciclo')
                changed_off()
                configs = all_configs()
                if configs['estrategia_principal'] == 'ana_trader':
                    actly_values(
                        API, configs['pares_favoritos'][0], configs['timeframe'])

                if configs['estrategia_principal'] == 'media_simples':
                    periods = 14
                    tyme_avg = 'SMA'
                    dfg = get_data(configs['pares_favoritos'][0], normalize_timeframe(
                        configs['timeframe']), 500)
                    dec = 7 - len(str(dfg.iloc[-1]['close']).split('.')[0])

                if not pair_open(API, configs['pares_favoritos'][0], configs['typecoin']):
                    print(
                        f'{Fore.RED}Paridade {configs["pares_favoritos"][0]} não está aberta...{Fore.RESET}')
                    enviar_mensagem_em_thread(
                        f"⚠️ Paridade {configs['pares_favoritos'][0]} não está aberta... ⚠️")
                    alter_config("status", "off")
                    continue
                changed_off()
                print("Fim de leitura de paridades e desligando mundanças...")

            # Verifica se houve alteração nas configurações

            if configs['estrategia_principal'] == 'paula':
                qtd_velas = 200
                entrar, direction = check_IA_bollinger(
                    API, configs['pares_favoritos'][0], configs['timeframe'], qtd_velas)

            elif configs['estrategia_principal'] == 'teste':

                if permited_time("general_permissions"):
                    print("É tempo permitido *****")
                    entrar, direction = (True, 'call')

            elif configs['estrategia_principal'] == 'ana_trader':
                if ana_dict["firstis"] or is_ana_time_permited():
                    actly_values(
                        API, configs['pares_favoritos'][0], configs['timeframe'])
                entrar, direction = operation_ana_trader(
                    API, configs['pares_favoritos'][0], configs['timeframe'])
            else:
                entrar, direction = (False, 'call')

            if entrar:
                enviar_mensagem_em_thread(f" Realizada entrada no par {configs['pares_favoritos'][0]} com direção {direction}",
                                          f" Banca atual: {banca()} | Lucro/Prejuízo: {get_one_data('luc_prej')} | Valor de entrada: {get_one_data('valor_entry')}")
                print("Realizando operacao - ",
                      datetime.now().strftime("%H:%M:%S"))
                operation_start(API, get_one_data(
                    'pares_favoritos')[0], direction, normalize_timeframe(configs['timeframe']), get_one_data('tipo_entrada'), get_one_data('typecoin'), itr)
                # Verifica se não bateu o Stop Gain
                if get_one_data('luc_prej') >= value_stop_gain:
                    enviar_mensagem_em_thread(
                        f"🤑 Você bateu o Stop Gain de {value_stop_gain} e o bot foi desligado 🤑")
                    alter_config("status", "off")
                if get_one_data('luc_prej') <= value_stop_loss:
                    enviar_mensagem_em_thread(
                        f"😭 Você bateu o Stop Loss de {value_stop_loss} e o bot foi desligado. Seu prejuízo é: {get_one_data('luc_prej')*-1} 😭")
                    alter_config("status", "off")
                changed_on()

                entrar = False

            print(
                f'\rRastreado Opotunidades...   {datetime.now().strftime("%H:%M:%S")}', end='')

        else:
            print(
                f'\rApenas monitorando...   {datetime.now().strftime("%H:%M:%S")}', end='')
            # Zera o lucro/prejuízo
            alter_config('luc_prej', 0)
            # Aqui o bot apenas monitora
            if is_changed():
                print("\nAtualiza configurações...")
                changed_off()
                configs = all_configs()

        # Aguarda 1 segundo para a próxima iteração
        sleep(1)


if __name__ == '__main__':
    mainbot()
