#############################################################################
# DEFINICOES
#############################################################################
import pandas as pd
import datetime as dt
import numpy as np
from scipy.stats import gamma, expon
postos = [  'uniao_da_vitoria'
            'rio_negro',
            'porto_amazonas',
            'sao_mateus_do_sul'
            ]
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
            q = np.percentile(srq.loc[idx_t].to_numpy(),100-perc)
            linha.append(round(q,2))
        df_qrefs.loc[t.dayofyear,:] = linha
    return df_qrefs


################################################################################
# ALGORITMO
################################################################################
for posto in postos:
    print('Processando {}'.format(posto))

    # 1 - Aquisicao da serie de vazoes do posto
    path = '../dados-entrada/'
    srq = pd.read_csv(path+'{}.csv'.format(posto)
            , parse_dates=True, index_col='data')['q_m3s']

    # 2 - Calculo das vazoes de referencia (thresholds)
    percs = [95, 90, 84]
    df_qrefs = thresholds(srq, percs)

    # 3 - Criacao do DataFrame contendo os deficits e qrefs de cada intervalo
    df_deficits = srq.to_frame()
    qref = 'q{}'.format(qref)
    df_deficits[qref] = df_deficits.apply(lambda x:
                        df_qrefs.loc[(df_qrefs['mes']==x.name.month)&
                        (df_qrefs['dia']==x.name.day),'q95'].values[0]
                        if x.name.day != 29 else
                        df_qrefs.loc[(df_qrefs['mes']==x.name.month)&
                        (df_qrefs['dia']==28),'q95'].values[0], axis=1)
    df_deficits['di'] = df_deficits[qref] - df_deficits['q_m3s']

    # 4 - Separacao dos eventos de seca
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

    # 5 - Calculo das duracoes de cada evento
    df_eventos['d'] = (df_eventos['te']-df_eventos['ts']) + dt.timedelta(days=1)

    # 6 - Merge dos eventos com intervalos entre eventos iguais ou menores que tc
    for i in df_eventos.index[1:]:
        gap=df_eventos.loc[i,'ts']-df_eventos.loc[i-1,'te']-dt.timedelta(days=1)
        if gap <= dt.timedelta(days=tc):
            df_eventos.loc[i,'ts'] = df_eventos.loc[i-1,'ts']
            df_eventos.loc[i,'D']  += df_eventos.loc[i-1,'D']
            df_eventos.loc[i,'d']  += df_eventos.loc[i-1,'d']
            df_eventos.drop(index=i-1, inplace=True)

    # 7 - Eliminacao dos eventos com duracao inferior a d
    df_eventos.drop(df_eventos[df_eventos['d']<=dt.timedelta(days=d)].index,
        inplace=True)

    # 8 - Calculo das duracoes "reais" dos evento, ou seja,
    # considerando o periodo mesclado e nao soh os dias com registro de deficit
    df_eventos['d'] = (df_eventos['te']-df_eventos['ts']) + dt.timedelta(days=1)

    # 9 - Exporta o df em excel
    df_eventos.to_excel('../dados-saida/{}.xlsx'.format(posto))

    # 10 - Ajuste de distribuicoes
    # rv - random variable - deficits
    # fd - frozen distribution
    rv = df_eventos['D'].astype('float')
    # 10.1 - Exponencial
    params = expon.fit(rv)
    fd = expon(loc=params[0], scale=params[1])
    df_eventos['Pexpon(<=Dobs)'] = df_eventos.apply(lambda x:
        fd.cdf(x['D']), axis=1)
    # 10.2 - Gama
    params = gamma.fit(rv)
    fd = gamma(params[0], loc=params[1], scale=params[2])
    df_eventos['Pgama(<=Dobs)'] = df_eventos.apply(lambda x:
        fd.cdf(x['D']), axis=1)

    # 11 - Exporta os resultados
    df_eventos.to_excel('../dados-saida/{}.xlsx'.format(posto))
