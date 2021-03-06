#############################################################################
# DEFINICOES-
#############################################################################
import pandas as pd
import datetime as dt
import numpy as np
from scipy.stats import gamma, expon
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

postos = {
    #'eta_francisco_beltrao': 'ETA Francisco Beltrão \n Rio Marrecas - 336 km²',
    #'porto_carriel': 'Porto Carriel \n Rio Piquiri - 3540 km²',
    #'porto_espanhol': 'Porto Espanhol \n Rio Ivaí - 8540 km²',
    #'eta_maringa':'Maringá \n Ribeirão Pirapó - 1240 km²',
    #'uniao_vitoria':'União da Vitória \n Rio Iguaçu - 24200 km²',
    #'fazendinha':'RMC \n Rio Pequeno - 106 km²',
    #'eta_irati': 'ETA Irati \n Rio Imbituva - 226 km²',
    #'tomazina':'Tomazina \n Rio das Cinzas - 2020 km²',
    #'cachoeira':'Cachoeira - São José dos Pinhais \n Rio Miringuava - 272 km²',
    'senges':'Bacia do Itaraté - Sengés \n Rio Jaguaricatu - 869 km²',
    #'ponte_acungui': 'Ponte do Açungui - Campo Largo \n Rui Açungui - 582 km²',
    #'morretes': 'Morretes \n Rio Nhundiaquara - 215 km²',
#    'passauna':'RMC - Campo Largo \n Rio Passaúna - 84.4 km²',
          }
qref = 95
tc   = 15
d    = 5

################################################################################
# FUNCOES
################################################################################
def thresholds(srq, percs):
    tuplas_idx = list(zip(srq.index.month, srq.index.day))
    cols = ['q'+str(i) for i in percs]
    df_qrefs = pd.DataFrame(columns=['mes','dia'] + cols)
    df_qrefs.index.names = ['dia_juliano']
    for t in pd.date_range(dt.date(1900,1,1), dt.date(1900,12,31)):
        janela = pd.date_range(t - dt.timedelta(days=15), t + dt.timedelta(days=15))
        tuplas_janela = list(zip(janela.month, janela.day))
        idx_t = [ i in tuplas_janela for i in tuplas_idx ]
        linha = [t.month, t.day]
        for perc in percs:
            q = np.nanpercentile(srq.loc[idx_t].to_numpy(),100-perc)
            linha.append(round(q,2))
        df_qrefs.loc[t.dayofyear,:] = linha
    return df_qrefs

################################################################################
# ALGORITMO
################################################################################
for posto, legenda in postos.items():
    qref = 95
    tc   = 15
    d    = 5

    print('Processando {}'.format(posto))

    # 1 - Aquisicao da serie de vazoes do posto
    path = '../dados-entrada/'
    srq = pd.read_csv(path+'{}.csv'.format(posto)
            , parse_dates=True, index_col='data')['vazao']

    print('1 ok')

    # 2 - Calculo das vazoes de referencia (thresholds)
    #percs = [95, 90, 85, 80, 75, 70, 65, 60, 55, 50]
    percs = range(100)
    df_qrefs = thresholds(srq, percs)
    df_qrefs.to_csv('../dados-saida/{}_quantis.csv'.format(posto))

    print('2 ok')

    # 3 - Calculo do percentil atual
    ontem = srq.index[-1]
    if (ontem.month==2) & (ontem.day==29):
        diadoano=df_qrefs[(df_qrefs["mes"]==2) & (df_qrefs['dia']==28)]
    else:
        diadoano =df_qrefs[(df_qrefs["mes"]==ontem.month) & (df_qrefs['dia']==ontem.day)]
    diadoano2 = diadoano.drop(['mes', 'dia'], axis=1)

    for q in diadoano2.columns:
        if (diadoano2.loc[:,q].values[0] > srq[-1]):
            continue
        if (diadoano2.loc[:,q].values[0] <= srq[-1]):
            break
    valor_referencia = diadoano2.loc[:,'q95'].values[0]
    print(posto.replace('_',' ').title(),'\n',
          'Data: ', srq.index[-1].date(), '\n',
          'Vazao atual = ', str(srq[-1]), ' m3/s\n',
          'Excedencia (q%) = ', q, '\n',
          'Vazao de referencia (q95)= ', str(valor_referencia), 'm3/s')

    print('3 ok')

    # 4 - Criacao do DataFrame contendo os deficits e qrefs de cada intervalo
    df_deficits = srq.to_frame()
    qref = 'q{}'.format(qref)
    df_deficits[qref] = df_deficits.apply(lambda x:
                        df_qrefs.loc[(df_qrefs['mes']==x.name.month)&
                        (df_qrefs['dia']==28),qref].values[0]
                        if ((x.name.month == 2) and (x.name.day == 29)) else
                        df_qrefs.loc[(df_qrefs['mes']==x.name.month)&
                        (df_qrefs['dia']==x.name.day),qref].values[0], axis=1)
    df_deficits['di'] = df_deficits[qref] - df_deficits['vazao']
    df_deficits['q50'] = df_deficits.apply(lambda x:
                        df_qrefs.loc[(df_qrefs['mes']==x.name.month)&
                        (df_qrefs['dia']==28),'q50'].values[0]
                        if ((x.name.month == 2) and (x.name.day == 29)) else
                        df_qrefs.loc[(df_qrefs['mes']==x.name.month)&
                        (df_qrefs['dia']==x.name.day),'q50'].values[0], axis=1)
    df_deficits.to_csv('../dados-saida/{}_serie.csv'.format(posto))

    print('4 ok')

    # 5 - Plotagem serie c/ percentis
    nome_bacia = posto
    data_ini = dt.datetime.now()- dt.timedelta(days=365)
    data_fim = dt.datetime.now()
    serie_observada = df_deficits
    serie_observada = serie_observada.loc[str(data_ini) : str(data_fim)]
    obs = serie_observada['vazao']
    q95 = serie_observada['q95']
    q50 = serie_observada['q50']

    plt.figure()
    plt.plot(serie_observada['vazao'], label = "Observado", linewidth = 0.6, color = 'black')
    plt.plot(serie_observada['q95'], label = "Q95", linewidth = 0.8, color = 'maroon')
    plt.fill_between(serie_observada.index, obs, q95, where = (obs < q95), color = 'red', alpha = 0.3)
    plt.plot(serie_observada['q50'], label = "Q50", linewidth = 0.8, color = 'darkgoldenrod')
    plt.fill_between(serie_observada.index, obs, q50, where = (obs < q50), color = 'gold', alpha = 0.3)
    plt.scatter(obs.index[-1], obs[-1], label = "Vazão atual", color = "darkblue", s = 15)
    plt.xlabel('Data')
    plt.ylabel('Vazão [m3s-1]')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    plt.gca().xaxis.set_tick_params(rotation = 30)
    plt.gca().set_xbound(data_ini, data_fim)
    plt.title(legenda)
    plt.annotate(q,(obs.index[-1],obs[-1]), size=8, weight='bold',
                 xytext=(obs.index[-1]+dt.timedelta(days=3),obs[-1]))
    plt.legend(loc=2)
    plt.savefig('../dados-saida/'+nome_bacia+'_plot3.png', dpi = 300)
    plt.show()
    plt.close()
    print('Figura gerada')

    try:
        # 5 - Separacao dos eventos de seca
        df_eventos = pd.DataFrame(columns = ['ts','te','D'])
        i  = 0 # numero do evento
        ts = 0 # tempo de inicio
        te = 0 # tempo de encerramento
        D  = 0 # deficit acumulado
        for row in df_deficits.itertuples():
            if row[3] <= 0:
                if D > 0:
                    df_eventos.loc[i,'te'] = row[0] - dt.timedelta(days=1)
                    df_eventos.loc[i,'D'] = D
                    D = 0
                continue
            else:
                if D == 0: # novo evento!
                    i += 1
                    df_eventos.loc[i,'ts'] = row[0]
                D += row[3]
        if pd.isnull(df_eventos.iloc[-1,1]):
            df_eventos.iloc[-1,1] = df_deficits.iloc[-1].name
            df_eventos.iloc[-1,2] = D

        print('5 ok')

        # 6 - Calculo das duracoes de cada evento
        df_eventos['d'] = (df_eventos['te']-df_eventos['ts']) + dt.timedelta(days=1)

        print('6 ok')

        # 7 - Merge dos eventos com intervalos entre eventos iguais ou menores que tc
        for i in df_eventos.index[1:]:
            gap=df_eventos.loc[i,'ts']-df_eventos.loc[i-1,'te']-dt.timedelta(days=1)
            if gap <= dt.timedelta(days=tc):
                df_eventos.loc[i,'ts'] = df_eventos.loc[i-1,'ts']
                df_eventos.loc[i,'D']  += df_eventos.loc[i-1,'D']
                df_eventos.loc[i,'d']  += df_eventos.loc[i-1,'d']
                df_eventos.drop(index=i-1, inplace=True)

        print('7 ok')

        # 8 - Eliminacao dos eventos com duracao inferior a d
        df_eventos.drop(df_eventos[df_eventos['d']<=dt.timedelta(days=d)].index,
            inplace=True)

        print('8 ok')

        # 9 - Calculo das duracoes "reais" dos evento, ou seja,
        # considerando o periodo mesclado e nao soh os dias com registro de deficit
        df_eventos['d'] = (df_eventos['te']-df_eventos['ts']) + dt.timedelta(days=1)

        print('9 ok')

        # 10 - Exporta o df em excel
        df_eventos.to_excel('../dados-saida/{}.xlsx'.format(posto))

        print('10 ok')

        # 11 - Ajuste de distribuicoes
        # rv - random variable - deficits
        # fd - frozen distribution
        rv = df_eventos['D'].astype('float')
        # 11.1 - Exponencial
        params = expon.fit(rv)
        fd = expon(loc=params[0], scale=params[1])
        df_eventos['Pexpon(<=Dobs)'] = df_eventos.apply(lambda x:
            fd.cdf(x['D']), axis=1)
        # 11.2 - Gama
        params = gamma.fit(rv)
        fd = gamma(params[0], loc=params[1], scale=params[2])
        df_eventos['Pgama(<=Dobs)'] = df_eventos.apply(lambda x:
            fd.cdf(x['D']), axis=1)

        print('11 ok')

        # 12 - Exporta os resultados
        df_eventos.to_excel('../dados-saida/{}.xlsx'.format(posto))
    except:
        print('Ocorreu um erro no cálculo dos eventos de déficit \n',
              'Possível erro: série com dados vazios')

    print('Finalizado {}'.format(posto))
