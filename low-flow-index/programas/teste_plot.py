#BIBLIOTECAS
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import datetime as dt

#DEFINICAO PERIODO ANALISE
data_inicial = dt.datetime(2020, 1, 1,  0,  0) #YYYY, M, D, H, Min
data_final = dt.datetime(2020, 10, 14,  23,  59)

dir_plot = "/home/bruno/github/analise-seca/low-flow-index/dados-saida"
os.chdir(dir_plot)


nome_bacia = 'uniao_da_vitoria'

data_ini = data_inicial
data_fim = data_final

serie_observada = pd.read_csv(nome_bacia+'_serie.csv', index_col=0)
serie_observada.index = pd.to_datetime(serie_observada.index)
serie_observada = serie_observada.loc[str(data_ini) : str(data_fim)]
serie_observada

plt.figure()
plt.plot(serie_observada['q_m3s'], label = "Observado", linewidth = 0.6, color = 'black')
plt.plot(serie_observada['q95'], label = "Q95", linewidth = 0.5, color = 'red')
plt.xlabel('Data')
plt.ylabel('Vazão [m3s-1]')
# Format the date into months & days
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
# Puts x-axis labels on an angle
plt.gca().xaxis.set_tick_params(rotation = 30)
# Changes x-axis range
plt.gca().set_xbound(data_ini, data_fim)
plt.savefig(nome_bacia+'_plot.png', dpi = 300)
plt.show()
