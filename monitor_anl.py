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
import requests

from datetime import datetime
from holoviews.operation.datashader import rasterize

from monitor_texts import MonitoringAppTexts
from monitor_dates import MonitoringAppDates

import dask
dask.config.set(scheduler='threads')

gv.extension("bokeh")

monitor_app_texts = MonitoringAppTexts()
monitor_warning_bottom_main = monitor_app_texts.warnings()

# Função para testar se a URL dos catálogos existe antes de tentar acessá-los
# - Se os dois catálogos existirem, monta o resto da dashborad desta aba
# - Se ambos não existirem, mostra uma mensagem de erro na interface
def url_exists(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        # códigos 200-399 indicam que a URL está acessível
        if response.status_code < 400:
            print(f"✅ [ANALYSIS PLOTS] Arquivo acessível: {url}")
            catalog_obj = intake.open_catalog(url)
            return True, catalog_obj
        else:
            print(f"❌ [ANALYSIS PLOTS] Arquivo não encontrado: {url} (status {response.status_code})")
            return False, None
    except requests.RequestException:
        return False, None

catalog_anl_file = 'https://dataserver.cptec.inpe.br/dataserver_dimnt/das/carlos.bastarz/SMNAMonitoringApp/anls/catalog_anl.yml'
catalog_bkg_file = 'https://dataserver.cptec.inpe.br/dataserver_dimnt/das/carlos.bastarz/SMNAMonitoringApp/anls/catalog_bkg.yml'

anl_exists = url_exists(catalog_anl_file)
bkg_exists = url_exists(catalog_bkg_file)

if anl_exists[0] and bkg_exists[0]:

    catalog_anl = url_exists(catalog_anl_file)[1]
    catalog_bkg = url_exists(catalog_bkg_file)[1]

    tmp = catalog_anl[list(catalog_anl.keys())[0]]
    tmp1 = tmp.to_dask()
    variable_list = list(tmp1.data_vars)

    vars3d = [var for var in tmp1.data_vars if tmp1[var].ndim == 3]

    variable = pn.widgets.Select(name='Variable', value=variable_list[2], options=variable_list, width=240)

    vcoord_levels = list(tmp1.lev.values)

    level = pn.widgets.Select(name='Level', value=vcoord_levels[0], options=vcoord_levels, width=240)

    monitoring_app_dates = MonitoringAppDates()
    sdate = monitoring_app_dates.getDates()[0].strip()
    edate = monitoring_app_dates.getDates()[1].strip()

    start_date = datetime(int(sdate[0:4]), int(sdate[4:6]), int(sdate[6:8]), int(sdate[8:10]))
    end_date = datetime(int(edate[0:4]), int(edate[4:6]), int(edate[6:8]), int(edate[8:10]))
    date_range = [d.strftime('%Y%m%d%H') for d in pd.date_range(start_date, end_date, freq='6h')][::-1]
    date = pn.widgets.Select(name='Date', value=date_range[0], options=date_range, width=240)

    colormap = pn.widgets.ColorMap(name='Colormap', options=cc.palette_n, value_name='coolwarm', width=260, margin=(0, 0, 0, 0))
    invert_colors = pn.widgets.Checkbox(name='Invert Colors', value=False, width=240)

    showbkg = pn.widgets.Checkbox(name='Show Background', value=False, width=240)
    stack_plots = pn.widgets.Checkbox(name='Stack Plots', value=False, disabled=True, width=240)
    showdiff = pn.widgets.Checkbox(name='Analysis Minus Background', value=False, disabled=True, width=240)

    @pn.cache
    def loadData(lfname, variable, level, vars3d):
        canl = catalog_anl[lfname].to_dask()
        cbkg = catalog_bkg[lfname].to_dask()
        if variable in vars3d:
            cdiff = (canl[variable].sel(lev=level) - cbkg[variable].sel(lev=level))
        else:
            cdiff = (canl[variable] - cbkg[variable])
        return canl, cbkg, cdiff

    def option_state_update(event):
        showdiff.disabled = not event.new
        stack_plots.disabled = not event.new

    showbkg.param.watch(option_state_update, 'value')

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
                cmap = colormap[::-1]
            else:
                cmap = colormap

            if variable in vars3d:
                if showdiff:
                    tax_diff = rasterize(gv.project(gv.Dataset(dfs_diff).to(gv.QuadMesh, ['lon', 'lat'])))
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

                    data_anl = dfs_anl[variable].sel(lev=level)
                    tax_anl = rasterize(gv.project(gv.Dataset(data_anl).to(gv.QuadMesh, ['lon', 'lat'])))
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

                    data_bkg = dfs_bkg[variable].sel(lev=level)
                    tax_bkg = rasterize(gv.project(gv.Dataset(data_bkg).to(gv.QuadMesh, ['lon', 'lat'])))
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
                    tax_diff = rasterize(gv.project(gv.Dataset(dfs_diff).to(gv.QuadMesh, ['lon', 'lat'])))
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

                    data_anl = dfs_anl[variable].sel(lev=level)
                    tax_anl = rasterize(gv.project(gv.Dataset(data_anl).to(gv.QuadMesh, ['lon', 'lat'])))
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

                    data_bkg = dfs_bkg[variable].sel(lev=level)
                    tax_bkg = rasterize(gv.project(gv.Dataset(data_bkg).to(gv.QuadMesh, ['lon', 'lat'])))
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
        return pn.Column(main_text, plotFields, monitor_warning_bottom_main, sizing_mode="stretch_both")

else:

    def LayoutSidebarAnl():
        main_text = pn.Column("""
        # Analysis Plots

        Set the parameters on the left to update the map below and explore our analysis features.
        """)
        return pn.Column(main_text, sizing_mode="stretch_both")

    def LayoutMainAnl():
        main_text = pn.Column("""
        # Analysis Plots

        Set the parameters on the left to update the map below and explore our analysis features.
        """)
        return pn.Column(main_text, sizing_mode="stretch_both")
