#!/usr/bin/env python
# coding: utf-8

import os
import colorcet as cc
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

#from bokeh.models import Tooltip
from datetime import datetime
from holoviews.operation.datashader import rasterize

from monitor_texts import MonitoringAppTexts
from monitor_dates import MonitoringAppDates

gv.extension("bokeh")

monitor_app_texts = MonitoringAppTexts()
monitor_warning_bottom_main = monitor_app_texts.warnings()

#catalog_anl = intake.open_catalog('http://ftp1.cptec.inpe.br/pesquisa/das/carlos.bastarz/SMNAMonitoringApp/anls/catalog_anl.yml')
#catalog_bkg = intake.open_catalog('http://ftp1.cptec.inpe.br/pesquisa/das/carlos.bastarz/SMNAMonitoringApp/anls/catalog_bkg.yml')
catalog_anl = intake.open_catalog('/extra2/SMNAMonitoringApp_DATA/anls/catalog_anl.yml')
catalog_bkg = intake.open_catalog('/extra2/SMNAMonitoringApp_DATA/anls/catalog_bkg.yml')

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

variable = pn.widgets.Select(name='Variable', value=variable_list[0], options=variable_list, width=240)

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

level = pn.widgets.Select(name='Level', value=vcoord_levels[0], options=vcoord_levels, width=240)

monitoring_app_dates = MonitoringAppDates()
sdate = monitoring_app_dates.getDates()[0].strip()
edate = monitoring_app_dates.getDates()[1].strip()

start_date = datetime(int(sdate[0:4]), int(sdate[4:6]), int(sdate[6:8]), int(sdate[8:10]))
end_date = datetime(int(edate[0:4]), int(edate[4:6]), int(edate[6:8]), int(edate[8:10]))
date_range = [d.strftime('%Y%m%d%H') for d in pd.date_range(start_date, end_date, freq='6h')][::-1]
date = pn.widgets.Select(name='Date', value=date_range[3], options=date_range, width=240)
#date_tt = pn.widgets.TooltipIcon(value='This is a simple tooltip by using a string', styles={'margin-top': '20px'})
   
colormap = pn.widgets.ColorMap(name='Colormap', options=cc.palette_n, value_name='coolwarm', width=260, margin=(0, 0, 0, 0))
invert_colors = pn.widgets.Checkbox(name='Invert Colors', value=False, width=240) 

showbkg = pn.widgets.Checkbox(name='Show Background', value=False, width=240)
stack_plots = pn.widgets.Checkbox(name='Stack Plots', value=False, width=240) 
showdiff = pn.widgets.Checkbox(name='Analysis Minus Background', value=False, width=240)

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

    #if showbkg:
    #    showdiff.disabled = False
    #    stack_plots.disabled = False
    #else:
    #    showdiff.disabled = True
    #    stack_plots.disabled = True   

    try:
        dfs_anl, dfs_bkg, dfs_diff = loadData(lfname, variable, level, vars3d)

        width=840
        height=500
        data_aspect=0.5

        if invert_colors == True:
            cmap = colormap[::-1]
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
                    #showdiff.disabled = False
                    #stack_plots.disabled = False
                else:
                    height=700
                    #showdiff.disabled = True
                    #stack_plots.disabled = True

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
                    #showdiff.disabled = False
                    #stack_plots.disabled = False
                    if stack_plots:
                        ax = hvs.Layout(ax_anl + ax_bkg).cols(1)
                    else:
                        ax = hvs.Layout(ax_anl + ax_bkg).cols(2)
                else:
                    #showdiff.disabled = True
                    #stack_plots.disabled = True
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
                    #showdiff.disabled = False
                    #stack_plots.disabled = False                    
                    height=height
                else:
                    #showdiff.disabled = True
                    #stack_plots.disabled = True                    
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
                    #showdiff.disabled = False
                    #stack_plots.disabled = False                    
                    if stack_plots:
                        ax = hvs.Layout(ax_anl + ax_bkg).cols(1)
                    else:
                        ax = hvs.Layout(ax_anl + ax_bkg).cols(2)
                else:
                    #showdiff.disabled = True
                    #stack_plots.disabled = True                    
                    ax = ax_anl
    except:
        ax = monitor_app_texts.warnings_anl(lfname + ' (plotFields)')
    return pn.Column(ax, sizing_mode='stretch_both')

def LayoutSidebarAnl():
    card_parameters = pn.Card(pn.Row(date, pn.widgets.TooltipIcon(value='Choose a date', align='start')), 
                              pn.Row(variable, pn.widgets.TooltipIcon(value='Choose a variable', align='start')),
                              pn.Row(level, pn.widgets.TooltipIcon(value='Choose a level', align='start')),
                              pn.Row(showbkg, pn.widgets.TooltipIcon(value='Whether to show the background', align='start')),
                              pn.Row(stack_plots, pn.widgets.TooltipIcon(value='Whether to stack the plots', align='start')),
                              pn.Row(showdiff, pn.widgets.TooltipIcon(value='Plot the difference between the analysis and background field', align='start')),
                              pn.Row(colormap, pn.widgets.TooltipIcon(value='Change the colormap', align='start')),
                              pn.Row(invert_colors, pn.widgets.TooltipIcon(value='Invert the color range in the colormap', align='start')),
                              title='Parameters', collapsed=False)
    return pn.Column(card_parameters)

def LayoutMainAnl():
    main_text = pn.Column("""
    # Analysis Plots

    Set the parameters on the left to update the map below and explore our analysis features.
    """)
    #return pn.Column(main_text, pn.Spacer(height=50), plotFields, sizing_mode="stretch_both")
    return pn.Column(main_text, plotFields, monitor_warning_bottom_main, sizing_mode="stretch_both")
