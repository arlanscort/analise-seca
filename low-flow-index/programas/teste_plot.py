#BIBLIOTECAS
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import datetime as dt

#DEFINICAO PERIODO ANALISE
#data_inicial = dt.datetime(2020, 7, 1,  0,  0) #YYYY, M, D, H, Min
data_inicial = dt.datetime.now()- dt.timedelta(days=365)
data_final = dt.datetime.now()

dir_plot = "../dados-saida/"
os.chdir(dir_plot)


#nome_bacia = 'uniao_da_vitoria'
nome_bacia = 'tomazina'

data_ini = data_inicial
data_fim = data_final
serie_observada = pd.read_csv(nome_bacia+'_serie.csv', index_col=0)
serie_observada.index = pd.to_datetime(serie_observada.index)
serie_observada = serie_observada.loc[str(data_ini) : str(data_fim)]
obs = serie_observada['q_m3s']
q95 = serie_observada['q95']
q50 = serie_observada['q50']

plt.figure()
plt.plot(serie_observada['q_m3s'], label = "Observado", linewidth = 0.6, color = 'black')
plt.plot(serie_observada['q95'], label = "Q95", linewidth = 0.8, color = 'maroon')
plt.plot(serie_observada['q50'], label = "Q50", linewidth = 0.8, color = 'darkgoldenrod')
plt.scatter(obs.index[-1], obs[-1], label = "Vazão atual", color = "darkblue", s = 15)
'''
plt.hlines(y = 150, xmin = dt.datetime(2020,1,27), xmax=dt.datetime(2020,1,31), linewidth = 0.4)
plt.text(y= 155, x = dt.datetime(2020,1,29), s = 'di', ha = 'center', weight = 'light')
plt.hlines(y = 150, xmin = dt.datetime(2020,2,19), xmax=dt.datetime(2020,2,25), linewidth = 0.4)
plt.text(y= 155, x = dt.datetime(2020,2,22), s = 'di', ha = 'center', weight = 'light')
plt.hlines(y = 150, xmin = dt.datetime(2020,3,9), xmax=dt.datetime(2020,5,23), linewidth = 0.4)
plt.text(y= 155, x = dt.datetime(2020,4,16), s = 'di', ha = 'center', weight = 'light')
plt.hlines(y = 150, xmin = dt.datetime(2020,5,25), xmax=dt.datetime(2020,6,7), linewidth = 0.4)
plt.text(y= 155, x = dt.datetime(2020,6,1), s = 'di', ha = 'center', weight = 'light')
plt.scatter(y = [150, 150, 150, 150, 150, 150, 150, 150],
            x = [dt.datetime(2020,1,27),dt.datetime(2020,1,31),
                 dt.datetime(2020,2,19),dt.datetime(2020,2,25),
                 dt.datetime(2020,3,9),dt.datetime(2020,5,23),
                 dt.datetime(2020,5,25),dt.datetime(2020,6,7)],
            marker = "|", linewidth = 0.4, color = 'black')
plt.hlines(y = 80, xmin = dt.datetime(2020,2,1), xmax=dt.datetime(2020,2,19), linewidth = 0.4)
plt.text(y= 85, x = dt.datetime(2020,2,10), s = 't < tc', ha = 'center', weight = 'light')
plt.hlines(y = 80, xmin = dt.datetime(2020,2,26), xmax=dt.datetime(2020,3,9), linewidth = 0.4)
plt.text(y= 85, x = dt.datetime(2020,3,3), s = 't < tc', ha = 'center', weight = 'light')
plt.scatter(y = [80, 80, 80, 80],
            x = [dt.datetime(2020,2,1),dt.datetime(2020,2,19),
                 dt.datetime(2020,2,26),dt.datetime(2020,3,9)],
            marker = "|", linewidth = 0.4, color = 'black')
'''
plt.xlabel('Data')
plt.ylabel('Vazão [m3s-1]')
plt.fill_between(serie_observada.index, obs, q95, where = (obs < q95), color = 'red', alpha = 0.3)
plt.fill_between(serie_observada.index, obs, q50, where = (obs < q50), color = 'gold', alpha = 0.3)
# Format the date into months & days
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))
# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
# Puts x-axis labels on an angle
plt.gca().xaxis.set_tick_params(rotation = 30)
# Changes x-axis range
plt.gca().set_xbound(data_ini, data_fim)
# Legenda
plt.title(nome_bacia.replace('_',' ').title())
plt.legend()
plt.savefig(nome_bacia+'_plot2.png', dpi = 300)
plt.show()
