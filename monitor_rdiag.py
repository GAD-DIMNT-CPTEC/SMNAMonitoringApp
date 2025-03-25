#!/usr/bin/env python
# coding: utf-8

import os
import random
import intake
import hvplot.pandas
import pandas as pd
import panel as pn



#import os
#import xarray as xr
#import hvplot.xarray
#import hvplot.pandas
#import pandas as pd
#import panel as pn
#import intake
#import cartopy.crs as ccrs
#import cartopy.feature as cfeature
#import geoviews as gv
#import geopandas as gpd
#import holoviews as hvs
#from datetime import datetime
#from holoviews.operation.datashader import rasterize
#import spatialpandas as spd

from datetime import datetime

from monitor_texts import MonitoringAppTexts
from monitor_dates import MonitoringAppDates

pn.extension()

monitor_app_texts = MonitoringAppTexts()
monitor_warning_bottom_main = monitor_app_texts.warnings()

#catalog_diag_conv_01 = intake.open_catalog('http://ftp1.cptec.inpe.br/pesquisa/das/carlos.bastarz/SMNAMonitoringApp/rdiag/catalog_diag_conv_01.yml')
#catalog_diag_conv_03 = intake.open_catalog('http://ftp1.cptec.inpe.br/pesquisa/das/carlos.bastarz/SMNAMonitoringApp/rdiag/catalog_diag_conv_03.yml')
catalog_diag_conv_01 = intake.open_catalog('/extra2/SMNAMonitoringApp_DATA/rdiag/catalog_diag_conv_01.yml')
catalog_diag_conv_03 = intake.open_catalog('/extra2/SMNAMonitoringApp_DATA/rdiag/catalog_diag_conv_03.yml')

monitoring_app_dates = MonitoringAppDates()
sdate = monitoring_app_dates.getDates()[0].strip()
edate = monitoring_app_dates.getDates()[1].strip()

start_date = datetime(int(sdate[0:4]), int(sdate[4:6]), int(sdate[6:8]), int(sdate[8:10]))
end_date = datetime(int(edate[0:4]), int(edate[4:6]), int(edate[6:8]), int(edate[8:10]))
date_range = [d.strftime('%Y%m%d%H') for d in pd.date_range(start_date, end_date, freq='6h')][::-1]
date = pn.widgets.Select(name='Date', value=date_range[3], options=date_range, width=235)

loop = pn.widgets.Select(name='Loop', value='01', options=['01', '03'], width=230)

Tiles = ['CartoDark', 'CartoLight', 'EsriImagery', 'EsriNatGeo', 'EsriUSATopo',
         'EsriTerrain', 'EsriStreet', 'EsriReference', 'OSM', 'OpenTopoMap']
tile = pn.widgets.Select(name='Tiles', value=Tiles[8], options=Tiles, width=230)

# From the catalogs, assemble a dictionary with all the kx values:
variable_list = ['q', 'ps', 't', 'uv', 'gps']
zlevs = [1000.0, 900.0, 800.0, 700.0, 600.0, 500.0, 400.0, 300.0, 250.0, 200.0, 150.0, 100.0, 50.0, 0.0]

_kx_values = {'q':   [181, 120, 187, 180, 183],
              'ps':  [181, 180, 120, 187, 183],
              't':   [181, 180, 120, 187, 183, 130, 126],
              'uv':  [257,  258,  281,  280,  253,  243,  254,  220,  287,  221,  284,  230,  244,  259,  252,  242,  250,  210,  229,  224,  282],
              'gps': [42, 269, 5, 44, 43, 3, 754, 752, 755, 753, 751, 750]}

_kx_valuesn = _kx_values.copy()
_kx_valuess = _kx_values.copy()

varn = pn.widgets.Select(name='Variable', value=variable_list[0], options=variable_list, width=230)
kxn = pn.widgets.MultiChoice(name='kx', value=_kx_values[varn.value], options=_kx_values[varn.value], solid=False, width=230)

@pn.depends(varn.param.value, watch=True)
def _update_kx_valuesn(select_varn):
    kx_valuesn = _kx_valuesn[select_varn]
    kxn.options = kx_valuesn
    kxn.value = kx_valuesn

vars = pn.widgets.Select(name='Variable', value=variable_list[0], options=variable_list, width=230)
kxs = pn.widgets.MultiChoice(name='kx', value=_kx_values[vars.value], options=_kx_values[vars.value], solid=False, width=230)

@pn.depends(vars.param.value, watch=True)
def _update_kx_valuess(select_vars):
    kx_valuess = _kx_valuess[select_vars]
    kxs.options = kx_valuess
    kxs.value = kx_valuess

level = pn.widgets.Select(name='Level', value=zlevs[0], options=zlevs, width=230)
iuse = pn.widgets.Select(name='iuse', value=1, options=[-1, 1], width=230)

by_level = pn.widgets.Toggle(name='by Level', value=False, button_type='success', width=230)
by_kx = pn.widgets.Toggle(name='by kx', value=False, button_type='success', width=230)

@pn.cache
def loadData(lfname, loop):
    try:
        if loop == '01':
            ax = catalog_diag_conv_01[lfname].read()
        elif loop == '03':
            ax = catalog_diag_conv_03[lfname].read()
    except:
        ax = monitor_app_texts.warnings_rdiag(lfname + ' (loadData)')
    return ax

@pn.depends(vars, kxs, level, iuse, date, loop, tile)
def plotPtmap(vars, kxs, level, iuse, date, loop, tile):
    try:
        lfname = str(vars) + '-diag_conv_' + str(loop) + '_' + str(date)
        #print(lfname)
        obsInfo = loadData(lfname, loop)
        df = obsInfo

        maskl = df['press'] == level
        dffl = df[maskl]

        maski = dffl['iuse'] == iuse
        dffi = dffl[maski]

        instr = getVarInfo(kxs, vars, 'instrument')
        label = '\n'.join(wrap(vars + '-' + str(kxs) + ' | ' + instr,30))

        ax = dffi.hvplot(global_extent=True,
                         grid=True,
                         tiles=tile,
                         title=label,
                         frame_height=750)
    except:
        ax = monitor_app_texts.warnings_rdiag(lfname + ' (plotPtmap)')
    return pn.Column(ax) 

@pn.depends(vars, kxs, level, iuse, date, loop, tile)
def plotPtmapMulti(vars, kxs, level, iuse, date, loop, tile):
    try:
        lfname = str(vars) + '-diag_conv_' + str(loop) + '_' + str(date)
        #print(lfname)
        obsInfo = loadData(lfname, loop)
        df = obsInfo.loc[kxs]

        maskl = df['press'] == level
        dffl = df[maskl]
            
        maski = dffl['iuse'] == iuse
        dffi = dffl[maski]
        
        color = [random.choice(['b', 'g', 'r', 'c', 'm', 'y', 'k']) for _ in range(len(_kx_values[str(vars)]))]      

        for count, i in enumerate(kxs):
            if count == 0:
                ax = dffi.hvplot.points(x='lon',
                                       y='lat',
                                       geo=True, 
                                       color=color, 
                                       tiles=tile,
                                       #responsive=True,
                                       frame_height=600,
                                       frame_width=800,
                                       title=str(vars) + ' | kx = ' + str(kxs) + ' | ' + str(level) + ' hPa | iuse = ' + str(iuse) + ' | loop = ' + str(loop) + ' | valid for ' + str(date))
            else:
               ax *= dffi.hvplot.points(x='lon',
                                       y='lat',
                                       geo=True, 
                                       color=color, 
                                       tiles=tile,
                                       #responsive=True,
                                       frame_height=600,
                                       frame_width=800,
                                       title=str(vars) + ' | kx = ' + str(kxs) + ' | ' + str(level) + ' hPa | iuse = ' + str(iuse) + ' | loop = ' + str(loop) + ' | valid for ' + str(date))
    except:
        ax = monitor_app_texts.warnings_rdiag(lfname + ' (plotPtmapMulti)')
    return pn.Column(ax) 
    
@pn.depends(varn, kxn, by_level, date, loop)
def plotPcount(varn, kxn, by_level, date, loop):
    try:
        lfname = str(varn) + '-diag_conv_' + str(loop) + '_' + str(date)
        obsInfo = loadData(lfname, loop)
        if by_level:
            df = obsInfo.loc[kxn].groupby('press').size()
            ax = df.hvplot.bar(x='press',
                               grid=True, 
                               rot=45,
                               width=1000,
                               height=600,
                               ylabel='Number of Observations',
                               title=str(varn) + '| kx = ' + str(kxn) + ' | loop = ' + str(loop) + ' | valid for ' + str(date))
        else:
            df = obsInfo.groupby(level=0).size()
            ax = df.hvplot.bar(x='kx',
                               grid=True, 
                               rot=45,
                               width=1000,
                               height=600,
                               ylabel='Number of Observations',
                               title=str(varn) + '| all levels | loop = ' + str(loop) + ' | valid for ' + str(date))
    except:
        ax = monitor_app_texts.warnings_rdiag(lfname + ' (plotPcount)')
    return pn.Column(ax)

@pn.depends(varn, kxn, by_level, by_kx, date, loop)
def plotPcount2(varn, kxn, by_level, by_kx, date, loop):
    try:
        lfname = str(varn) + '-diag_conv_' + str(loop) + '_' + str(date)
        #print(lfname)
        obsInfo = loadData(lfname, loop)
        if by_level:
            df = obsInfo.loc[kxn].groupby('press').size()
            #df = obsInfo.groupby(['press', 'kx']).size()
            ax = df.hvplot.bar(stacked=True,
                               legend="top_left",
                               rot=45,
                               #width=1000,
                               height=600,
                               ylabel='Number of Observations',
                               responsive=True,
                               title=str(varn) + ' | kx = ' + str(kxn) + ' | loop = ' + str(loop) + ' | valid for ' + str(date))
        elif by_kx:
            df = obsInfo.drop(kxn).groupby(['press', 'kx']).size()
            ax = df.hvplot.barh(stacked=True,
                               legend="bottom_right",
                               rot=45,
                               #width=1000,
                               height=600,
                               ylabel='Number of Observations',
                               responsive=True,
                               title=str(varn) + ' | loop = ' + str(loop) + ' | valid for ' + str(date))     
            ax.opts(invert_yaxis=True)       
        else:
            df = obsInfo.groupby(level=0).size()
            ax = df.hvplot.bar(x='kx',
                               grid=True, 
                               rot=45,
                               #width=1000,
                               height=600,
                               ylabel='Number of Observations',
                               responsive=True,
                               title=str(varn) + ' | all levels | loop = ' + str(loop) + ' | valid for ' + str(date))
    except:
        ax = monitor_app_texts.warnings_rdiag(lfname + ' (plotPcount2)')
    return pn.Column(ax)

@pn.depends(varn, kxn, by_level, date, loop)
def getTable(varn, kxn, by_level, date, loop):
    try:
        lfname = str(varn) + '-diag_conv_' + str(loop) + '_' + str(date)
        #print(lfname)
        obsInfo = loadData(lfname, loop)
        if by_level:
            ax = obsInfo[varn].head(50)#[varn].loc[kxn]#.loc[kxn].groupby('press')#.size()
            #ax = pn.widgets.Tabulator(df)
        else:
            ax = obsInfo[varn].groupby(level=0)#.size()
            #ax = pn.widgets.Tabulator(df)
    except:
        ax = monitor_app_texts.warnings_rdiag(lfname + ' (getTable)')
    return pn.Column(ax)

def LayoutSidebarRdiag(): 

    card1 = pn.Card(pn.Row(varn, pn.widgets.TooltipIcon(value='Choose a variable', align='start')), 
                    pn.Row(loop, pn.widgets.TooltipIcon(value='Choose a loop', align='start')), 
                    pn.Row(by_level, pn.widgets.TooltipIcon(value='Whether to plot by level', align='start')), 
                    pn.Row(kxn, pn.widgets.TooltipIcon(value='Choose a variable type', align='start')), 
                    pn.Row(by_kx, pn.widgets.TooltipIcon(value='Whether to plot by variable type', align='start')), 
                    title='Number of Observations', collapsed=False)
    #pn.Card(varn, by_level, kxn, title='Table', collapsed=True)
    card2 = pn.Card(pn.Row(vars, pn.widgets.TooltipIcon(value='Choose a variable', align='start')), 
                    pn.Row(loop, pn.widgets.TooltipIcon(value='Choose a loop', align='start')), 
                    pn.Row(tile, pn.widgets.TooltipIcon(value='Choose a tile type', align='start')), 
                    pn.Row(kxs, pn.widgets.TooltipIcon(value='Choose a variable type', align='start')), 
                    pn.Row(level, pn.widgets.TooltipIcon(value='Choose a level', align='start')), 
                    pn.Row(iuse, pn.widgets.TooltipIcon(value='Choose a use flag (1 = used; -1 = not used)', align='start')), 
                    title='Spatial Distribution', collapsed=True)

    # Função para alternar os estados dos cards
    def toggle_cards(event):
        if event.new == False:  # Se um card foi aberto, fecha o outro
            if event.obj is card1:
                card2.collapsed = True
            elif event.obj is card2:
                card1.collapsed = True 

    # Monitorando mudanças no estado `collapsed`
    card1.param.watch(toggle_cards, 'collapsed')
    card2.param.watch(toggle_cards, 'collapsed')

    global cards_rdiag
    cards_rdiag = [card1, card2]

    card_parameters = pn.Card(pn.Row(date, pn.widgets.TooltipIcon(value='Choose a date', align='start')), card1, card2, title='Parameters', collapsed=False)

    return pn.Column(card_parameters)

def LayoutMainRdiag():
    main_text = pn.Column("""
    # Analysis Diagnostics

    Set the parameters on the left to update the map below and explore our analysis features.
    """)

    tabs_rdiag = pn.Tabs(('NUMBER OF OBSERVATIONS', pn.Column('Number of Observations for a variable by level and type (kx).', plotPcount2)), 
                                        #('Table', pn.Column('Table.', getTable)),
                                        ('SPATIAL DISTRIBUTION', pn.Column('Spatial distribution of observations by level and type (kx).', plotPtmapMulti)), dynamic=True)

    # Função para abrir o card correspondente e fechar os outros
    def on_tab_change(event):
        index = event.new  # Obtém o índice da aba selecionada
        for i, card in enumerate(cards_rdiag):
            card.collapsed = i != index  # Abre o card correspondente e fecha os outros

    # Monitorando mudanças na aba selecionada
    tabs_rdiag.param.watch(on_tab_change, "active")

    return pn.Column(main_text, tabs_rdiag,  monitor_warning_bottom_main, sizing_mode="stretch_both")
