#!/usr/bin/env python
# coding: utf-8

import os
import intake
import hvplot.pandas
import pandas as pd
import panel as pn

from datetime import datetime

from monitor_texts import MonitoringAppTexts
from monitor_dates import MonitoringAppDates

pn.extension()

monitor_app_texts = MonitoringAppTexts()

catalog_diag_conv_01 = intake.open_catalog('http://ftp1.cptec.inpe.br/pesquisa/das/carlos.bastarz/GSIMonitor/rdiag/catalog_diag_conv_01.yml')
catalog_diag_conv_03 = intake.open_catalog('http://ftp1.cptec.inpe.br/pesquisa/das/carlos.bastarz/GSIMonitor/rdiag/catalog_diag_conv_03.yml')

monitoring_app_dates = MonitoringAppDates()
sdate = monitoring_app_dates.getDates()[0].strip()
edate = monitoring_app_dates.getDates()[1].strip()

start_date = datetime(int(sdate[0:4]), int(sdate[4:6]), int(sdate[6:8]), int(sdate[8:10]))
end_date = datetime(int(edate[0:4]), int(edate[4:6]), int(edate[6:8]), int(edate[8:10]))
date_range = [d.strftime('%Y%m%d%H') for d in pd.date_range(start_date, end_date, freq='6h')][::-1]
date = pn.widgets.Select(name='Date', value=date_range[0], options=date_range)

# From the catalogs, assemble a dictionary with all the kx values:
variable_list = ['q', 'ps', 't', 'uv']
zlevs = [1000.0, 900.0, 800.0, 700.0, 600.0, 500.0, 400.0, 300.0, 250.0, 200.0, 150.0, 100.0, 50.0, 0.0]

#_kx_values = {}
#for var in variable_list:
#    source_name = str(var) + '_diag_conv_01_' + str(sdate)
#    gdf_tmp = catalog_diag_conv_01[source_name].read()
#    _kx_values[str(var)] = gdf_tmp.index.get_level_values('kx').unique().to_list()
#
#_kx_valuesm = _kx_values.copy()

_kx_values = {'q':  [181, 120, 187, 180, 183],
              'ps': [181, 180, 120, 187, 183],
              't':  [181, 180, 120, 187, 183, 130, 126],
              'uv': [257,  258,  281,  280,  253,  243,  254,  220,  287,  221,  284,  230,  244,  259,  252,  242,  250,  210,  229,  224,  282]}

_kx_valuesn = _kx_values.copy()
_kx_valuess = _kx_values.copy()

varn = pn.widgets.Select(name='Variable', value=variable_list[0], options=variable_list)
kxn = pn.widgets.MultiChoice(name='kx', value=_kx_values[varn.value], options=_kx_values[varn.value], solid=False)

@pn.depends(varn.param.value, watch=True)
def _update_kx_valuesn(select_varn):
    kx_valuesn = _kx_valuesn[select_varn]
    kxn.options = kx_valuesn
    kxn.value = kx_valuesn

vars = pn.widgets.Select(name='Variable', value=variable_list[0], options=variable_list)
kxs = pn.widgets.MultiChoice(name='kx', value=_kx_values[vars.value], options=_kx_values[vars.value], solid=False)

@pn.depends(vars.param.value, watch=True)
def _update_kx_valuess(select_vars):
    kx_valuess = _kx_valuess[select_vars]
    kxs.options = kx_valuess
    kxs.value = kx_valuess

level = pn.widgets.Select(name='Level', value=zlevs[0], options=zlevs)
iuse = pn.widgets.Select(name='iuse', value=1, options=[-1, 1])

by_level = pn.widgets.Toggle(name='by Level', value=False, button_type='success')
by_kx = pn.widgets.Toggle(name='by kx', value=False, button_type='success')

@pn.cache
def loadData(lfname):
    try:
        ax = catalog_diag_conv_01[lfname].read()
    except:
        ax = monitor_app_texts.warnings_rdiag(lfname + ' (loadData)')
    return ax

@pn.depends(vars, kxs, level, iuse, date)
def plotPtmap(vars, kxs, level, iuse, date):
    try:
        lfname = str(vars) + '_diag_conv_01_' + str(sdate)
        obsInfo = loadData(lfname)
        df = obsInfo

        maskl = df['press'] == level
        dffl = df[maskl]

        maski = dffl['iuse'] == iuse
        dffi = dffl[maski]

        instr = getVarInfo(kxs, vars, 'instrument')
        label = '\n'.join(wrap(vars + '-' + str(kxs) + ' | ' + instr,30))

        ax = dffi.hvplot(global_extent=True,
                         grid=True,
                         tiles=True,
                         title=label,
                         frame_height=750)
    except:
        ax = monitor_app_texts.warnings_rdiag(lfname + ' (plotPtmap)')
    return pn.Column(ax) 

@pn.depends(vars, kxs, level, iuse, date)
def plotPtmapMulti(vars, kxs, level, iuse, date):
    try:
        lfname = str(vars) + '_diag_conv_01_' + str(sdate)
        obsInfo = loadData(lfname)
        df = obsInfo.loc[kxs]

        maskl = df['press'] == level
        dffl = df[maskl]
            
        maski = dffl['iuse'] == iuse
        dffi = dffl[maski]

        ax = dffi.hvplot(global_extent=True,
                         grid=True,
                         tiles=True,
                         title=str(vars) + ', kx = ' + str(kxs) + ' @ ' + str(level) + ' hPa | iuse = ' + str(iuse) + ' , valid for ' + str(date),
                         frame_height=700)
                         #frame_width=1000)
                         #data_aspect=0.8)
    except:
        ax = monitor_app_texts.warnings_rdiag(lfname + ' (plotPtmapMulti)')
    return pn.Column(ax) 
    
@pn.depends(varn, kxn, by_level, date)
def plotPcount(varn, kxn, by_level, date):
    try:
        lfname = str(varn) + '_diag_conv_01_' + str(sdate)
        obsInfo = loadData(lfname)
        if by_level:
            df = obsInfo.loc[kxn].groupby('press').size()
            ax = df.hvplot.bar(x='press',
                               grid=True, 
                               rot=45,
                               width=1000,
                               height=600,
                               ylabel='Number of Observations',
                               title='1' + str(varn) + ', kx = ' + str(kxn) + ', valid for ' + str(date))
        else:
            df = obsInfo.groupby(level=0).size()
            ax = df.hvplot.bar(x='kx',
                               grid=True, 
                               rot=45,
                               width=1000,
                               height=600,
                               ylabel='Number of Observations',
                               title='3' + str(varn) + ', all levels, valid for ' + str(date))
    except:
        ax = monitor_app_texts.warnings_rdiag(lfname + ' (plotPcount)')
    return pn.Column(ax)

@pn.depends(varn, kxn, by_level, by_kx, date)
def plotPcount2(varn, kxn, by_level, by_kx, date):
    try:
        lfname = str(varn) + '_diag_conv_01_' + str(sdate)
        obsInfo = loadData(lfname)
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
                               title=str(varn) + ', kx = ' + str(kxn) + ', valid for ' + str(date))
        elif by_kx:
            df = obsInfo.drop(kxn).groupby(['press', 'kx']).size()
            ax = df.hvplot.barh(stacked=True,
                               legend="bottom_right",
                               rot=45,
                               #width=1000,
                               height=600,
                               ylabel='Number of Observations',
                               responsive=True,
                               title=str(varn) + ', valid for ' + str(date))     
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
                               title=str(varn) + ', all levels, valid for ' + str(date))
    except:
        ax = monitor_app_texts.warnings_rdiag(lfname + ' (plotPcount2)')
    return pn.Column(ax)

@pn.depends(varn, kxn, by_level, date)
def getTable(varn, kxn, by_level, date):
    try:
        lfname = str(varn) + '_diag_conv_01_' + str(sdate)
        obsInfo = loadData(lfname)
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
    card_parameters = pn.Card(date,
                              pn.Card(varn, by_level, kxn, by_kx, title='Number of Observations', collapsed=False),
                              #pn.Card(varn, by_level, kxn, title='Table', collapsed=True),
                              pn.Card(vars, kxs, level, iuse, title='Spatial Distribution', collapsed=True),
                              title='Parameters', collapsed=False)

    return pn.Column(card_parameters)

def LayoutMainRdiag():
    main_text = pn.Column("""
    # Analysis Diagnostics

    Set the parameters on the left to update the map below and explore our analysis features.
    """)
    return pn.Column(main_text, pn.Tabs(('NUMBER OF OBSERVATIONS', pn.Column('Number of Observations for a variable by level and type (kx).', plotPcount2)), 
                                        #('Table', pn.Column('Table.', getTable)),
                                        ('SPATIAL DISTRIBUTION', pn.Column('Spatial distribution of observations by level and type (kx).', plotPtmapMulti)), dynamic=True), 
                                        sizing_mode="stretch_both")