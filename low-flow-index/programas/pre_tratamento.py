import pandas as pd
import numpy as np


def tratamento(sr_bruta):
    sr_bruta = sr_bruta.asfreq('D')
    sr_tratada = sr_bruta.interpolate(method='spline', order=3)
    return sr_tratada

nomes = [   'uniao_da_vitoria']

for nome in nomes:
    df_bruto = pd.read_csv(f'../series-brutas/{nome}.csv', parse_dates=True)
    df_bruto.set_index('data', inplace=True)
    sr_bruta = df_bruto['q_m3s']
    sr = tratamento(sr_bruta)
    sr.to_csv(f'../series-tratadas/{nome}.csv')
