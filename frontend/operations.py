from .service import all_configs, atualiza_banca, banca_min
from backend.handler import get_one_data


def render_template():

    conf = all_configs()
    banca = atualiza_banca()
    lucprej = get_one_data('luc_prej')
    opaberto = conf['opaberto']
    valgain = round(banca * conf['porcentagem_stop_win'], 2)
    banca_minima = banca_min(conf['fator_martingale'], conf['qtd_ciclos'])
    return f"__***RESULTADOS ATUALIZADOS***__\n**BANCA** : U$ {banca} \n**LUCRO/PREJUIZO **: U$ {lucprej}  \n**OP. EM ABERTO** : U$ {opaberto}  \n**VALOR GAIN** : U$ {valgain}\n **BANCA MINIMA** : U$ {banca_minima} "
