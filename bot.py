from frontend.utils_f import *
from frontend.service import all_configs, alter_config, ligar_desligar, banca
from frontend.operations import *
from backend.utils import calibrar_entrada
from backend.backtest import backtest_maker
from backend.senderbot import paridades
from time import sleep
from pyrogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                            Message, ReplyKeyboardMarkup)
from pyrogram import Client, filters
from dotenv import load_dotenv
from asyncio import run
import os
import sys
caminho = os.path.join(os.getcwd(), 'backend')
sys.path.append(caminho)

load_dotenv()

# TODO
#    IMPLEMENTAR VERIFICAÇÃO DE NUMERO DE GALES COM ESTRATEGIA


# Adicione um dicionário para guardar as mensagens enviad
sent_messages = {}


class MyClient(Client):
    def __init__(self):
        # Inicialize o objeto Client e defina a variável de sessão
        super().__init__(
            "BeRichBot",
            api_id=os.environ['TELEGRAM_API_ID'],
            api_hash=os.environ['TELEGRAM_API_HASH'],
            bot_token=os.environ['TELEGRAM_BOT_TOKEN'],
        )
        self.user_data = {}

    # Adicione um método para atualizar a variável de sessão com os dados do usuário
    def update_user_data(self, user_id, data):
        self.user_data[user_id] = data

    # Adicione um método para recuperar os dados do usuário da variável de sessão
    def get_user_data(self, user_id):
        return self.user_data.get(user_id, {})


def registra_sess_data(app, user_id, data_res, chave):
    # Registra todos os dados na variavel de sessão
    user_data = app.get_user_data(user_id)
    user_data[chave] = data_res
    app.update_user_data(user_id, user_data)


def refresh_config():
    obj_comp = all_configs()
    ciclo_view = form_ciclo_view(obj_comp['valor_por_ciclo'])
    reply_markup_text = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Status: {obj_comp['status']}", callback_data="status_edit"),
         InlineKeyboardButton(f"Tipo: {obj_comp['tipo_entrada']}", callback_data="tipo_entrada_edit")],
        [InlineKeyboardButton(f"Qtd MG: {obj_comp['qtd_martingale']}", callback_data="qtd_martingale_edit"),
         InlineKeyboardButton(f"FT MG: {obj_comp['fator_martingale']}", callback_data="fator_martingale_edit")],
        [InlineKeyboardButton(f"Corretora: {obj_comp['corretora']}", callback_data="corretora_edit"),
         InlineKeyboardButton(f"Qtd Ciclos: {obj_comp['qtd_ciclos']}", callback_data="qtd_ciclos_edit")],
        [InlineKeyboardButton(
            ciclo_view, callback_data="valor_por_ciclo_edit")],
        [InlineKeyboardButton(f"Vlr Entry: {obj_comp['pct_entrada']}", callback_data="pct_entrada_edit"),
         InlineKeyboardButton(f"SG: {float_to_percent(obj_comp['porcentagem_stop_win'])}", callback_data="porcentagem_stop_win_edit")],
        [InlineKeyboardButton(f"SL: {float_to_percent(obj_comp['porcentagem_stop_loss'])}", callback_data="porcentagem_stop_loss_edit"),
         InlineKeyboardButton(f"Coin: {obj_comp['pares_favoritos']}", callback_data="pares_favoritos_edit")],
        [InlineKeyboardButton(f"timeframe: {obj_comp['timeframe']}", callback_data="timeframe_edit"),
         InlineKeyboardButton(f"Estratégia: {obj_comp['estrategia_principal']}", callback_data="estrategia_principal_edit")],
        [InlineKeyboardButton(f"Tipo Conta: {obj_comp['tipo_conta']}", callback_data="tipo_conta_edit"),
         InlineKeyboardButton(f"Tipo Moeda: {obj_comp['typecoin']}", callback_data="typecoin_edit")],
        [InlineKeyboardButton(f"Auto Ciclo: {obj_comp['autociclo']}", callback_data="autociclo_edit"),
         InlineKeyboardButton(f"Limite Candles: {obj_comp['lmt_candles']}", callback_data="lmt_candles_edit")],
    ])
    return reply_markup_text


# Crie o aplicativo
app = MyClient()


@app.on_message(filters.command('start'))
async def inicio(Client, message):
    registra_sess_data(app, message.from_user.id,
                       "", "active_edit")

    teclado = ReplyKeyboardMarkup(
        [
            [
                'Ligar/Desligar', 'Configurações', 'Calibrar'
            ],
            [
                'Painel', 'Backtest', 'Paridades'
            ]
        ], resize_keyboard=True
    )
    await message.reply(
        '🤖 Seja bem vindo ao bot de Operações em Opções Binárias. Escolha as opções abaixo 🤖', reply_markup=teclado
    )


@app.on_message(filters.regex("Ligar/Desligar"))
async def ligar(Client, message):
    interrupt = ligar_desligar()
    await app.send_message(message.chat.id, interrupt)


@app.on_message(filters.regex("Calibrar"))
async def ligar(Client, message):
    calibrar_entrada()
    await app.send_message(message.chat.id, "Entradas calibradas com sucesso!!")


@app.on_message(filters.regex("Paridades"))
async def painel(Client, message):
    await app.send_message(message.chat.id, "Analizando pares. Aguarde...")
    pares_open = paridades()
    await app.send_message(message.chat.id, pares_open)


@app.on_message(filters.regex("Painel"))
async def painel(Client, message):
    rotulo = render_template()
    await app.send_message(message.chat.id, rotulo)


@app.on_message(filters.regex("Backtest"))
async def backtest(Client, message):
    await app.send_message(message.chat.id, "Qual par deseja fazer o backtest?")
    registra_sess_data(app, message.from_user.id,
                       "coin_backtest", "active_edit")


@app.on_message(filters.regex("Configurações"))
async def configurar(Client, message):

    obj_comp = all_configs()
    ciclo_view = form_ciclo_view(obj_comp['valor_por_ciclo'])
    reply_markup_text = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Status: {obj_comp['status']}", callback_data="status_edit"),
         InlineKeyboardButton(f"Tipo: {obj_comp['tipo_entrada']}", callback_data="tipo_entrada_edit")],
        [InlineKeyboardButton(f"Qtd MG: {obj_comp['qtd_martingale']}", callback_data="qtd_martingale_edit"),
         InlineKeyboardButton(f"FT MG: {obj_comp['fator_martingale']}", callback_data="fator_martingale_edit")],
        [InlineKeyboardButton(f"Corretora: {obj_comp['corretora']}", callback_data="corretora_edit"),
         InlineKeyboardButton(f"Qtd Ciclos: {obj_comp['qtd_ciclos']}", callback_data="qtd_ciclos_edit")],
        [InlineKeyboardButton(
            ciclo_view, callback_data="valor_por_ciclo_edit")],
        [InlineKeyboardButton(f"Valor Ent: {obj_comp['pct_entrada']}", callback_data="pct_entrada_edit"),
         InlineKeyboardButton(f"SG: {float_to_percent(obj_comp['porcentagem_stop_win'])}", callback_data="porcentagem_stop_win_edit")],
        [InlineKeyboardButton(f"SL: {float_to_percent(obj_comp['porcentagem_stop_loss'])}", callback_data="porcentagem_stop_loss_edit"),
         InlineKeyboardButton(f"Coin: {obj_comp['pares_favoritos']}", callback_data="pares_favoritos_edit")],
        [InlineKeyboardButton(f"timeframe: {obj_comp['timeframe']}", callback_data="timeframe_edit"),
         InlineKeyboardButton(f"Estratégia: {obj_comp['estrategia_principal']}", callback_data="estrategia_principal_edit")],
        [InlineKeyboardButton(f"Tipo Conta: {obj_comp['tipo_conta']}", callback_data="tipo_conta_edit"),
         InlineKeyboardButton(f"Tipo Moeda: {obj_comp['typecoin']}", callback_data="typecoin_edit")],
        [InlineKeyboardButton(f"Auto Ciclo: {obj_comp['autociclo']}", callback_data="autociclo_edit"),
         InlineKeyboardButton(f"Limite Candles: {obj_comp['lmt_candles']}", callback_data="lmt_candles_edit")],
    ])

    sent_messages['config'] = await message.reply_text("Selecione o campo que deseja editar:", reply_markup=reply_markup_text)
    sent_messages['message_id'] = sent_messages['config'].id


@app.on_callback_query()
async def callback(clinet, callback_query):
    print("Conteudo da minha callback_query: ")
    print(callback_query.from_user.id)
    try:
        user_data = app.get_user_data(callback_query.from_user.id)
        print(user_data)
    except:
        print("Usuário não registrado")

    if callback_query.data.endswith("_edit"):

        if "status" in callback_query.data:
            await callback_query.answer("Você não tem permissão para editar esse campo!", show_alert=True)
            return
        elif "autociclo" in callback_query.data:
            # Se a variavel autociclo dentro do arquivo db.json estiver como on, altere para off, e caso seja off altere para on e replique para o usuario '🟢 Auto ciclo Ligado' ou '🔴 Auto ciclo Desligado'
            if all_configs()['autociclo'] == "on":
                alter_config("autociclo", "off")
                await callback_query.answer("🔴 Auto ciclo Desligado", show_alert=True)
            else:
                alter_config("autociclo", "on")
                await callback_query.answer("🟢 Auto ciclo Ligado", show_alert=True)

            # Deleta mensagem e altera a configuração
            await app.edit_message_reply_markup(
                chat_id=callback_query.message.chat.id,
                message_id=sent_messages['message_id'],
                reply_markup=refresh_config()
            )

        elif "tipo_entrada" in callback_query.data:
            reply_markup1 = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        f"Normal", callback_data="entr_normal"),
                    InlineKeyboardButton(f"Ciclo", callback_data="entr_ciclo"),
                    InlineKeyboardButton(
                        f"Martingale", callback_data="entr_martingale"),

                ]

            ])

            sent_message = await callback_query.message.reply_text("Escolha o tipo de sequencia de entradas", reply_markup=reply_markup1)

            sent_messages[callback_query.from_user.id] = sent_message

        elif "qtd_martingale" in callback_query.data:

            await callback_query.message.reply(f"Insira a quantidade de martingale que deseja usar:")
            registra_sess_data(app, callback_query.from_user.id,
                               "qtd_martingale", "active_edit")

        elif "lmt_candles" in callback_query.data:

            await callback_query.message.reply(f"Insira o limite de candles a serem analisados:")
            registra_sess_data(app, callback_query.from_user.id,
                               "lmt_candles", "active_edit")

        elif "qtd_ciclos" in callback_query.data:

            await callback_query.message.reply(f"Insira quantos ciclos deseja usar:")
            registra_sess_data(app, callback_query.from_user.id,
                               "qtd_ciclos", "active_edit")

        elif "fator_martingale" in callback_query.data:
            await callback_query.message.reply(f"Insira o fator de martingale que deseja usar:")
            registra_sess_data(app, callback_query.from_user.id,
                               "fator_martingale", "active_edit")

        elif "valor_por_ciclo" in callback_query.data:
            await callback_query.message.reply(f"Insira os valores por ciclo que deseja usar. Separe cada ciclo por ; e as entradas por , :")
            registra_sess_data(app, callback_query.from_user.id,
                               "valor_por_ciclo", "active_edit")
        elif "corretora" in callback_query.data:
            reply_markup2 = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        f"iqoption", callback_data="corr_iqoption"),
                    InlineKeyboardButton(
                        f"quotex", callback_data="corr_quotex"),
                    InlineKeyboardButton(
                        f"binomo", callback_data="corr_binomo"),

                ]

            ])

            await callback_query.message.reply_text("Escolha sua corretora", reply_markup=reply_markup2)

        elif "pct_entrada" in callback_query.data:

            await callback_query.message.reply(f"Insira a porcentagem de entrada que deseja usar:")
            registra_sess_data(app, callback_query.from_user.id,
                               "pct_entrada", "active_edit")

        elif "porcentagem_stop_win" in callback_query.data:

            await callback_query.message.reply(f"Insira a porcentagem de stopgain que deseja usar:")
            registra_sess_data(app, callback_query.from_user.id,
                               "porcentagem_stop_win", "active_edit")

        elif "porcentagem_stop_loss" in callback_query.data:

            await callback_query.message.reply(f"Insira a porcentagem de stoploss que deseja usar:")
            registra_sess_data(app, callback_query.from_user.id,
                               "porcentagem_stop_loss", "active_edit")

        elif "pares_favoritos" in callback_query.data:

            await callback_query.message.reply(f"Insira os pares que deseja operar. Separe cada par por , :")
            registra_sess_data(app, callback_query.from_user.id,
                               "pares_favoritos", "active_edit")

        elif "timeframe" in callback_query.data:

            reply_markup22 = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "1m", callback_data="1m_tmf"),
                    InlineKeyboardButton(
                        "2m", callback_data="2m_tmf"),
                    InlineKeyboardButton("5m", callback_data="5m_tmf"),

                ], [
                    InlineKeyboardButton(
                        "15m", callback_data="15m_tmf"),
                    InlineKeyboardButton(
                        "30m", callback_data="30m_tmf"),
                    InlineKeyboardButton(
                        "1h", callback_data="1h_tmf"),
                ]
            ])

            await callback_query.message.reply_text("Escolha o periodo de tempo que deseja analisar", reply_markup=reply_markup22)

        elif "estrategia_principal" in callback_query.data:

            reply_markup2 = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "paula", callback_data="paula_est"),
                ], [
                    InlineKeyboardButton(
                        "teste", callback_data="teste_est"),
                ]
            ])

            await callback_query.message.reply_text("Escolha a estratégia que deseja usar para fazer suas entradas", reply_markup=reply_markup2)

        elif "tipo_conta" in callback_query.data:
            reply_markup1 = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        f"Real", callback_data="taccount_real"),
                    InlineKeyboardButton(
                        f"Prática", callback_data="taccount_practice"),

                ]

            ])

            sent_message = await callback_query.message.reply_text("Escolha o tipo de conta que deseja usar", reply_markup=reply_markup1)

            sent_messages[callback_query.from_user.id] = sent_message

        elif "typecoin" in callback_query.data:
            reply_markup1 = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        f"Digital", callback_data="tcoin_digital"),
                    InlineKeyboardButton(
                        f"Binária", callback_data="tcoin_binaria"),

                ]

            ])

            sent_message = await callback_query.message.reply_text("Escolha se quer operar binárias ou digitais:", reply_markup=reply_markup1)

            sent_messages[callback_query.from_user.id] = sent_message
        else:
            print(callback_query.data)

    elif "entr_" in callback_query.data:

        if "normal" in callback_query.data:
            alter_config("tipo_entrada", "normal")
        elif "ciclo" in callback_query.data:
            alter_config("tipo_entrada", "ciclo")
        elif "martingale" in callback_query.data:
            alter_config("tipo_entrada", "martingale")

        await app.delete_messages(callback_query.message.chat.id, callback_query.message.id)
        await app.edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            message_id=sent_messages['message_id'],
            reply_markup=refresh_config()
        )

    elif "corr_" in callback_query.data:
        if "iqoption" in callback_query.data:
            alter_config("corretora", "iqoption")
        elif "quotex" in callback_query.data:
            alter_config("corretora", "quotex")
        elif "binomo" in callback_query.data:
            alter_config("corretora", "binomo")

        await app.delete_messages(callback_query.message.chat.id, callback_query.message.id)
        await app.edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            message_id=sent_messages['message_id'],
            reply_markup=refresh_config()
        )

    # Timeframe
    elif "_tmf" in callback_query.data:

        timeframe = callback_query.data.replace("_tmf", "")
        alter_config("timeframe", timeframe)

        await app.delete_messages(callback_query.message.chat.id, callback_query.message.id)
        await app.edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            message_id=sent_messages['message_id'],
            reply_markup=refresh_config()
        )

    # Estratégias
    elif "_trat_back" in callback_query.data:
        estrat_back = callback_query.data.replace("_trat_back", "")
        registra_sess_data(app, callback_query.from_user.id,
                           estrat_back, "trat_back")

        reply_markup1 = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "1 min", callback_data="1_timeframe_back"),
                InlineKeyboardButton(
                    "2 min", callback_data="2_timeframe_back"),
                InlineKeyboardButton(
                    "5 min", callback_data="5_timeframe_back"),
                InlineKeyboardButton(
                    "15 min", callback_data="15_timeframe_back"),
            ]

        ])
        sent_message = await callback_query.message.reply_text(
            "Escolha o timeframe para o Backtest:", reply_markup=reply_markup1)

    elif "_timeframe_back" in callback_query.data:
        timeframe_back = callback_query.data.replace("_timeframe_back", "")
        registra_sess_data(app, callback_query.from_user.id,
                           timeframe_back, "timeframe_back")
        await callback_query.message.reply(f"Informe o limite de ciclos de candle para a estrategia")
        registra_sess_data(app, callback_query.from_user.id,
                           "lmt_candle", "active_edit")

    elif "_persontime_back" in callback_query.data:
        persontime = callback_query.data.replace("_persontime_back", "")
        print("persontime: ", persontime)
        if persontime == "sim":
            registra_sess_data(app, callback_query.from_user.id,
                               "personsdatas", "active_edit")
            await callback_query.message.reply(f"Digite a data/hora inicial e final no formato dd/mm/aaaa;hh:mm, sendo a separação entre elas o - (hífen)")

        else:

            reply_markup15 = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "6h", callback_data="6h_time_back"),
                    InlineKeyboardButton(
                        "8h", callback_data="8h_time_back"),
                    InlineKeyboardButton(
                        "12h", callback_data="12h_time_back"),
                ], [
                    InlineKeyboardButton(
                        "1 dia", callback_data="1d_time_back"),
                    InlineKeyboardButton(
                        "5 dias", callback_data="5d_time_back"),
                    InlineKeyboardButton(
                        "15 dias", callback_data="15d_time_back"),
                ]

            ])
            await callback_query.message.reply_text(
                "Escolha o período do Backtest:", reply_markup=reply_markup15)

    elif "_time_back" in callback_query.data:
        time_back = callback_query.data.replace("_time_back", "")
        registra_sess_data(app, callback_query.from_user.id,
                           time_back, "time_back")

        reply_markup1 = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "paula", callback_data="paula_est"),
            ], [
                InlineKeyboardButton(
                    "teste", callback_data="teste_est"),
            ]

        ])
        sent_message = await callback_query.message.reply_text(
            "Escolha a estratégia para o Backtest:", reply_markup=reply_markup1)

    elif "_est" in callback_query.data:

        estrat = callback_query.data.replace("_est", "")
        alter_config("estrategia_principal", estrat)

        await app.delete_messages(callback_query.message.chat.id, callback_query.message.id)
        await app.edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            message_id=sent_messages['message_id'],
            reply_markup=refresh_config()
        )
    # Tipo de conta
    elif "taccount_" in callback_query.data:
        if "real" in callback_query.data:
            alter_config("tipo_conta", "REAL")
        elif "practice" in callback_query.data:
            alter_config("tipo_conta", "PRACTICE")

        await app.delete_messages(callback_query.message.chat.id, callback_query.message.id)
        await app.edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            message_id=sent_messages['message_id'],
            reply_markup=refresh_config()
        )
    # Tipo de moeda
    elif "tcoin_" in callback_query.data:
        if "digital" in callback_query.data:
            alter_config("typecoin", "digital")
        elif "binaria" in callback_query.data:
            alter_config("typecoin", "binaria")

        await app.delete_messages(callback_query.message.chat.id, callback_query.message.id)
        await app.edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            message_id=sent_messages['message_id'],
            reply_markup=refresh_config()
        )


@app.on_message()
async def messages(Client, message):
    # Obter o user_id do bot
    me = await app.get_me()
    bot_user_id = me.id
    # await message.reply("Processando solicitação...")
    # Verificar se a mensagem é enviada pelo próprio bot
    if message.from_user.id == bot_user_id:
        return  # Não faça nada se a mensagem for do próprio bot
    try:
        user_data = app.get_user_data(message.chat.id)
        print(user_data)
    except:
        print("Usuário não registrado")

    if not app.get_user_data(message.chat.id):
        registra_sess_data(app, message.from_user.id,
                           "", "active_edit")

    general_session = app.get_user_data(message.chat.id)
    if general_session['active_edit'] == "qtd_martingale":
        if message.text.isnumeric():
            alter_config("qtd_martingale", int(message.text))
            # Deleta as mensagens anteriores entre a msg atual e a msg de configuração
            current_msg = message.id
            print(f"current_msg: {current_msg}")
            print(f"sent_messages: {sent_messages['message_id']}")
            while current_msg > sent_messages['message_id']:
                print(f"current_msg: {current_msg}")
                print(f"sent_messages: {sent_messages['message_id']}")
                await app.delete_messages(message.chat.id, current_msg)
                current_msg -= 1

            await app.edit_message_reply_markup(chat_id=message.chat.id, message_id=sent_messages['message_id'], reply_markup=refresh_config())
            registra_sess_data(app, message.from_user.id,
                               "", "active_edit")
        else:
            await app.send_message(message.chat.id, "Valor inválido, tente novamente!")

    elif general_session['active_edit'] == "personsdatas":
        registra_sess_data(app, message.from_user.id,
                           message.text, "personsdatas")
        reply_markup21 = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "paula", callback_data="paula_est"),
            ], [
                InlineKeyboardButton(
                    "teste", callback_data="teste_est"),
            ]
        ])
        sent_message = await message.reply_text(
            "Escolha a estratégia para o Backtest:", reply_markup=reply_markup21)

    elif general_session['active_edit'] == "lmt_candles":
        if message.text.isnumeric():
            alter_config("lmt_candles", int(message.text))
            # Deleta as mensagens anteriores entre a msg atual e a msg de configuração
            current_msg = message.id
            print(f"current_msg: {current_msg}")
            print(f"sent_messages: {sent_messages['message_id']}")
            while current_msg > sent_messages['message_id']:
                print(f"current_msg: {current_msg}")
                print(f"sent_messages: {sent_messages['message_id']}")
                await app.delete_messages(message.chat.id, current_msg)
                current_msg -= 1

            await app.edit_message_reply_markup(chat_id=message.chat.id, message_id=sent_messages['message_id'], reply_markup=refresh_config())
            registra_sess_data(app, message.from_user.id,
                               "", "active_edit")
        else:
            await app.send_message(message.chat.id, "Valor inválido, tente novamente!")

    elif general_session['active_edit'] == "fator_martingale":
        if is_numeric_point(message.text):
            alter_config("fator_martingale", float(message.text))

            # Deleta as mensagens anteriores entre a msg atual e a msg de configuração
            current_msg = message.id
            print(f"current_msg: {current_msg}")
            print(f"sent_messages: {sent_messages['message_id']}")
            while current_msg > sent_messages['message_id']:
                print(f"current_msg: {current_msg}")
                print(f"sent_messages: {sent_messages['message_id']}")
                await app.delete_messages(message.chat.id, current_msg)
                current_msg -= 1

            await app.edit_message_reply_markup(chat_id=message.chat.id, message_id=sent_messages['message_id'], reply_markup=refresh_config())
            registra_sess_data(app, message.from_user.id,
                               "", "active_edit")
        else:
            await app.send_message(message.chat.id, "Valor inválido, tente novamente!")

    elif general_session['active_edit'] == "qtd_ciclos":
        if is_numeric_point(message.text):
            alter_config("qtd_ciclos", float(message.text))

            # Deleta as mensagens anteriores entre a msg atual e a msg de configuração
            current_msg = message.id
            print(f"current_msg: {current_msg}")
            print(f"sent_messages: {sent_messages['message_id']}")
            while current_msg > sent_messages['message_id']:
                print(f"current_msg: {current_msg}")
                print(f"sent_messages: {sent_messages['message_id']}")
                await app.delete_messages(message.chat.id, current_msg)
                current_msg -= 1

            await app.edit_message_reply_markup(chat_id=message.chat.id, message_id=sent_messages['message_id'], reply_markup=refresh_config())
            registra_sess_data(app, message.from_user.id,
                               "", "active_edit")
        else:
            await app.send_message(message.chat.id, "Valor inválido, tente novamente!")

    elif general_session['active_edit'] == "valor_por_ciclo":
        ciclo_formatado = formatCiclo(message.text)
        if ciclo_formatado:
            alter_config("valor_por_ciclo", ciclo_formatado)
            # Deleta as mensagens anteriores entre a msg atual e a msg de configuração
            current_msg = message.id
            print(f"current_msg: {current_msg}")
            print(f"sent_messages: {sent_messages['message_id']}")
            while current_msg > sent_messages['message_id']:
                print(f"current_msg: {current_msg}")
                print(f"sent_messages: {sent_messages['message_id']}")
                await app.delete_messages(message.chat.id, current_msg)
                current_msg -= 1

            await app.edit_message_reply_markup(chat_id=message.chat.id, message_id=sent_messages['message_id'], reply_markup=refresh_config())
            registra_sess_data(app, message.from_user.id,
                               "", "active_edit")
        else:
            await app.send_message(message.chat.id, "Valor inválido, tente novamente!")

    elif general_session['active_edit'] == "pct_entrada":

        if is_numeric_point(message.text):
            alter_config("pct_entrada", float(message.text))

            # Deleta as mensagens anteriores entre a msg atual e a msg de configuração
            current_msg = message.id

            while current_msg > sent_messages['message_id']:
                print(f"current_msg: {current_msg}")
                print(f"sent_messages: {sent_messages['message_id']}")
                await app.delete_messages(message.chat.id, current_msg)
                current_msg -= 1

            await app.edit_message_reply_markup(chat_id=message.chat.id, message_id=sent_messages['message_id'], reply_markup=refresh_config())
            registra_sess_data(app, message.from_user.id,
                               "", "active_edit")

    elif general_session['active_edit'] == "porcentagem_stop_win":

        if is_numeric_point(message.text):
            alter_config("porcentagem_stop_win",
                         percent_to_float(message.text))

            # Deleta as mensagens anteriores entre a msg atual e a msg de configuração
            current_msg = message.id

            while current_msg > sent_messages['message_id']:
                print(f"current_msg: {current_msg}")
                print(f"sent_messages: {sent_messages['message_id']}")
                await app.delete_messages(message.chat.id, current_msg)
                current_msg -= 1

            await app.edit_message_reply_markup(chat_id=message.chat.id, message_id=sent_messages['message_id'], reply_markup=refresh_config())
            registra_sess_data(app, message.from_user.id,
                               "", "active_edit")
        else:
            await app.send_message(message.chat.id, "Valor inválido, tente novamente!")

    elif general_session['active_edit'] == "porcentagem_stop_loss":

        if is_numeric_point(message.text):
            alter_config("porcentagem_stop_loss",
                         percent_to_float(message.text))

            # Deleta as mensagens anteriores entre a msg atual e a msg de configuração
            current_msg = message.id

            while current_msg > sent_messages['message_id']:
                print(f"current_msg: {current_msg}")
                print(f"sent_messages: {sent_messages['message_id']}")
                await app.delete_messages(message.chat.id, current_msg)
                current_msg -= 1

            await app.edit_message_reply_markup(chat_id=message.chat.id, message_id=sent_messages['message_id'], reply_markup=refresh_config())
            registra_sess_data(app, message.from_user.id,
                               "", "active_edit")
        else:
            await app.send_message(message.chat.id, "Valor inválido, tente novamente!")

    elif general_session['active_edit'] == "ajust_sleep":
        if is_numeric_point(message.text):
            alter_config("timesleep", float(message.text))

            await app.send_message(message.chat.id, f"Valor alterado com sucesso para {message.text}")

            registra_sess_data(app, message.from_user.id,
                               "", "active_edit")

    elif general_session['active_edit'] == "coin_backtest":

        registra_sess_data(app, message.from_user.id,
                           message.text, "coin_backtest")
        await app.send_message(message.chat.id, f"Valor alterado com sucesso para {message.text}")
        usuario_dados = app.get_user_data(message.from_user.id)
        print(usuario_dados)
        registra_sess_data(app, message.from_user.id,
                           "", "active_edit")

        reply_markup15 = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "Sim", callback_data="sim_persontime_back"),
                InlineKeyboardButton(
                    "Não", callback_data="nao_persontime_back"),

            ]

        ])
        await message.reply_text(
            "Deseja usar periodo personalizado?:", reply_markup=reply_markup15)

    elif general_session['active_edit'] == "lmt_candle":
        obj_comp = all_configs()
        registra_sess_data(app, message.from_user.id,
                           message.text, "lmt_candle")
        usuario_dados = app.get_user_data(message.from_user.id)
        print(usuario_dados)
        # Verifica se existe a chave time_back no dicionario, se não houver atribui o valor 0
        if "time_back" not in usuario_dados:
            registra_sess_data(app, message.from_user.id,
                               0, "time_back")

        # Verifica se existe a chave personsdatas no dicionario, se não houver atribui o valor None
        if "personsdatas" not in usuario_dados:
            registra_sess_data(app, message.from_user.id,
                               None, "personsdatas")
        coin = usuario_dados['coin_backtest']
        period = usuario_dados['time_back']
        strateg = usuario_dados['trat_back']
        timeframe_back = usuario_dados['timeframe_back']
        lmt = usuario_dados['lmt_candle']
        personsdatas = usuario_dados['personsdatas']
        await app.send_message(message.chat.id, "Processando informações. Aguarde...")
        result = backtest_maker(
            coin, timeframe_back, period, strateg, lmt, obj_comp['banca'], personsdatas)
        for i in result:
            await app.send_message(message.chat.id, i)
        registra_sess_data(app, message.from_user.id,
                           "", "active_edit")

    elif general_session['active_edit'] == "pares_favoritos":
        pares_l = split_pairs(message.text)
        if pares_l:
            alter_config("pares_favoritos", pares_l)

            # Deleta as mensagens anteriores entre a msg atual e a msg de configuração
            current_msg = message.id

            while current_msg > sent_messages['message_id']:
                print(f"current_msg: {current_msg}")
                print(f"sent_messages: {sent_messages['message_id']}")
                await app.delete_messages(message.chat.id, current_msg)
                current_msg -= 1

            await app.edit_message_reply_markup(chat_id=message.chat.id, message_id=sent_messages['message_id'], reply_markup=refresh_config())
            registra_sess_data(app, message.from_user.id,
                               "", "active_edit")
        else:
            await app.send_message(message.chat.id, "Valor inválido, tente novamente!")
        # Verificar se a mensagem foi enviada pelo próprio bot.

    elif message.from_user.id == bot_user_id:
        return  # Ignorar a mensagem.

    else:
        await app.send_message(message.chat.id, "Olá, eu sou o BeRichBot, o bot do BeRich. Como posso te ajudar?")

app.run()
