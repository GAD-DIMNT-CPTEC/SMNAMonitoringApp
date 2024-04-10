#!/usr/bin/env python
# coding: utf-8

import os
import xarray as xr
import hvplot.xarray
import hvplot.pandas
import pandas as pd
import panel as pn
import intake
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import geoviews as gv
import geopandas as gpd
import holoviews as hvs
from datetime import datetime
from holoviews.operation.datashader import rasterize

from monitor_texts import MonitoringAppTexts
from monitor_dates import MonitoringAppDates

gv.extension("bokeh")

monitor_app_texts = MonitoringAppTexts()

catalog_anl = intake.open_catalog('http://ftp1.cptec.inpe.br/pesquisa/das/carlos.bastarz/SMNAMonitoringApp/anls/catalog_anl.yml')
catalog_bkg = intake.open_catalog('http://ftp1.cptec.inpe.br/pesquisa/das/carlos.bastarz/SMNAMonitoringApp/anls/catalog_bkg.yml')

variable_list = [
'VIRTUAL TEMPERATURE',
'TOPOGRAPHY',                           
'LAND SEA ICE MASK',                    
'LN SURFACE PRESSURE',                  
'DIVERGENCE',                           
'VORTICITY',                            
'SPECIFIC HUMIDITY',                  
'ROUGHNESS LENGTH',                     
'SURFACE TEMPERATURE',                  
'DEEP SOIL TEMPERATURE',                
'STORAGE ON CANOPY',                    
'STORAGE ON GROUND',                    
'SOIL WETNESS OF SURFACE',              
'SOIL WETNESS OF ROOT ZONE',            
'SOIL WETNESS OF DRAINAGE ZONE',        
'TEMPERATURE AT 2-M FROM SURFACE',      
'SPECIFIC HUMIDITY AT 2-M FROM SURFACE',
'ZONAL WIND AT 10-M FROM SURFACE',      
'MERID WIND AT 10-M FROM SURFACE',      
'MASK VEGETATION',                      
'MASK SOIL TEXTURE CLASSES',            
'PARTIAL OXYGEN DENSITY',               
'SURFACE SOIL TEMPERATURE',             
'VEGETATION COVER',                     
'SNOW DEPTH',                           
'LIQ MIXING RATIO PROGNOSTIC',          
'ICE MIXING RATIO PROGNOSTIC',          
'CLOUD TOTAL PROGNOSTIC',               
        ]        

vars3d = ['DIVERGENCE', 'VORTICITY', 'SPECIFIC HUMIDITY', 'VIRTUAL TEMPERATURE', 'LIQ MIXING RATIO PROGNOSTIC', 'ICE MIXING RATIO PROGNOSTIC', 'CLOUD TOTAL PROGNOSTIC']               

variable = pn.widgets.Select(name='Variable', value=variable_list[0], options=variable_list)

vcoord_levels = [1.0000000e+03, 9.9467389e+02, 9.8864404e+02, 9.8182812e+02,
       9.7413733e+02, 9.6547662e+02, 9.5574554e+02, 9.4483936e+02,
       9.3265070e+02, 9.1907172e+02, 9.0399707e+02, 8.8732709e+02,
       8.6897253e+02, 8.4885895e+02, 8.2693237e+02, 8.0316449e+02,
       7.7755896e+02, 7.5015576e+02, 7.2103583e+02, 6.9032397e+02,
       6.5818927e+02, 6.2484418e+02, 5.9053998e+02, 5.5556073e+02,
       5.2021417e+02, 4.8482129e+02, 4.4970471e+02, 4.1517715e+02,
       3.8153036e+02, 3.4902579e+02, 3.1788751e+02, 2.8829736e+02,
       2.6039276e+02, 2.3426695e+02, 2.0997141e+02, 1.8751950e+02,
       1.6689160e+02, 1.4804048e+02, 1.3089703e+02, 1.1537564e+02,
       1.0137925e+02, 8.8803711e+01, 7.7541557e+01, 6.7485062e+01,
       5.8528511e+01, 5.0570110e+01, 4.3513206e+01, 3.7267128e+01,
       3.1747662e+01, 2.6877260e+01, 2.2585030e+01, 1.8806541e+01,
       1.5483560e+01, 1.2563700e+01, 1.0000000e+01, 7.7563500e+00,
       5.8265901e+00, 4.2146201e+00, 2.9185901e+00, 1.9237399e+00,
       1.1999500e+00, 7.0422000e-01, 3.8661000e-01, 1.9740000e-01]

level = pn.widgets.Select(name='Level', value=vcoord_levels[0], options=vcoord_levels)

monitoring_app_dates = MonitoringAppDates()
sdate = monitoring_app_dates.getDates()[0].strip()
edate = monitoring_app_dates.getDates()[1].strip()

start_date = datetime(int(sdate[0:4]), int(sdate[4:6]), int(sdate[6:8]), int(sdate[8:10]))
end_date = datetime(int(edate[0:4]), int(edate[4:6]), int(edate[6:8]), int(edate[8:10]))
date_range = [d.strftime('%Y%m%d%H') for d in pd.date_range(start_date, end_date, freq='6h')][::-1]
date = pn.widgets.Select(name='Date', value=date_range[0], options=date_range)

colormaps = ['nipy_spectral',  'Blues',  'BrBG',  'BuGn',  'BuPu',  'CMRmap',  'Dark2',  'GnBu', 
             'Greens',  'Greys',  'OrRd',  'Oranges',  'PRGn',  'Paired',  'Pastel1', 
             'Pastel2',  'PiYG',  'PuBu', 'PuBuGn',   'PuOr',  'PuRd',  'Purples', 
             'RdBu',  'RdGy',  'RdPu',  'RdYlBu',  'RdYlGn',  'Reds',  'Set1', 
             'Set2',  'Set3',  'Spectral',  'Wistia',  'YlGn', 'YlGnBu',   'YlOrBr', 
             'YlOrRd',  'afmhot',  'autumn',  'binary',  'bone',  'brg',  'bwr', 
             'cividis',  'cool', 
             'Accent',  'copper',  'crest',  'cubehelix',  'flag',  'flare',  
             'gist_earth',  'gist_gray',  'gist_heat',  'gist_ncar',   
             'gist_stern',  'gist_yarg',  'gnuplot', 'gnuplot2',   'gray',  'hot',  'hsv', 
             'icefire',  'inferno',  'jet',  'magma',  'mako',  'coolwarm',  
             'ocean',  'pink',  'plasma',  'prism',  'rainbow',  'rocket',  'seismic', 
             'spring',  'summer',  'tab10',  'tab20',  'tab20b',  'tab20c',  'terrain',  
             'turbo',  'twilight',  'twilight_shifted',  'viridis',  'vlag',  'winter']

colormap = pn.widgets.Select(name='Colormap', value=colormaps[0], options=colormaps)      
invert_colors = pn.widgets.Checkbox(name='Invert Colors', value=False) 

showdiff = pn.widgets.Checkbox(name='Analysis Minus Background', value=False)

showbkg = pn.widgets.Checkbox(name='Show Background', value=False)

stack_plots = pn.widgets.Checkbox(name='Stack Plots', value=False) 

@pn.cache
def loadData(lfname, variable, level, vars3d):
    canl = catalog_anl[lfname].to_dask()
    cbkg = catalog_bkg[lfname].to_dask()
    if variable in vars3d:
        cdiff = (canl[variable].sel(lev=level) - cbkg[variable].sel(lev=level))
    else:
        print(lfname, variable, level, vars3d)
        cdiff = (canl[variable] - cbkg[variable])
    return canl, cbkg, cdiff

@pn.depends(variable, level, date, colormap, invert_colors, showdiff, stack_plots, showbkg)
def plotFields(variable, level, date, colormap, invert_colors, showdiff, stack_plots, showbkg):
    lfname = date

    feature_opts_lw = 1 
    features = gv.feature.coastline.options(line_width=feature_opts_lw) * gv.feature.borders.options(line_width=feature_opts_lw)

    try:
        dfs_anl, dfs_bkg, dfs_diff = loadData(lfname, variable, level, vars3d)

        width=840
        height=500
        data_aspect=0.5

        if invert_colors == True:
            cmap = colormap + '_r'
        else:
            cmap = colormap
            
        if variable in vars3d:
            if showdiff:
                tax_diff = rasterize(gv.project(gv.Dataset(dfs_diff.compute()).to(gv.Image, ['lon', 'lat'])))
                tax_diff.opts(
                    projection=ccrs.PlateCarree(),
                    cmap=cmap,
                    tools=["hover"],
                    colorbar=True,
                    symmetric=False,
                    responsive=True,
                    title="Analysis Minus Background of " + str(variable) + " @ level " + str(level) + " (valid for " + str(date) + ")",
                    height=700,
                )
                ax = tax_diff * features
            else:
                cmin = float(dfs_anl[variable].sel(lev=level).min().values)
                cmax = float(dfs_anl[variable].sel(lev=level).max().values)

                if showbkg:
                    height=height
                else:
                    height=700

                tax_anl = rasterize(gv.project(gv.Dataset(dfs_anl[variable].sel(lev=level).compute()).to(gv.Image, ['lon', 'lat'])))
                tax_anl.opts(
                    projection=ccrs.PlateCarree(),
                    cmap=cmap,
                    tools=["hover"],
                    colorbar=True,
                    symmetric=False,
                    responsive=True,
                    title="Analysis of " + str(variable) + " @ level " + str(level) + " (valid for " + str(date) + ")",
                    height=height,
                )
                tax_anl.opts(clim=(cmin,cmax))
                ax_anl = tax_anl * features
                
                tax_bkg = rasterize(gv.project(gv.Dataset(dfs_bkg[variable].sel(lev=level).compute()).to(gv.Image, ['lon', 'lat'])))
                tax_bkg.opts(
                    projection=ccrs.PlateCarree(),
                    cmap=cmap,
                    tools=["hover"],
                    colorbar=True,
                    symmetric=False,
                    responsive=True,
                    title="Background of " + str(variable) + " @ level " + str(level) + " (valid for " + str(date) + ")",
                    height=height,
                )
                tax_bkg.opts(clim=(cmin,cmax))
                ax_bkg = tax_bkg * features

                if showbkg:
                    if stack_plots:
                        ax = hvs.Layout(ax_anl + ax_bkg).cols(1)
                    else:
                        ax = hvs.Layout(ax_anl + ax_bkg).cols(2)
                else:
                    ax = ax_anl
        else:
            if showdiff:
                tax_diff = rasterize(gv.project(gv.Dataset(dfs_diff.compute()).to(gv.Image, ['lon', 'lat'])))
                tax_diff.opts(
                    projection=ccrs.PlateCarree(),
                    cmap=cmap,
                    tools=["hover"],
                    colorbar=True,
                    symmetric=False,
                    responsive=True,
                    title="Analysis Minus Background of " + str(variable) + " (valid for " + str(date) + ")",
                    height=height,
                )
                ax = tax * features
            else:
                cmin = float(dfs_anl[variable].min().values)
                cmax = float(dfs_anl[variable].max().values)

                if showbkg:
                    height=height
                else:
                    height=700

                tax_anl = rasterize(gv.project(gv.Dataset(dfs_anl[variable].compute()).to(gv.Image, ['lon', 'lat'])))
                tax_anl.opts(
                    projection=ccrs.PlateCarree(),
                    cmap=cmap,
                    tools=["hover"],
                    colorbar=True,
                    symmetric=False,
                    responsive=True,
                    title="Analysis of " + str(variable) + " (valid for " + str(date) + ")",
                    height=height,
                )
                tax_anl.opts(clim=(cmin,cmax))
                ax_anl = tax_anl * features
    
                tax_bkg = rasterize(gv.project(gv.Dataset(dfs_bkg[variable].compute()).to(gv.Image, ['lon', 'lat'])))
                tax_bkg.opts(
                    projection=ccrs.PlateCarree(),
                    cmap=cmap,
                    tools=["hover"],
                    colorbar=True,
                    symmetric=False,
                    responsive=True,
                    title="Background of " + str(variable) + " (valid for " + str(date) + ")",
                    height=height,
                )
                tax_bkg.opts(clim=(cmin,cmax))
                ax_bkg = tax_bkg * features
                
                if showbkg:
                    if stack_plots:
                        ax = hvs.Layout(ax_anl + ax_bkg).cols(1)
                    else:
                        ax = hvs.Layout(ax_anl + ax_bkg).cols(2)
                else:
                    ax = ax_anl
    except:
        ax = monitor_app_texts.warnings_anl(lfname + ' (plotFields)')
    return pn.Column(ax, sizing_mode='stretch_both')

def LayoutSidebarAnl():
    card_parameters = pn.Card(date, variable, level, showbkg, showdiff, colormap, invert_colors, stack_plots, title='Parameters', collapsed=False)
    return pn.Column(card_parameters)

def LayoutMainAnl():
    main_text = pn.Column("""
    # Analysis Plots

    Set the parameters on the left to update the map below and explore our analysis features.
    """)
    #return pn.Column(main_text, pn.Spacer(height=50), plotFields, sizing_mode="stretch_both")
    return pn.Column(main_text, plotFields, sizing_mode="stretch_both")
