#!/usr/bin/env python
# coding: utf-8

# Usar o ambiente SCANPLOT_PANEL
# @cfbastarz, Jun/2023 (carlos.bastarz@inpe.br)

import os
import io
import intake
import requests
import colorcet as cc
import xarray as xr
import numpy as np
import pandas as pd
import geopandas as gpd
import seaborn as sns
import panel as pn
import param
import hvplot.xarray
import hvplot.pandas
import hvplot as hv
import holoviews as hvs
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from datetime import datetime
from matplotlib import pyplot as plt

from monitor_texts import MonitoringAppTexts
from monitor_dates import MonitoringAppDates

hvs.extension('bokeh')

pn.extension('katex')
pn.extension('floatpanel')
pn.extension('texteditor')
pn.extension(notifications=True)
pn.extension(sizing_mode='stretch_width')

# SCANPLOT_V2.0.0a1
# @cfbastarz, Jun/2023 (carlos.bastarz@inpe.br)


monitor_app_texts = MonitoringAppTexts()
monitor_warning_bottom_main = monitor_app_texts.warnings()

#data_catalog = intake.open_catalog('http://ftp1.cptec.inpe.br/pesquisa/das/carlos.bastarz/SMNAMonitoringApp/objeval/catalog-scantec-s0.yml')
data_catalog = intake.open_catalog('/extra2/SMNAMonitoringApp_DATA/objeval/catalog-scantec-s0.yml')

monitoring_app_dates = MonitoringAppDates()
sdate = monitoring_app_dates.getDates()[0].strip()
edate = monitoring_app_dates.getDates()[1].strip()

start_date = datetime(int(sdate[0:4]), int(sdate[4:6]), int(sdate[6:8]), int(sdate[8:10]))
end_date = datetime(int(edate[0:4]), int(edate[4:6]), int(edate[6:8]), int(edate[8:10]))
date_range = [d.strftime('%Y%m%d%H') for d in pd.date_range(start_date, end_date, freq='6h')][::-1]
date = pn.widgets.Select(name='Date', value=date_range[0], options=date_range, width=230)

Vars = [
('VTMP:925', 'Virtual Temperature @ 925 hPa [K]'),
('VTMP:850', 'Virtual Temperature @ 850 hPa [K]'),
('VTMP:500', 'Virtual Temperature @ 500 hPa [K]'),
('VTMP:250', 'Virtual Temperature @ 250 hPa [K]'),
('VTMP:200', 'Virtual Temperature @ 200 hPa [K]'),
('VTMP:150', 'Virtual Temperature @ 150 hPa [K]'),
('VTMP:070', 'Virtual Temperature @ 70 hPa [K]'),
('VTMP:050', 'Virtual Temperature @ 50 hPa [K]'),
('TEMP:850', 'Absolute Temperature @ 850 hPa [K]'),
('TEMP:500', 'Absolute Temperature @ 500 hPa [K]'),
('TEMP:250', 'Absolute Temperature @ 250 hPa [K]'),
('TEMP:200', 'Absolute Temperature @ 200 hPa [K]'),
('TEMP:150', 'Absolute Temperature @ 150 hPa [K]'),
('TEMP:070', 'Absolute Temperature @ 70 hPa [K]'),
('TEMP:050', 'Absolute Temperature @ 50 hPa [K]'),
('PSNM:000', 'Mean Sea Level Pressure [hPa]'),
('UMES:925', 'Specific Humidity @ 925 hPa [g/Kg]'),
('UMES:850', 'Specific Humidity @ 850 hPa [g/Kg]'),
('UMES:500', 'Specific Humidity @ 500 hPa [g/Kg]'),
('UMES:250', 'Specific Humidity @ 250 hPa [g/Kg]'),
('UMES:200', 'Specific Humidity @ 200 hPa [g/Kg]'),
('UMES:150', 'Specific Humidity @ 150 hPa [g/Kg]'),
('UMES:070', 'Specific Humidity @ 70 hPa [g/Kg]'),
('UMES:050', 'Specific Humidity @ 50 hPa [g/Kg]'),
('AGPL:000', 'Inst. Precipitable Water @ 1000 hPa [Kg/m2]'),
('ZGEO:850', 'Geopotential height @ 850 hPa [gpm]'),
('ZGEO:500', 'Geopotential height @ 500 hPa [gpm]'),
('ZGEO:250', 'Geopotential height @ 250 hPa [gpm]'),
('UVEL:850', 'Zonal Wind @ 850 hPa [m/s]'),
('UVEL:500', 'Zonal Wind @ 500 hPa [m/s]'),
('UVEL:250', 'Zonal Wind @ 250 hPa [m/s]'),
('UVEL:200', 'Zonal Wind @ 200 hPa [m/s]'),
('UVEL:150', 'Zonal Wind @ 150 hPa [m/s]'),
('UVEL:070', 'Zonal Wind @ 70 hPa [m/s]'),
('UVEL:050', 'Zonal Wind @ 50 hPa [m/s]'),
('VVEL:850', 'Meridional Wind @ 850 hPa [m/s]'),
('VVEL:500', 'Meridional Wind @ 500 hPa [m/s]'),
('VVEL:250', 'Meridional Wind @ 250 hPa [m/s]'),
('VVEL:200', 'Meridional Wind @ 200 hPa [m/s]'),
('VVEL:150', 'Meridional Wind @ 150 hPa [m/s]'),
('VVEL:070', 'Meridional Wind @ 70 hPa [m/s]'),
('VVEL:050', 'Meridional Wind @ 50 hPa [m/s]'), 
]    

list_var = [ltuple[0].lower() for ltuple in Vars]

date_range = '20191115122020020100'

Regs = ['gl', 'hn', 'tr', 'hs', 'as']
Refs = ['ref_gfs_no_clim.new',
        'ref_era5_no_clim.new', 
        'ref_panl_agcm_clim.new', 'ref_panl_cfsr_clim.new', 'ref_panl_no_clim.new', ]
Exps = ['EXP15', 'EXP18', 'X666']
Stats = ['RMSE', 'VIES', 'ACOR']
Tstats = ['Mudança Fracional', 'Ganho Percentual']
#
# Widgets
#

# Widgets Datas (das distribuições espaciais)
datei = datetime.strptime('2019-11-15', '%Y-%m-%d')
datef = datetime.strptime('2019-11-26', '%Y-%m-%d')

date = pn.widgets.DateSlider(name='Data', start=datei, end=datef, value=datei, format='%Y-%m-%d', width=230)
#fcts = pn.widgets.IntSlider(name='Previsão (horas)', start=0, end=264, step=24, value=0, width=230)
       
# Widget de Notificações
silence = pn.widgets.Toggle(name='🔔 Silenciar Notificações', button_type='primary', button_style='outline', value=False)

read_catalog = pn.widgets.Button(name='🎲 Ler Catálogo de Dados', button_type='primary')
file_input = pn.widgets.FileInput(name='Escolher Catálogo de Dados', accept='yml', mime_type='text/yml', multiple=False)

# Widgets Série Temporal (_st)    
varlev_st = pn.widgets.Select(name='Variable', options=[i[0] for i in Vars], value=[i[0] for i in Vars][0], disabled=False, width=230)
reg_st = pn.widgets.Select(name='Region', options=Regs, value=Regs[0], disabled=False, width=230)
ref_st = pn.widgets.Select(name='Reference', options=Refs, value=Refs[0], disabled=False, width=230)
expt_st = pn.widgets.MultiChoice(name='Experiments', options=Exps, value=[Exps[0]], disabled=False, solid=False, width=230)

# Widgets Scorecard (_sc)
Tstats = ['Percentual Gain', 'Fractional Change']
#colormap_sc = pn.widgets.Select(name='Cor do Preenchimento', value=colormaps[74], options=colormaps, width=230)
colormap_sc = pn.widgets.ColorMap(name='Colormap', options=cc.palette_n, value_name='coolwarm', width=250, margin=(0, 0, 0, 0))
invert_colors_sc = pn.widgets.Checkbox(name='Invert Colors', value=True, width=230)

statt_sc = pn.widgets.Select(name='Statistic', options=Stats, value=Stats[0], disabled=False, width=230)
tstat = pn.widgets.Select(name='Type', options=Tstats, value=Tstats[0], disabled=False, width=230)
reg_sc = pn.widgets.Select(name='Region', options=Regs, value=Regs[0], disabled=False, width=230)
ref_sc = pn.widgets.Select(name='Reference', options=Refs, value=Refs[0], disabled=False, width=230)
expt1 = pn.widgets.Select(name='Experiment 1', options=Exps, value=Exps[0], disabled=False, width=230)
expt2 = pn.widgets.Select(name='Experiment 2', options=Exps, value=Exps[0], disabled=False, width=230)

# Widgets Distribuição Espacial (_de) 
Fills = ['image', 'contour']
fill_de = pn.widgets.Select(name='Fill', options=Fills, width=230)     
#colormap_de = pn.widgets.Select(name='Cor do Preenchimento', value=colormaps[0], options=colormaps, width=230)      
colormap_de = pn.widgets.ColorMap(name='Colormap', options=cc.palette_n, value_name='coolwarm', width=250, margin=(0, 0, 0, 0))
invert_colors_de = pn.widgets.Checkbox(name='Invert Colors', value=True, width=230) 
interval = pn.widgets.IntInput(name='Intervals', value=10, step=1, start=5, end=20, width=230)     
    
state = pn.widgets.Select(name='Statistic', options=Stats, value=Stats[0], disabled=False, width=230)    
varlev_de = pn.widgets.Select(name='Variable', options=[i[0] for i in Vars], value=[i[0] for i in Vars][0], disabled=False, width=230)   
reg_de = pn.widgets.Select(name='Region', options=Regs, value=Regs[0], disabled=False, width=230)  
ref_de = pn.widgets.Select(name='Reference', options=Refs, value=Refs[0], disabled=False, width=230)     
expe_de = pn.widgets.MultiChoice(name='Experiments', options=Exps, value=[Exps[0]], disabled=False, solid=False, width=230)    
      
# Widgets Distribuição Espacial Double (_ded) 
fill_ded = pn.widgets.Select(name='Fill', value=Fills[0], options=Fills, width=230) 
#colormap_ded = pn.widgets.Select(name='Cor do Preenchimento', value=colormaps[80], options=colormaps, width=230)      
colormap_ded = pn.widgets.ColorMap(name='Colormap', options=cc.palette_n, value_name='coolwarm', width=250, margin=(0, 0, 0, 0))
invert_colors_ded = pn.widgets.Checkbox(name='Invert Colors', value=True, width=230) 
swipe_ded = pn.widgets.Checkbox(name='Join Figures', value=False, width=230) 
show_diff_ded = pn.widgets.Checkbox(name='Show Difference', value=False, width=230) 

varlev_ded = pn.widgets.Select(name='Variable', disabled=False, width=230)    
reg_ded = pn.widgets.Select(name='Region', disabled=False, width=230)    
ref_ded = pn.widgets.Select(name='Reference', disabled=False, width=230)    
expe_ded = pn.widgets.MultiChoice(name='Experiments', disabled=False, solid=False, width=230)  
exp1_ded = pn.widgets.Select(name='Experiment 1', disabled=False, width=230)
exp2_ded = pn.widgets.Select(name='Experiment 2', disabled=False, width=230)

# Variável lógica para determinar se o arquivo de catálogo já foi lido (True) ou não (False)
loaded = pn.widgets.Checkbox(name='Catálogo Carregado', value=True, disabled=True)

## Botão da paleta de cores
#show_color_pallete = pn.widgets.Button(name='🎨 Paletas de Cores...', button_type='default')

#
# Funções de plotagem
#

def get_min_max_ds(ds):
    return ds.compute().min().item(), ds.compute().max().item()

def get_df(reg, exp, stat, ref, varlev):
    kname = 'scantec-' + reg + '-' + stat + '-' + exp.lower() + '-' + ref + '-table'
    #print(kname)
    #if data_catalog is not None:
    df = data_catalog[kname].read()
    df.set_index('Unnamed: 0', inplace=True)
    df.index.name = '' 
    return df

@pn.depends(varlev_st, reg_st, ref_st, expt_st, loaded)
def plotCurves(varlev_st, reg_st, ref_st, expt_st, loaded):
    
    if loaded and varlev_st and reg_st and ref_st and expt_st:       
        
        for i in Vars:
            if i[0] == varlev_st:
                nexp_ext = i[1]

        varlev_st = varlev_st.lower()

        height=500    
        
        for count, i in enumerate(expt_st):
            if count == 0:
                exp = expt_st[count] 
                #print(reg_st, exp, 'vies', ref_st, varlev_st)
                df_vies = get_df(reg_st, exp, 'vies', ref_st, varlev_st)
            
                if df_vies is not None:
            
                    ax_vies = df_vies.hvplot.line(x='%Previsao',
                                          y=varlev_st,
                                          xlabel='Horas',
                                          ylabel='VIES',
                                          shared_axes=False,
                                          grid=True,
                                          line_width=3,
                                          label=str(exp),
                                          fontsize={'ylabel': '12px', 'ticks': 10},
                                          responsive=True,
                                          height=height,
                                          title='VIES' + ' - ' + str(nexp_ext))
            
                    df_rmse = get_df(reg_st, exp, 'rmse', ref_st, varlev_st)
        
                    ax_rmse = df_rmse.hvplot.line(x='%Previsao',
                                          y=varlev_st,
                                          xlabel='Horas',
                                          ylabel='RMSE',
                                          shared_axes=False,
                                          grid=True,
                                          line_width=3,
                                          label=str(exp),
                                          fontsize={'ylabel': '12px', 'ticks': 10},
                                          responsive=True,
                                          height=height,
                                          title='RMSE' + ' - ' + str(nexp_ext))            
                        
                    df_acor = get_df(reg_st, exp, 'acor', ref_st, varlev_st)
            
                    ax_acor = df_acor.hvplot.line(x='%Previsao', 
                                          y=varlev_st,
                                          xlabel='Horas',
                                          ylabel='ACOR',
                                          shared_axes=False,
                                          grid=True,
                                          line_width=3,
                                          label=str(exp),
                                          fontsize={'ylabel': '12px', 'ticks': 10},     
                                          responsive=True,
                                          height=height,
                                          title='ACOR' + ' - ' + str(nexp_ext))  
            
            else:
            
                exp = expt_st[count]
            
                df_vies = get_df(reg_st, exp, 'vies', ref_st, varlev_st)
            
                if df_vies is not None:
            
                    ax_vies *= df_vies.hvplot.line(x='%Previsao', 
                                           y=varlev_st, 
                                           xlabel='Horas', 
                                           ylabel='VIES',
                                           shared_axes=False,
                                           grid=True,
                                           line_width=3,
                                           label=str(exp),  
                                           fontsize={'ylabel': '12px', 'ticks': 10},
                                           responsive=True,
                                           height=height,
                                           title='VIES' + ' - ' + str(nexp_ext))
            
                    df_rmse = get_df(reg_st, exp, 'rmse', ref_st, varlev_st)
            
                    ax_rmse *= df_rmse.hvplot.line(x='%Previsao',
                                           y=varlev_st,
                                           xlabel='Horas',
                                           ylabel='RMSE', 
                                           shared_axes=False,
                                           grid=True,
                                           line_width=3,
                                           label=str(exp), 
                                           fontsize={'ylabel': '12px', 'ticks': 10},
                                           responsive=True,
                                           height=height,
                                           title='RMSE' + ' - ' + str(nexp_ext))       

                    df_acor = get_df(reg_st, exp, 'acor', ref_st, varlev_st)
            
                    ax_acor *= df_acor.hvplot.line(x='%Previsao',
                                           y=varlev_st,
                                           xlabel='Horas',
                                           ylabel='ACOR', 
                                           shared_axes=False,
                                           grid=True,
                                           line_width=3,
                                           label=str(exp),      
                                           fontsize={'ylabel': '12px', 'ticks': 10},
                                           responsive=True,
                                           height=height,
                                           title='ACOR' + ' - ' + str(nexp_ext))             
       
            if ax_vies is not None:
                ax_vies *= hvs.HLine(0).opts(line_width=1, shared_axes=False, responsive=True, height=height, line_color='black', line_dash='dashed')
                ax_rmse *= hvs.HLine(0).opts(line_width=1, shared_axes=False, responsive=True, height=height, line_color='black', line_dash='dashed')
                ax_acor *= hvs.HLine(0.6).opts(line_width=1, shared_axes=False, responsive=True, height=height, line_color='black', line_dash='dashed')    
            

        if ax_vies is not None:
            ax_vies.opts(axiswise=True, legend_position='bottom_left')
            ax_rmse.opts(axiswise=True, legend_position='top_left')
            ax_acor.opts(axiswise=True, legend_position='bottom_left')
    
        layout = hvs.Layout(ax_vies + ax_rmse + ax_acor).cols(3)
    
    else:
        
        layout = pn.Column(
                    pn.pane.Markdown("""
                    # Série Temporal
                    
                    A avaliação por meio de série temporal permite verificar o comportamento de parâmetros (variáveis) do modelo ao longo do tempo, seja por meio da verificação dos erros aleatórios, sistemáticos e habilidade de previsão.
                    """),
                    pn.pane.Alert('⛔ **Atenção:** Nada para mostrar! Para começar, selecione um catálogo de dados ou aguarde a execução da função de plotagem.', alert_type='danger')
                )
    
    return layout
    
@pn.depends(statt_sc, tstat, reg_sc, ref_sc, expt1, expt2, colormap_sc, invert_colors_sc, loaded)    
def plotScorecard(statt_sc, tstat, reg_sc, ref_sc, expt1, expt2, colormap_sc, invert_colors_sc, loaded):
    
    if loaded and statt_sc and tstat and reg_sc and ref_sc and expt1 and expt2 and colormap_sc and invert_colors_sc:   
    
        dfs = globals()['data_catalog']
    
        kname1 = 'scantec-' + reg_sc + '-' + statt_sc.lower() + '-' + expt1.lower() + '-' + ref_sc + '-table'
        kname2 = 'scantec-' + reg_sc + '-' + statt_sc.lower() + '-' + expt2.lower() + '-' + ref_sc + '-table'
    
        df1 = dfs[kname1].read()
        df2 = dfs[kname2].read()
        
        df1.set_index('Unnamed: 0', inplace=True)
        df1.index.name = ''   

        df2.set_index('Unnamed: 0', inplace=True)
        df2.index.name = ''      
        
        p_table1 = pd.pivot_table(df1, index='%Previsao', values=list_var)
        p_table2 = pd.pivot_table(df2, index='%Previsao', values=list_var)
 
        if invert_colors_sc == True:
            cmap = colormap_sc[::-1]
        else:
            cmap = colormap_sc
    
        if tstat == 'Percentual Gain':
            # Porcentagem de ganho
            if statt_sc == 'ACOR':
                #score_table = ((p_table2[1:].T - p_table1[1:].T) / (1.0 - p_table1[1:].T)) * 100
                score_table = ((p_table2.T - p_table1.T) / (1.0 - p_table1.T)) * 100
            elif statt_sc == 'RMSE' or statt_sc == 'VIES':
                #score_table = ((p_table2[1:].T - p_table1[1:].T) / (0.0 - p_table1[1:].T)) * 100
                score_table = ((p_table2.T - p_table1.T) / (0.0 - p_table1.T)) * 100
        elif tstat == 'Fractional Change':
            # Mudança fracional
            #score_table = (1.0 - (p_table2[1:].T / p_table1[1:].T))
            score_table = (1.0 - (p_table2.T / p_table1.T))
 
        if score_table.isnull().values.any():

            #print(score_table)

            # Tentativa de substituir os NaN - que aparecem quando vies e rmse são iguais a zero
            score_table = score_table.fillna(0.0000001)

            # Tentativa de substituir valores -inf por um número não muito grande
            score_table.replace([np.inf, -np.inf], 1000000, inplace=True)

            if silence.value is False: pn.state.notifications.info('NaN or Inf values may have been replaced by other values.', duration=5000) 

        ## Figura
        plt.figure(figsize = (9,6))

        sns.set(style='whitegrid', font_scale=0.450)
        sns.set_context(rc={'xtick.major.size':  1.5,  'ytick.major.size': 1.5,
                            'xtick.major.pad':   0.05,  'ytick.major.pad': 0.05,
                            'xtick.major.width': 0.5, 'ytick.major.width': 0.5,
                            'xtick.minor.size':  1.5,  'ytick.minor.size': 1.5,
                            'xtick.minor.pad':   0.05,  'ytick.minor.pad': 0.05,
                            'xtick.minor.width': 0.5, 'ytick.minor.width': 0.5})

        if tstat == 'Percentual Gain':
            ax = sns.heatmap(score_table, annot=True, fmt='.3f', cmap=cmap, 
                             vmin=-100, vmax=100, center=0, linewidths=0.25, square=False,
                             cbar_kws={'shrink': 1.0, 
                                       'ticks': np.arange(-100,110,10),
                                       'pad': 0.01,
                                       'orientation': 'vertical'})

            cbar = ax.collections[0].colorbar
            cbar.set_ticks([-100, -50, 0, 50, 100])
            cbar.set_ticklabels(['pior', '-50%', '0', '50%', 'melhor'])
            cbar.ax.tick_params(labelsize=7)    

            plt.title('Ganho ' + str(statt_sc) + ' (%) - ' + expt1 + ' Vs. ' + expt2, fontsize=8)

        elif tstat == 'Fractional Change':
            ax = sns.heatmap(score_table, annot=True, fmt='.3f', cmap=cmap, 
                             vmin=-1, vmax=1, center=0, linewidths=0.25, square=False,
                             cbar_kws={'shrink': 1.0, 
                                       'ticks': np.arange(-1,2,1),
                                       'pad': 0.01,
                                       'orientation': 'vertical'})

            cbar = ax.collections[0].colorbar
            cbar.set_ticks([-1, -0.5, 0, 0.5, 1])
            cbar.set_ticklabels(['pior', '-0.5', '0', '0.5', 'melhor'])
            cbar.ax.tick_params(labelsize=7)    

            plt.title('Fractional Change ' + str(statt_sc) + " - " + expt1 + ' Vs. ' + expt2, fontsize=8)

        plt.xlabel('Forecast Length')
        plt.yticks(fontsize=7)
        #plt.xticks(rotation=90, fontsize=6)    
        plt.xticks(fontsize=7)  
        plt.tight_layout()        

        layout = ax.get_figure()

        plt.close()

    else:
        
        layout = pn.Column(
                    pn.pane.Markdown("""
                    # Scorecard
                    
                    Para uma variável alpha (e.g., pressão, temperatura, umidade, componentes do vento etc.), podem ser calculadas duas métricas que permitem quantificar a variação relativa entre dois experimentos avaliados pelo SCANTEC. As métricas aplicadas são o Ganho Percentual e a Mudança Fracional* e ambas podem ser calculadas com base nas tabelas de estatisticas do SCANTEC. Estas métricas podem ser utilizadas quando se quiser ter uma visão imediata sobre as melhorias obtidas entre duas versões de um modelo ou entre dois experimentos de um mesmo modelo.
                    """),
                    pn.pane.Alert('⛔ **Atenção:** Nada para mostrar! Para começar, selecione um catálogo de dados ou aguarde a execução da função de plotagem.', alert_type='danger')
                )        
        
    return layout

@pn.depends(state, varlev_de, reg_de, ref_de, date, colormap_de, invert_colors_de, interval, expe_de, fill_de)
def plotFields(state, varlev_de, reg_de, ref_de, date, colormap_de, invert_colors_de, interval, expe_de, fill_de):
    
    date = str(date) + ' 12:00' # consertar...

    #print(varlev_de)

    var = varlev_de.replace(':', '').lower()
    
    for i in Vars:
        if i[0] == varlev_de:
            nexp_ext = i[1]
    
    if invert_colors_de == True:
        cmap = colormap_de[::-1]
    else:
        cmap = colormap_de
    
    if reg_de == 'as':
        data_aspect=1
        frame_height=700
    elif (reg_de == 'hn') or (reg_de == 'hs'):
        data_aspect=1
        frame_height=225        
    elif reg_de == 'tr':
        data_aspect=1
        frame_height=150         
    elif reg_de == 'gl': 
        data_aspect=1
        frame_height=590
  
    for count, i in enumerate(expe_de):
        if count == 0:
            exp = expe_de[count]
            kname = 'scantec-' + reg_de + '-' + state.lower() + '-' + exp.lower() + '-' + ref_de + '-field'
            if data_catalog is not None:
                ds = data_catalog[kname].to_dask()
            
            vmin, vmax = get_min_max_ds(ds[var])
                       
            if fill_de == 'image':
            
                ax = ds.sel(time=date).hvplot.image(x='lon',
                                                    y='lat',
                                                    z=var,
                                                    data_aspect=data_aspect,
                                                    frame_height=frame_height, 
                                                    cmap=cmap, 
                                                    projection=ccrs.PlateCarree(), 
                                                    coastline=True,
                                                    rasterize=True,
                                                    clim=(vmin,vmax),
                                                    title=str(state) + ' - ' + str(nexp_ext) + ' (' + str(date) + ')')    
                
            elif fill_de == 'contour':
                
                ax = ds.sel(time=date).hvplot.contour(x='lon',
                                                      y='lat',
                                                      z=var,
                                                      data_aspect=data_aspect,
                                                      frame_height=frame_height, 
                                                      cmap=cmap, 
                                                      projection=ccrs.PlateCarree(), 
                                                      coastline=True,
                                                      rasterize=True,
                                                      clim=(vmin,vmax),
                                                      levels=interval,
                                                      line_width=2,
                                                      title=str(state) + ' - ' + str(nexp_ext) + ' (' + str(date) + ')')  
             
        else:  
            
            ax *= ds.sel(time=date).hvplot.contour(x='lon',
                                                   y='lat',
                                                   z=var,
                                                   data_aspect=data_aspect,
                                                   frame_height=frame_height, 
                                                   cmap=cmap, 
                                                   projection=ccrs.PlateCarree(), 
                                                   coastline=True,
                                                   clim=(vmin,vmax),
                                                   colorbar=True,
                                                   levels=interval,
                                                   line_width=4,
                                                   line_dash='dashed',
                                                   title=str(state) + ' - ' + str(nexp_ext) + ' (' + str(date) + ')') 
   
    return ax

@pn.depends(state, varlev_ded, reg_ded, ref_ded, date, colormap_ded, invert_colors_ded, interval, fill_ded, swipe_ded, show_diff_ded, exp1_ded, exp2_ded)
def plotFieldsDouble(state, varlev_ded, reg_ded, ref_ded, date, colormap_ded, invert_colors_ded, interval, fill_ded, swipe_ded, show_diff_ded, exp1_ded, exp2_ded):
    
    if loaded and state and varlev_ded and reg_ded and ref_ded and date and colormap_ded and interval and fill_ded and exp1_ded and exp2_ded:
    
        datefmt = str(date) + ' 12:00' # consertar...

        var = varlev_ded.replace(':', '').lower()

        for i in Vars:
            if i[0] == varlev_ded:
                nexp_ext = i[1]

        if invert_colors_ded == True:
            cmap = colormap_ded[::-1]
        else:
            cmap = colormap_ded

        if reg_ded == 'as':
            data_aspect=1
            frame_height=800
        elif (reg_ded == 'hn') or (reg_ded == 'hs'):
            data_aspect=1
            frame_height=235        
        elif reg_ded == 'tr':
            data_aspect=1
            frame_height=155         
        elif reg_ded == 'gl': 
            data_aspect=1
            frame_height=340
            frame_height=390

        exp1 = exp1_ded
        kname1 = 'scantec-' + reg_ded + '-' + state.lower() + '-' + exp1.lower() + '-' + ref_ded + '-field'
        if data_catalog is not None:
            ds1 = data_catalog[kname1].to_dask()

        exp2 = exp2_ded
        kname2 = 'scantec-' + reg_ded + '-' + state.lower() + '-' + exp2.lower() + '-' + ref_ded + '-field'
        if data_catalog is not None:
            ds2 = data_catalog[kname2].to_dask()

        #vmin, vmax = get_min_max_ds(ds1[var])

        if show_diff_ded:

            #ds_diff = ds1[var].sel(time=datefmt) - ds2[var].sel(time=datefmt)
            ds_diff = ds1[var].isel(time=0) - ds2[var].isel(time=0)

            vmin, vmax = get_min_max_ds(ds_diff)

            if fill_ded == 'image':

                ax1 = ds1.sel(time=datefmt).hvplot.image(x='lon',
                                                      y='lat',
                                                      z=var,
                                                      data_aspect=data_aspect,
                                                      frame_height=frame_height, 
                                                      #frame_width=650,
                                                      cmap=cmap, 
                                                      projection=ccrs.PlateCarree(), 
                                                      coastline=True,
                                                      rasterize=True,
                                                      #datashade=True,
                                                      colorbar=True,
                                                      #features=['borders', 'coastline', 'lakes', 'land', 'ocean', 'rivers', 'states'],   
                                                      clim=(vmin,vmax),
                                                      title=str(state) + ' - ' + str(exp1) + ' - ' + str(nexp_ext) + ' (' + str(datefmt) + ')')    

                ax2 = ds2.sel(time=datefmt).hvplot.image(x='lon',
                                                      y='lat',
                                                      z=var,
                                                      data_aspect=data_aspect,
                                                      frame_height=frame_height, 
                                                      #frame_width=650,
                                                      cmap=cmap, 
                                                      projection=ccrs.PlateCarree(), 
                                                      coastline=True,
                                                      rasterize=True,
                                                      #features=['borders', 'coastline', 'lakes', 'land', 'ocean', 'rivers', 'states'],
                                                      #datashade=True,  
                                                      colorbar=True,   
                                                      clim=(vmin,vmax),
                                                      title=str(state) + ' - ' + str(exp2) + ' - ' + str(nexp_ext) + ' (' + str(datefmt) + ')')         

                axd = (ds1.sel(time=datefmt) - ds2.sel(time=datefmt)).hvplot.image(x='lon',
                                                                                  y='lat',
                                                                                  z=var,
                                                                                  data_aspect=data_aspect,
                                                                                  frame_height=frame_height, 
                                                                                  #frame_width=650,
                                                                                  cmap=cmap, 
                                                                                  projection=ccrs.PlateCarree(), 
                                                                                  coastline=True,
                                                                                  rasterize=True,
                                                                                  #features=['borders', 'coastline', 'lakes', 'land', 'ocean', 'rivers', 'states'], 
                                                                                  #datashade=True,
                                                                                  colorbar=True,
                                                                                  clim=(vmin,vmax),
                                                                                  title=str(state) + ' - ' + 'Dif. (' + str(exp1) + '-' + str(exp2) + ') - ' + str(nexp_ext) + ' (' + str(datefmt) + ')')    

            elif fill_ded == 'contour':

                ax1 = ds1.sel(time=datefmt).hvplot.contour(x='lon',
                                                        y='lat',
                                                        z=var,
                                                        data_aspect=data_aspect,
                                                        frame_height=frame_height, 
                                                        #frame_width=650,
                                                        cmap=cmap, 
                                                        projection=ccrs.PlateCarree(), 
                                                        coastline=True,
                                                        rasterize=True,
                                                        #features=['borders', 'coastline', 'lakes', 'land', 'ocean', 'rivers', 'states'],
                                                        clim=(vmin,vmax),
                                                        levels=interval,
                                                        line_width=1,
                                                        title=str(state) + ' - ' + str(exp1) + ' - ' + str(nexp_ext) + ' (' + str(datefmt) + ')')    

                ax2 = ds2.sel(time=datefmt).hvplot.contour(x='lon',
                                                        y='lat',
                                                        z=var,
                                                        data_aspect=data_aspect,
                                                        frame_height=frame_height, 
                                                        #frame_width=650,
                                                        cmap=cmap, 
                                                        projection=ccrs.PlateCarree(), 
                                                        coastline=True,
                                                        rasterize=True,
                                                        #features=['borders', 'coastline', 'lakes', 'land', 'ocean', 'rivers', 'states'],
                                                        clim=(vmin,vmax),
                                                        levels=interval,
                                                        line_width=1,
                                                        title=str(state) + ' - ' + str(exp2) + ' - ' + str(nexp_ext) + ' (' + str(datefmt) + ')')                  

                axd = (ds1.sel(time=datefmt) - ds2.sel(time=datefmt)).hvplot.contour(x='lon',
                                                                                    y='lat',
                                                                                    z=var,
                                                                                    data_aspect=data_aspect,
                                                                                    frame_height=frame_height, 
                                                                                    #frame_width=650,
                                                                                    cmap=cmap, 
                                                                                    projection=ccrs.PlateCarree(), 
                                                                                    coastline=True,
                                                                                    rasterize=True,
                                                                                    #features=['borders', 'coastline', 'lakes', 'land', 'ocean', 'rivers', 'states'],
                                                                                    #clim=(vmin,vmax),
                                                                                    levels=interval,
                                                                                    line_width=1,
                                                                                    title=str(state) + ' - ' + str(exp1) + ' - ' + str(nexp_ext) + ' (' + str(datefmt) + ')')          
        else:

            vmin, vmax = get_min_max_ds(ds1[var])

            if fill_ded == 'image':

                ax1 = ds1.sel(time=datefmt).hvplot.image(x='lon',
                                                      y='lat',
                                                      z=var,
                                                      data_aspect=data_aspect,
                                                      frame_height=frame_height, 
                                                      #frame_width=650,
                                                      cmap=cmap, 
                                                      projection=ccrs.PlateCarree(), 
                                                      coastline=True,
                                                      rasterize=True,
                                                      #datashade=True,
                                                      colorbar=True,
                                                      #features=['borders', 'coastline', 'lakes', 'land', 'ocean', 'rivers', 'states'],   
                                                      clim=(vmin,vmax),
                                                      title=str(state) + ' - ' + str(exp1) + ' - ' + str(nexp_ext) + ' (' + str(datefmt) + ')')    

                ax2 = ds2.sel(time=datefmt).hvplot.image(x='lon',
                                                      y='lat',
                                                      z=var,
                                                      data_aspect=data_aspect,
                                                      frame_height=frame_height, 
                                                      #frame_width=650,
                                                      cmap=cmap, 
                                                      projection=ccrs.PlateCarree(), 
                                                      coastline=True,
                                                      rasterize=True,
                                                      #features=['borders', 'coastline', 'lakes', 'land', 'ocean', 'rivers', 'states'],
                                                      #datashade=True,  
                                                      colorbar=True,   
                                                      clim=(vmin,vmax),
                                                      title=str(state) + ' - ' + str(exp2) + ' - ' + str(nexp_ext) + ' (' + str(datefmt) + ')')       

            elif fill_ded == 'contour':

                ax1 = ds1.sel(time=datefmt).hvplot.contour(x='lon',
                                                        y='lat',
                                                        z=var,
                                                        data_aspect=data_aspect,
                                                        frame_height=frame_height, 
                                                        #frame_width=650,
                                                        cmap=cmap, 
                                                        projection=ccrs.PlateCarree(), 
                                                        coastline=True,
                                                        rasterize=True,
                                                        #features=['borders', 'coastline', 'lakes', 'land', 'ocean', 'rivers', 'states'],
                                                        clim=(vmin,vmax),
                                                        levels=interval,
                                                        line_width=1,
                                                        title=str(state) + ' - ' + str(exp1) + ' - ' + str(nexp_ext) + ' (' + str(datefmt) + ')')    

                ax2 = ds2.sel(time=datefmt).hvplot.contour(x='lon',
                                                        y='lat',
                                                        z=var,
                                                        data_aspect=data_aspect,
                                                        frame_height=frame_height, 
                                                        #frame_width=650,
                                                        cmap=cmap, 
                                                        projection=ccrs.PlateCarree(), 
                                                        coastline=True,
                                                        rasterize=True,
                                                        #features=['borders', 'coastline', 'lakes', 'land', 'ocean', 'rivers', 'states'],
                                                        clim=(vmin,vmax),
                                                        levels=interval,
                                                        line_width=1,
                                                        title=str(state) + ' - ' + str(exp2) + ' - ' + str(nexp_ext) + ' (' + str(datefmt) + ')')  

        if show_diff_ded:    
            #layout = pn.Column(ax1, ax2, axd, sizing_mode='stretch_width')
            layout = pn.Column(axd, sizing_mode='stretch_width')
            #if reg_ded == 'as':
            #    layout = hvs.Layout(ax1 + ax2 + axd).cols(3)
            #else:
            #    layout = hvs.Layout(ax1 + ax2 + axd).cols(1)
        else:
            if swipe_ded:
                layout = pn.Swipe(ax1, ax2, value=5)
            else:
                if reg_ded == 'as':# or reg_ded == 'gl':
                    layout = hvs.Layout(ax1 + ax2).cols(2)
                else:
                    layout = hvs.Layout(ax1 + ax2).cols(1)

        if silence.value is False: pn.state.notifications.info('Colors may represent different values ranges.', duration=5000)

    else:
        
        layout = pn.Column(
                    pn.pane.Markdown("""
                    # Spatial Distribution
                    
                    This evaluation is made by looking at the statistics spatial distribution, which allows to check the skill of model parameters (variables) along the forecast length.
                    """),
                    pn.pane.Alert('⛔ **Error:** Nothing to show! To start, choose a data catalog or wait the plotting to finish.', alert_type='danger')
                )          
        
    return layout
    
def LayoutSidebarObjEval():

    card1 = pn.Card(pn.Row(date, pn.widgets.TooltipIcon(value='Choose a date', align='start')), 
                    pn.Row(varlev_st, pn.widgets.TooltipIcon(value='Choose a variable and level', align='start')), 
                    pn.Row(reg_st, pn.widgets.TooltipIcon(value='Choose a region', align='start')), 
                    pn.Row(ref_st, pn.widgets.TooltipIcon(value='Choose a reference', align='start')), 
                    pn.Row(expt_st, pn.widgets.TooltipIcon(value='Choose one or more experiments', align='start')), 
                    title='Time Series', collapsed=False)
    
    card2 = pn.Card(pn.Row(statt_sc, pn.widgets.TooltipIcon(value='Choose a statistic', align='start')), 
                    pn.Row(tstat, pn.widgets.TooltipIcon(value='Choose a score', align='start')), 
                    pn.Row(reg_sc, pn.widgets.TooltipIcon(value='Choose a region', align='start')), 
                    pn.Row(ref_sc, pn.widgets.TooltipIcon(value='Choose a reference', align='start')), 
                    pn.Row(expt1, pn.widgets.TooltipIcon(value='Choose a experiment', align='start')), 
                    pn.Row(expt2, pn.widgets.TooltipIcon(value='Choose a experiment', align='start')), 
                    pn.Row(colormap_sc, pn.widgets.TooltipIcon(value='Choose a colormap', align='start')), 
                    pn.Row(invert_colors_sc, pn.widgets.TooltipIcon(value='Invert the color range in the colormap', align='start')), 
                    title='Scorecard', collapsed=True)
    
    card3 = pn.Card(pn.Row(state, pn.widgets.TooltipIcon(value='Choose a statistic', align='start')), 
                    pn.Row(varlev_de, pn.widgets.TooltipIcon(value='Choose a variable and level', align='start')), 
                    pn.Row(reg_de, pn.widgets.TooltipIcon(value='Choose a region', align='start')), 
                    pn.Row(ref_de, pn.widgets.TooltipIcon(value='Choose a reference', align='start')), 
                    pn.Row(date, pn.widgets.TooltipIcon(value='Choose a date', align='start')), 
                    pn.Row(colormap_de, pn.widgets.TooltipIcon(value='Choose a colormap', align='start')), 
                    pn.Row(invert_colors_de, pn.widgets.TooltipIcon(value='Invert the color range in the colormap', align='start')), 
                    pn.Row(interval, pn.widgets.TooltipIcon(value='Choose the contour invervals', align='start')), 
                    pn.Row(expe_de, pn.widgets.TooltipIcon(value='Choose a experiment', align='start')), 
                    pn.Row(fill_de, pn.widgets.TooltipIcon(value='Choose a experiment', align='start')), 
                    title='Spatial Distribution', collapsed=True)

    # Função para alternar os estados dos cards
    def toggle_cards(event):
        if event.new == False:  # Se um card foi aberto, fecha o outro
            if event.obj is card1:
                card2.collapsed = True
                card3.collapsed = True
            elif event.obj is card2:
                card1.collapsed = True 
                card3.collapsed = True
            elif event.obj is card3:
                card1.collapsed = True
                card2.collapsed = True

    # Monitorando mudanças no estado `collapsed`
    card1.param.watch(toggle_cards, 'collapsed')
    card2.param.watch(toggle_cards, 'collapsed')
    card3.param.watch(toggle_cards, 'collapsed')

    global cards_objeval
    cards_objeval = [card1, card2, card3]

    card_parameters = pn.Card('Click to expand cards.', card1, card2, card3, title='Parameters', collapsed=False)

    return pn.Column(card_parameters)

def LayoutMainObjEval():
    main_text = pn.Column("""
    # Objective Evaluation

    Set the parameters on the left to update the map below and explore our analysis features.
    """)

    tabs_objeval = pn.Tabs(('TIME SERIES', pn.Column('Time series of bias, root mean square error and anomaly correlation for a variable and level for a particular region with respect to a climatology.', plotCurves)), 
                             ('SCORECARD', pn.Column('Scorecard of bias, root mean square error and anomaly correlation for all variables and levels for a time range over a particular region with respect to a climatology.', plotScorecard)),
                             ('SPATIAL DISTRIBUTION', pn.Column('Spatial distribution of bias and root square error for a variable and level for a particular region with respect to a climatology.', plotFields)),
                             dynamic=True)
    
    # Função para abrir o card correspondente e fechar os outros
    def on_tab_change(event):
        index = event.new  # Obtém o índice da aba selecionada
        for i, card in enumerate(cards_objeval):
            card.collapsed = i != index  # Abre o card correspondente e fecha os outros

    # Monitorando mudanças na aba selecionada
    tabs_objeval.param.watch(on_tab_change, "active")    

    return pn.Column(main_text, tabs_objeval,  monitor_warning_bottom_main, sizing_mode="stretch_both")
