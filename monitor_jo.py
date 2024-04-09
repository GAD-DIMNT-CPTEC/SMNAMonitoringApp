#!/usr/bin/env python
# coding: utf-8

# # SMNA-Dashboard
# 
# Este notebook trata da apresentação dos resultados do GSI em relação à minimização da função custo do 3DVar. A apresentação dos resultados é feita a partir da leitura de um arquivo CSV e os gráficos são mostrados em um dashboard do Panel para explorar as informações nele contidas. Para mais informações sobre o arquivo CSV e a sua estrutura de dados, veja o notebook `SMNA-Dashboard-load_files_create_dataframe_save.ipynb`.
# 
# Para realizar o deploy do dashboard no GitHub, é necessário converter este notebook em um script executável, o que pode ser feito a partir da interface do Jupyter (File -> Save and Export Notebook As... -> Executable Script). A seguir, utilize o comando abaixo para converter o script em uma página HTML. Junto com a página, será gerado um arquivo JavaScript e ambos devem ser adicionados ao repositório, junto com o arquivo CSV.
# 
# ```
# panel convert SMNA-Dashboard.py --to pyodide-worker --out .
# ```
# 
# Para utilizar o dashboard localmente, utilize o comando a seguir:
# 
# ```
# panel serve SMNA-Dashboard.ipynb --autoreload --show
# ```
# 
# ---
# Carlos Frederico Bastarz (carlos.bastarz@inpe.br), Abril de 2023.

import os
import re
import numpy as np
import pandas as pd
import hvplot.pandas
import panel as pn
#from panel_modal import Modal
from datetime import datetime, timedelta
from matplotlib import pyplot as plt

from monitor_dates import MonitoringAppDates

pn.extension('floatpanel')
pn.extension(sizing_mode='stretch_width', notifications=True)

#dfs = pd.read_csv('http://ftp1.cptec.inpe.br/pesquisa/das/carlos.bastarz/GSIMonitor/jo/jo_table_series.csv', header=[0, 1], parse_dates=[('df_preOper', 'Date'), ('df_preOper_new', 'Date'), ('df_JGerd', 'Date')])
dfs = pd.read_csv('http://ftp1.cptec.inpe.br/pesquisa/das/carlos.bastarz/GSIMonitor/jo/jo_table_series.csv', header=[0, 1], parse_dates=[('df_preOper', 'Date'), ('df_JGerd', 'Date')])

# Separa os dataframes de interesse
df_preOper = dfs.df_preOper
#df_preOper_new = dfs.df_preOper_new
df_JGerd = dfs.df_JGerd

# Atribui nomes aos dataframes
df_preOper.name = 'df_preOper'
#df_preOper_new.name = 'df_preOper_new'
df_JGerd.name = 'df_JGerd'

monitoring_app_dates = MonitoringAppDates()
sdate = monitoring_app_dates.getDates()[0].strip()
edate = monitoring_app_dates.getDates()[1].strip()

start_date = datetime(int(sdate[0:4]), int(sdate[4:6]), int(sdate[6:8]), int(sdate[8:10]))
start_date_fixed = datetime(int(sdate[0:4]), int(sdate[4:6]), int(sdate[6:8]), int(sdate[8:10]))
end_date = datetime(int(edate[0:4]), int(edate[4:6]), int(edate[6:8]), int(edate[8:10]))
end_date_fixed = datetime(int(edate[0:4]), int(edate[4:6]), int(edate[6:8]), int(edate[8:10]))

# Constrói as widgets e apresenta o dashboard
#sdate = pd.to_datetime(dfs.df_preOper['Date']).dt.strftime('%Y%m%d%H').min()
#edate = pd.to_datetime(dfs.df_preOper['Date']).dt.strftime('%Y%m%d%H').max()
#sdate = pd.to_datetime(sfdate.min()).date()
#edate = pd.to_datetime(efdate.max()).date()
#start_date = sdate.datetime.strptime('%Y%m%d%H')
#end_date = edate.datetime.strptime('%Y%m%d%H')
#start_date = datetime(2024, 3, 12, 12)
#start_date_fixed = datetime(2024, 3, 19, 12)
#end_date = datetime(2024, 3, 12, 12)
#end_date_fixed = datetime(2024, 3, 19, 12)

values = (start_date, end_date)

date_range_slider = pn.widgets.DatetimeRangePicker(name='Date Range', value=values, enable_time=False)

#experiment_list = [df_preOper, df_preOper_new, df_JGerd]
#experiment_list2 = ['df_preOper', 'df_preOper_new', 'df_JGerd']
experiment_list = [df_preOper, df_JGerd]
experiment_list2 = ['df_preOper', 'df_JGerd']
variable_list = ['surface pressure', 'temperature', 'wind', 'moisture', 'gps', 'radiance'] 
synoptic_time_list = ['00Z', '06Z', '12Z', '18Z', '00Z e 12Z', '06Z e 18Z', '00Z, 06Z, 12Z e 18Z']
iter_fcost_list = ['OMF', 'OMF (1st INNER LOOP)', 'OMF (2nd INNER LOOP)', 'OMA (AFTER 1st OUTER LOOP)', 'OMA (1st INNER LOOP)', 'OMA (2nd INNER LOOP)', 'OMA (AFTER 2nd OUTER LOOP)']

date_range = date_range_slider.value

experiment = pn.widgets.MultiChoice(name='Experiments (Plots)', value=[experiment_list[0].name], options=[i.name for i in experiment_list], solid=False)
experiment2 = pn.widgets.Select(name='Experiment (Table)', value=experiment_list[0].name, options=[i.name for i in experiment_list])
variable = pn.widgets.Select(name='Variable', value=variable_list[0], options=variable_list)
synoptic_time = pn.widgets.RadioBoxGroup(name='Synoptic Time', value=synoptic_time_list[-1], options=synoptic_time_list, inline=False)
iter_fcost = pn.widgets.Select(name='Iteration', value=iter_fcost_list[0], options=iter_fcost_list)

# Considerando que todos os dataframes possuem o mesmo tamanho (i.e, linhas e colunas), 
# então a função a seguir utiliza apenas um dos dataframes para criar a máscara temporal que será 
# utilizada pelos demais
def subset_dataframe(df, start_date, end_date, send_notification):
    if start_date > end_date_fixed:
        start_date = start_date_fixed
        if send_notification:
            pn.state.notifications.error('Seleção da data inicial é maior do que a data final no arquivo CVS', duration=5000)
    if end_date > end_date_fixed:
        end_date = end_date_fixed
        if send_notification:
            pn.state.notifications.error('Seleção da data final é maior do que a data final no arquivo CVS', duration=5000)
    mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
    return df.loc[mask]

height=250

@pn.depends(variable, experiment, synoptic_time, iter_fcost, date_range_slider.param.value)
def plotCurves(variable, experiment, synoptic_time, iter_fcost, date_range):
    for count, i in enumerate(experiment):
        if count == 0:
            sdf = globals()[i]
            df = dfs.xs(sdf.name, axis=1)
            
            send_notification = True
            start_date, end_date = date_range
            df2 = subset_dataframe(df, start_date, end_date, send_notification)
            
            if synoptic_time == '00Z': time_fmt0 = '00:00:00'; time_fmt1 = '00:00:00'
            if synoptic_time == '06Z': time_fmt0 = '06:00:00'; time_fmt1 = '06:00:00'
            if synoptic_time == '12Z': time_fmt0 = '12:00:00'; time_fmt1 = '12:00:00'
            if synoptic_time == '18Z': time_fmt0 = '18:00:00'; time_fmt1 = '18:00:00'    
    
            if synoptic_time == '00Z e 12Z': time_fmt0 = '00:00:00'; time_fmt1 = '12:00:00'
            if synoptic_time == '06Z e 18Z': time_fmt0 = '06:00:00'; time_fmt1 = '18:00:00'
    
            if synoptic_time == '00Z e 06Z': time_fmt0 = '00:00:00'; time_fmt1 = '06:00:00'
            if synoptic_time == '12Z e 18Z': time_fmt0 = '12:00:00'; time_fmt1 = '18:00:00'    
    
            if synoptic_time == '00Z, 06Z, 12Z e 18Z': time_fmt0 = '00:00:00'; time_fmt1 = '18:00:00'    
    
            if time_fmt0 == time_fmt1:
                df_s = df2.loc[df2['Observation Type'] == variable].loc[df2['Iter'] == iter_fcost].set_index('Date').at_time(str(time_fmt0)).reset_index()
            else:                
                df_s = df2.loc[df2['Observation Type'] == variable].loc[df2['Iter'] == iter_fcost].set_index('Date').between_time(str(time_fmt0), str(time_fmt1), inclusive='both')
                
                if synoptic_time == '00Z e 12Z':
                    df_s = df_s.drop(df_s.at_time('06:00:00').index).reset_index()
                elif synoptic_time == '06Z e 18Z':    
                    df_s = df_s.drop(df_s.at_time('12:00:00').index).reset_index()
                elif synoptic_time == '00Z, 06Z, 12Z e 18Z':
                    df_s = df_s.reset_index()                    
                
            xticks = len(df_s['Date'].values)    
                
            ax_nobs = df_s.hvplot.line(x='Date', y='Nobs', xlabel='Data', ylabel=str('Nobs'), persist=True, rot=90, grid=True, label=str(i), line_width=3, height=height, responsive=True)    
            ax_jo = df_s.hvplot.line(x='Date', y='Jo', xlabel='Data', ylabel=str('Jo'), persist=True, rot=90, grid=True, label=str(i), line_width=3, height=height, responsive=True)    
            ax_jon = df_s.hvplot.line(x='Date', y='Jo/n', xlabel='Data', ylabel=str('Jo/n'), persist=True, rot=90, grid=True, label=str(i), line_width=3, height=height, responsive=True)
            
            # Adiciona pontos às curvas
            sax_nobs = df_s.hvplot.scatter(x='Date', y='Nobs', height=height, label=str(i), persist=True, responsive=True).opts(size=5, marker='o')    
            sax_jo = df_s.hvplot.scatter(x='Date', y='Jo', height=height, label=str(i), persist=True, responsive=True).opts(size=5, marker='o')     
            sax_jon = df_s.hvplot.scatter(x='Date', y='Jo/n', height=height, label=str(i), persist=True, responsive=True).opts(size=5, marker='o')             
            
        else:
            
            sdf = globals()[i]
            df = dfs.xs(sdf.name, axis=1)
            
            send_notification = False
            start_date, end_date = date_range
            df2 = subset_dataframe(df, start_date, end_date, send_notification)
            
            if synoptic_time == '00Z': time_fmt0 = '00:00:00'; time_fmt1 = '00:00:00'
            if synoptic_time == '06Z': time_fmt0 = '06:00:00'; time_fmt1 = '06:00:00'
            if synoptic_time == '12Z': time_fmt0 = '12:00:00'; time_fmt1 = '12:00:00'
            if synoptic_time == '18Z': time_fmt0 = '18:00:00'; time_fmt1 = '18:00:00'    
    
            if synoptic_time == '00Z e 12Z': time_fmt0 = '00:00:00'; time_fmt1 = '12:00:00'
            if synoptic_time == '06Z e 18Z': time_fmt0 = '06:00:00'; time_fmt1 = '18:00:00'
    
            if synoptic_time == '00Z, 06Z, 12Z e 18Z': time_fmt0 = '00:00:00'; time_fmt1 = '18:00:00'   
    
            if time_fmt0 == time_fmt1:
                df_s = df2.loc[df2['Observation Type'] == variable].loc[df2['Iter'] == iter_fcost].set_index('Date').at_time(str(time_fmt0)).reset_index()
            else:                    
                df_s = df2.loc[df2['Observation Type'] == variable].loc[df2['Iter'] == iter_fcost].set_index('Date').between_time(str(time_fmt0), str(time_fmt1), inclusive='both')

                if synoptic_time == '00Z e 12Z':
                    df_s = df_s.drop(df_s.at_time('06:00:00').index).reset_index()
                elif synoptic_time == '06Z e 18Z':    
                    df_s = df_s.drop(df_s.at_time('12:00:00').index).reset_index()
                elif synoptic_time == '00Z, 06Z, 12Z e 18Z':
                    df_s = df_s.reset_index()
                
            xticks = len(df_s['Date'].values)
            
            ax_nobs *= df_s.hvplot.line(x='Date', y='Nobs', xlabel='Data', ylabel=str('Nobs'), persist=True, rot=90, grid=True, label=str(i), line_width=3, height=height, responsive=True)
            ax_jo *= df_s.hvplot.line(x='Date', y='Jo', xlabel='Data', ylabel=str('Jo'), persist=True, rot=90, grid=True, label=str(i), line_width=3, height=height, responsive=True)
            ax_jon *= df_s.hvplot.line(x='Date', y='Jo/n', xlabel='Data', ylabel=str('Jo/n'), persist=True, rot=90, grid=True, label=str(i), line_width=3, height=height, responsive=True)
            
            # Adiciona pontos às curvas
            sax_nobs *= df_s.hvplot.scatter(x='Date', y='Nobs', height=height, label=str(i), persist=True, responsive=True).opts(size=5, marker='o')    
            sax_jo *= df_s.hvplot.scatter(x='Date', y='Jo', height=height, label=str(i), persist=True, responsive=True).opts(size=5, marker='o')     
            sax_jon *= df_s.hvplot.scatter(x='Date', y='Jo/n', height=height, label=str(i), persist=True, responsive=True).opts(size=5, marker='o')             
            
    return pn.Column(ax_nobs*sax_nobs, ax_jo*sax_jo, ax_jon*sax_jon, sizing_mode='stretch_width')

@pn.depends(variable, experiment2, synoptic_time, iter_fcost, date_range_slider.param.value)
def getTable(variable, experiment2, synoptic_time, iter_fcost, date_range):
    #for count, i in enumerate(experiment):
    #    if count == 0:
    sdf = globals()[experiment2]
    df = dfs.xs(sdf.name, axis=1)
    
    send_notification = False            
    start_date, end_date = date_range
    df2 = subset_dataframe(df, start_date, end_date, send_notification)
            
    if synoptic_time == '00Z': time_fmt0 = '00:00:00'; time_fmt1 = '00:00:00'
    if synoptic_time == '06Z': time_fmt0 = '06:00:00'; time_fmt1 = '06:00:00'
    if synoptic_time == '12Z': time_fmt0 = '12:00:00'; time_fmt1 = '12:00:00'
    if synoptic_time == '18Z': time_fmt0 = '18:00:00'; time_fmt1 = '18:00:00'    
    
    if synoptic_time == '00Z e 12Z': time_fmt0 = '00:00:00'; time_fmt1 = '12:00:00'
    if synoptic_time == '06Z e 18Z': time_fmt0 = '06:00:00'; time_fmt1 = '18:00:00'
    
    if synoptic_time == '00Z e 06Z': time_fmt0 = '00:00:00'; time_fmt1 = '06:00:00'
    if synoptic_time == '12Z e 18Z': time_fmt0 = '12:00:00'; time_fmt1 = '18:00:00'    
    
    if synoptic_time == '00Z, 06Z, 12Z e 18Z': time_fmt0 = '00:00:00'; time_fmt1 = '18:00:00'    
    
    if time_fmt0 == time_fmt1:
        df_s = df2.loc[df2['Observation Type'] == variable].loc[df2['Iter'] == iter_fcost].set_index('Date').at_time(str(time_fmt0)).reset_index()
    else:                
        df_s = df2.loc[df2['Observation Type'] == variable].loc[df2['Iter'] == iter_fcost].set_index('Date').between_time(str(time_fmt0), str(time_fmt1), inclusive='both')
                
    if synoptic_time == '00Z e 12Z':
        df_s = df_s.drop(df_s.at_time('06:00:00').index).reset_index()
    elif synoptic_time == '06Z e 18Z':    
        df_s = df_s.drop(df_s.at_time('12:00:00').index).reset_index()
    elif synoptic_time == '00Z, 06Z, 12Z e 18Z':
        df_s = df_s.reset_index()                    
                
    #return pn.Column(df_s, sizing_mode='stretch_width')
    return pn.Column(pn.widgets.Tabulator(df_s, selectable=False, disabled=True), sizing_mode='stretch_width')

###

def Layout():

    text_info = """
    # SMNA Dashboard - Função Custo
    
    ## Curvas
    
    A depender da quantidade de outer e inner loops, o GSI registra um número diferente de informações sobre o número de observações consideradas (`Nobs`), o custo da minimização (`Jo`) e o custo da minimização normalizado pelo número de observações (`Jo/n`). A configuração do GSI/3DVar aplicado ao SMNA (válido para a data de escrita deste notebook), considera `miter=2` e `niter=3`, ou seja, 2 outer loops com 3 inner loops cada. Nesse sentido, as informações obtidas a partir das iterações do processo de minimização da função custo, consideram o seguinte:
    
    * `OMF`: início do primeiro outer loop, onde o estado do sistema é dado pelo background;
    * `OMF (1st INNER LOOP)`: final do primeiro inner loop do primeiro outer loop, onde o estado do sistema ainda é dado pelo background;
    * `OMF (2nd INNER LOOP)`: final do segundo inner loop do primeiro outer loop, onde o estado do sistema ainda é dado pelo background;
    * `OMA (AFTER 1st OUTER LOOP)`: início do segundo outer loop, onde o estado do sistema é dado pela análise;
    * `OMA (1st INNER LOOP)`: final do primeiro inner loop do segundo outer loop, onde o estado do sistema é dado pela análise;
    * `OMA (2nd INNER LOOP)`: final do segundo inner loop do segundo outer loop, onde o estado do sistema é dado pela análise;
    * `OMA (AFTER 2nd OUTER LOOP)`: final do segundo outer loop, análise final.
    
    **Nota:** as informações das iterações `OMF` e `OMF (1st INNER LOOP)` são iguais, assim como as informações das iterações `OMA (AFTER 1st OUTER LOOP)` e `OMA (1st INNER LOOP)`.
    
    ## Experimentos
    
    * `df_dtc`: experimento controle SMNA-Oper, com a matriz **B** do DTC, realizado pelo DIMNT;
    * `df_dtc_alex`: experimento SMNA-Oper, com a matriz **B** do DTC, realizado pela DIPTC;
    * `df_bamh_T0`: experimento controle SMNA-Oper, com a matriz **B** do BAMH (exp. T0), realizado pelo DIMNT;
    * `df_bamh_T4`: experimento controle SMNA-Oper, com a matriz **B** do BAMH (exp. T4), realizado pelo DIMNT;
    * `df_bamh_GT4AT2`: experimento controle SMNA-Oper, com a matriz **B** do BAMH (exp. GT4AT2), realizado pelo DIMNT;
    
    **Nota:** a descrição dos experimentos T0, T4 e GT4AT2 podem ser encontradas em [https://projetos.cptec.inpe.br/issues/11766](https://projetos.cptec.inpe.br/issues/11766).        
    
    ## Período
    
    O período considerado para a apresentação dos resultados é 2023021600 a 2023031600.
    
    ---
    
    Atualizado em: 09/05/2023 ([carlos.bastarz@inpe.br](mailto:carlos.bastarz@inpe.br))
    
    """
  
    card_parameters = pn.Card(variable, iter_fcost, date_range_slider, synoptic_time, experiment2, pn.Column(experiment, height=240), title='Parameters', collapsed=False)
    settings = pn.Column(card_parameters)
    tabs_contents = pn.Tabs(('PLOTS', plotCurves), ('TABLE', getTable))
    return pn.Column(settings, tabs_contents)

def monitor_jo_sidebar():
    card_parameters = pn.Card(variable, iter_fcost, date_range_slider, synoptic_time, experiment2, pn.Column(experiment, height=240), title='Parameters', collapsed=False)
    settings = pn.Column(card_parameters)
    return settings

def monitor_jo_main():
    tabs_contents_jb = pn.Tabs(('PLOTS', plotCurves), ('TABLE', getTable))
    tabs_contents_jo = pn.Tabs(('PLOTS', plotCurves), ('TABLE', getTable))
    tabs_contents = pn.Tabs(('Jo', pn.Column('Jo minimization.', tabs_contents_jo)), 
                            ('Jb', pn.Column('Jb minimization.', tabs_contents_jb)),
                            ('Jc', pn.Column('Jc minimization.', tabs_contents_jo)), active=1)
    main_text = pn.Column("""
    # Minimization Plots

    Navigate through the tabs to visualize the minimization results. Set the parameters on the left to update the curves. Click on the `TABLE` tab to visualize the tabular data.
    """)
    return pn.Column(main_text, tabs_contents)
