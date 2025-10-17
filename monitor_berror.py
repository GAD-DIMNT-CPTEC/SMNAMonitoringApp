#!/usr/bin/env python
# coding: utf-8

import os
import requests
import colorcet as cc
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import panel as pn
import hvplot.xarray
import numpy as np
import intake
import geopandas as gpd
import geoviews as gv

from monitor_texts import MonitoringAppTexts

pn.extension(sizing_mode="stretch_width")

monitor_app_texts = MonitoringAppTexts()
monitor_warning_bottom_main = monitor_app_texts.warnings()

def url_exists(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        # códigos 200-399 indicam que a URL está acessível
        if response.status_code < 400:
            print(f"✅ [B ERROR COVARIANCE] Arquivo acessível: {url}")
            catalog_obj = intake.open_catalog(url)
            return True, catalog_obj
        else:
            print(f"❌ [B ERROR COVARIANCE] Arquivo não encontrado: {url} (status {response.status_code})")
            return False, None
    except requests.RequestException:
        return False, None

catalog_berror_file = 'https://dataserver.cptec.inpe.br/dataserver_dimnt/das/carlos.bastarz/SMNAMonitoringApp/berror/catalog_berror.yml'

berror_exists = url_exists(catalog_berror_file)

if berror_exists[0]:

    catalog_berror = url_exists(catalog_berror_file)[1]

    level_lst = np.arange(0,64, 1).tolist()
    level = pn.widgets.IntSlider(name='Level', value=0, start=level_lst[0], step=1, end=level_lst[-1], width=230)

    balproj_lst = ['agvin', 'bgvin', 'wgvin']
    balproj = pn.widgets.Select(name='Balance Projection Matrix', value=balproj_lst[0], options=balproj_lst, width=230)

    stdevvars_lst = ['sf', 'vp', 't', 'q', 'qin', 'oz', 'ps', 'cw', 'sst']
    stdevvars = pn.widgets.Select(name='Standard Deviation', value=stdevvars_lst[0], options=stdevvars_lst, width=230)

    show_profile = pn.widgets.Checkbox(name='Profile', value=False, width=230)

    hscalevars_lst = ['sf', 'vp', 't', 'q', 'oz', 'cw', 'ps', 'sst']
    hscalevars = pn.widgets.Select(name='Horizontal Length Scale', value=hscalevars_lst[0], options=hscalevars_lst, width=230)

    vscalevars_lst = ['sf', 'vp', 't', 'q', 'oz', 'cw']
    vscalevars = pn.widgets.Select(name='Vertical Length Scale', value=vscalevars_lst[0], options=vscalevars_lst, width=230)


    colormap = pn.widgets.ColorMap(name='Colormap', options=cc.palette_n, value_name='rainbow4', width=255, margin=(0, 0, 0, 0))
    invert_colors = pn.widgets.Checkbox(name='Invert Colors', value=False, width=235)

    vertical_log_bp = pn.widgets.Checkbox(name='Vertical Log', value=False, width=230)
    vertical_log_am = pn.widgets.Checkbox(name='Vertical Log', value=False, width=230)
    vertical_log_hs = pn.widgets.Checkbox(name='Vertical Log', value=False, width=230)
    vertical_log_vs = pn.widgets.Checkbox(name='Vertical Log', value=False, width=230)

    height=400
    height_sst=325

    @pn.depends(balproj, level, vertical_log_bp, colormap, invert_colors)
    def plotBalProjs(balproj, level, vertical_log_bp, colormap, invert_colors):
        if invert_colors == True:
            cmap = colormap[::-1]
        else:
            cmap = colormap

        vname = 'balprojs_' + str(balproj)
        dset = catalog_berror[vname].to_dask()
        if balproj == 'wgvin':
            ax = dset.isel(level=0, latitude=slice(0,-2)).hvplot.line(x='latitude',
                                                                    clabel='No dim.',
                                                                    shared_axes=False,
                                                                    height=height,
                                                                    responsive=True,
                                                                    title='Projection of the Stream Function over the balanced part of Surface Pressure')
        elif balproj == 'bgvin':
            if vertical_log_bp:
                ax = dset.hvplot.image(y='level',
                                        x='latitude',
                                        logy=True,
                                        clabel='No dim.',
                                        #aspect=1,
                                        cmap=cmap,
                                        shared_axes=False,
                                        height=height,
                                        responsive=True,
                                        title='Projection of the Stream Function over the balanced part of Velocity Potential')
            else:
                ax = dset.hvplot.image(y='level',
                                        x='latitude',
                                        logy=False,
                                        clabel='No dim.',
                                        #aspect=1,
                                        cmap=cmap,
                                        shared_axes=False,
                                        height=height,
                                        responsive=True,
                                        title='Projection of the Stream Function over the balanced part of Velocity Potential')
        elif balproj == 'agvin':
            if vertical_log_bp:
                ax = dset.isel(level_2=level).hvplot.image(y='level',
                                                            x='latitude',
                                                            logy=True,
                                                            clabel='No dim.',
                                                            #aspect=1,
                                                            cmap=cmap,
                                                            shared_axes=False,
                                                            height=height,
                                                            responsive=True,
                                                            title='Projection of Stream Function at level ' + str(level) + ' over the vertical \nprofile of the balanced part of Virtual Temperature')
            else:
                ax = dset.isel(level_2=level).hvplot.image(y='level',
                                                            x='latitude',
                                                            logy=False,
                                                            clabel='No dim.',
                                                            #aspect=1,
                                                            cmap=cmap,
                                                            shared_axes=False,
                                                            height=height,
                                                            responsive=True,
                                                            title='Projection of Stream Function at level ' + str(level) + ' over the vertical \nprofile of the balanced part of Virtual Temperature')
        return ax

    @pn.depends(stdevvars, show_profile, vertical_log_am, colormap, invert_colors)
    def plotStDev(stdevvars, show_profile, vertical_log_am, colormap, invert_colors):
        if stdevvars == 'sf':
            vfname = 'Stream Function'
            clabel = 'm2/s'
        elif stdevvars == 'vp':
            vfname = 'Velocity Potential'
            clabel = 'm2/s'
        elif stdevvars == 't':
            vfname = 'Unbalanced part of Temperature'
            clabel = 'K'
        elif stdevvars == 'q':
            vfname = 'Relative Humidity'
            clabel = '%'
        elif stdevvars == 'qin':
            vfname = 'Relative Humidity'
            clabel = '%'
        elif stdevvars == 'oz':
            vfname = 'Ozone'
            clabel = ''
        elif stdevvars == 'cw':
            vfname = 'Liquid Water Content'
            clabel = ''
        elif stdevvars == 'ps':
            vfname = 'Surface Pressure'
            clabel = 'Pa'
        elif stdevvars == 'sst':
            vfname = 'Sea Surface Temperature'
            clabel = 'K'

        if invert_colors == True:
            cmap = colormap[::-1]
        else:
            cmap = colormap

        if vertical_log_am:
            logy=True
        else:
            logy=False

        if stdevvars == 'qin':
            vname = 'amplitudes_' + str(stdevvars)
            dset = catalog_berror[vname].to_dask()*1e2
            if show_profile:
                ax = dset.isel(latitude=slice(0,25)).mean(dim='latitude').hvplot.line(#y='level',
                                                                    #x='latitude',
                                                                    clabel=clabel,
                                                                    #aspect=1,
                                                                    cmap=cmap,
                                                                    shared_axes=False,
                                                                    height=height,
                                                                    invert=True,
                                                                    logy=logy,
                                                                    responsive=True,
                                                                    title='Standard Deviation of ' + str(vfname))
            else:
                ax = dset.isel(latitude=slice(0,25)).hvplot.image(y='level',
                                                                    x='latitude',
                                                                    clabel=clabel,
                                                                    #aspect=1,
                                                                    cmap=cmap,
                                                                    shared_axes=False,
                                                                    height=height,
                                                                    logy=logy,
                                                                    responsive=True,
                                                                    title='Standard Deviation of ' + str(vfname))
        elif stdevvars == 'ps':
            vname = 'amplitudes_' + str(stdevvars)
            dset = catalog_berror[vname].to_dask()
            ax = dset.hvplot.line(x='latitude',
                                clabel=clabel,
                                #aspect=1,
                                cmap=cmap,
                                height=height,
                                responsive=True,
                                title='Standard Deviation of ' + str(vfname))
        elif stdevvars == 'sst':
            vname = 'amplitudes_' + str(stdevvars)
            dset = catalog_berror[vname].to_dask()
            ax_sst = dset.hvplot.image(y='latitude',
                                    x='longitude',
                                    clabel=clabel,
                                    #aspect=1,
                                    cmap=cmap,
                                    shared_axes=False,
                                    height=height_sst,
                                    geo=True,
                                    coastline=True,
                                    responsive=True,
                                    title='Standard Deviation of ' + str(vfname))

            ax = ax_sst * gv.feature.land.options(fill_color='k', line_color='w')
        else:
            vname = 'amplitudes_' + str(stdevvars)
            dset = catalog_berror[vname].to_dask()
            if show_profile:
                ax = dset.mean(dim='latitude').hvplot.line(#y='level',
                                        #x='latitude',
                                        clabel=clabel,
                                        #aspect=1,
                                        cmap=cmap,
                                        shared_axes=False,
                                        height=height,
                                        invert=True,
                                        #show_grid=True,
                                        logy=logy,
                                        responsive=True,
                                        title='Standard Deviation of ' + str(vfname))
            else:
                ax = dset.hvplot.image(y='level',
                                        x='latitude',
                                        clabel=clabel,
                                        #aspect=1,
                                        cmap=cmap,
                                        shared_axes=False,
                                        height=height,
                                        logy=logy,
                                        responsive=True,
                                        title='Standard Deviation of ' + str(vfname))
        return ax

    @pn.depends(hscalevars, vertical_log_hs, colormap, invert_colors)
    def plotHScale(hscalevars, vertical_log_hs, colormap, invert_colors):
        if hscalevars == 'sf':
            vfname = 'Stream Function'
        elif hscalevars == 'vp':
            vfname = 'Velocity Potential'
        elif hscalevars == 't':
            vfname = 'Unbalanced part of Temperature'
        elif hscalevars == 'q':
            vfname = 'Relative Humidity'
        elif hscalevars == 'qin':
            vfname = 'Relative Humidity'
        elif hscalevars == 'oz':
            vfname = 'Ozone'
        elif hscalevars == 'cw':
            vfname = 'Liquid Water Content'
        elif hscalevars == 'ps':
            vfname = 'Surface Pressure'
        elif hscalevars == 'sst':
            vfname = 'Sea Surface Temperature'

        if vertical_log_hs:
            logy=True
        else:
            logy=False

        if invert_colors == True:
            cmap = colormap[::-1]
        else:
            cmap = colormap

        vname = 'hscales_' + str(hscalevars)
        dset = catalog_berror[vname].to_dask()*1e-3

        if hscalevars == 'ps':
            ax = dset.hvplot.line(x='latitude',
                                clabel='Km',
                                #aspect=1,
                                cmap=cmap,
                                shared_axes=False,
                                height=height,
                                responsive=True,
                                title='Horizontal Length Scale of ' + str(vfname))
        elif hscalevars == 'sst':
            ax_sst = dset.hvplot.image(y='latitude',
                                    x='longitude',
                                    clabel='Km',
                                    #aspect=1,
                                    cmap=cmap,
                                    shared_axes=False,
                                    height=height_sst,
                                    geo=True,
                                    coastline=True,
                                    responsive=True,
                                    title='Horizontal Length Scale of ' + str(vfname))

            ax = ax_sst * gv.feature.land.options(fill_color='k', line_color='w')
        else:
            ax = dset.hvplot.image(y='level',
                                    x='latitude',
                                    clabel='Km',
                                    #aspect=1,
                                    cmap=cmap,
                                    shared_axes=False,
                                    height=height,
                                    logy=logy,
                                    responsive=True,
                                    title='Horizontal Length Scale of ' + str(vfname))
        return ax

    @pn.depends(vscalevars, vertical_log_vs, colormap, invert_colors)
    def plotVScale(vscalevars, vertical_log_vs, colormap, invert_colors):
        if vscalevars == 'sf':
            vfname = 'Stream Function'
        elif vscalevars == 'vp':
            vfname = 'Velocity Potential'
        elif vscalevars == 't':
            vfname = 'Unbalanced part of Temperature'
        elif vscalevars == 'q':
            vfname = 'Relative Humidity'
        elif vscalevars == 'qin':
            vfname = 'Relative Humidity'
        elif vscalevars == 'oz':
            vfname = 'Ozone'
        elif vscalevars == 'cw':
            vfname = 'Liquid Water Content'
        elif vscalevars == 'ps':
            vfname = 'Surface Pressure'
        elif vscalevars == 'sst':
            vfname = 'Sea Surface Temperature'

        if invert_colors == True:
            cmap = colormap[::-1]
        else:
            cmap = colormap

        if vertical_log_vs:
            logy=True
        else:
            logy=False

        if vscalevars == 'qin':
            vname = 'vscales_' + str(vscalevars)
            dset_tmp = catalog_berror[vname].to_dask()*1e2
            ax = dset.isel(latitude=slice(0,25)).hvplot.image(y='level',
                                                                x='latitude',
                                                                clabel='Grid Units',
                                                                #aspect=1,
                                                                cmap=cmap,
                                                                shared_axes=False,
                                                                height=height,
                                                                logy=logy,
                                                                responsive=True,
                                                                title='Vertical Length Scale of ' + str(vfname))
        elif vscalevars == 'ps':
            vname = 'vscales_' + str(vscalevars)
            dset = catalog_berror[vname].to_dask()
            ax = dset.hvplot.line(x='latitude',
                                clabel='Grid Units',
                                #aspect=1,
                                shared_axes=False,
                                cmap=cmap,
                                height=height,
                                responsive=True,
                                title='Vertical Length Scale of ' + str(vfname))
        elif vscalevars == 'sst':
            vname = 'vscales_' + str(vscalevars)
            dset = catalog_berror[vname].to_dask()
            ax_sst = dset.hvplot.image(y='latitude',
                                    x='longitude',
                                    clabel='Grid Units',
                                    #aspect=1,
                                    cmap=cmap,
                                    shared_axes=False,
                                    height=height_sst,
                                    geo=True,
                                    coastline=True,
                                    responsive=True,
                                    title='Vertical Length Scale of ' + str(vfname))
            ax = ax_sst * gv.feature.land.options(fill_color='k', line_color='w')
        else:
            vname = 'vscales_' + str(vscalevars)
            dset = catalog_berror[vname].to_dask()
            ax = dset.hvplot.image(y='level',
                                    x='latitude',
                                    clabel='Grid Units',
                                    #aspect=1,
                                    cmap=cmap,
                                    shared_axes=False,
                                    height=height,
                                    logy=logy,
                                    responsive=True,
                                    title='Vertical Length Scale of ' + str(vfname))
        return ax

    def LayoutSidebarBerror():

        card1 = pn.Card(pn.Row(balproj, pn.widgets.TooltipIcon(value='Choose a variable', align='start')),
                        pn.Row(level, pn.widgets.TooltipIcon(value='Choose a level', align='start')),
                        pn.Row(vertical_log_bp, pn.widgets.TooltipIcon(value='Log vertical axis', align='start')),
                        title='Balance Projection Matrices', collapsed=False)
        card2 = pn.Card(pn.Row(stdevvars, pn.widgets.TooltipIcon(value='Choose a variable', align='start')),
                        pn.Row(show_profile, pn.widgets.TooltipIcon(value='Whether to show a an average vertical profile', align='start')),
                        pn.Row(vertical_log_am, pn.widgets.TooltipIcon(value='Log vertical axis', align='start')),
                        title='Standard Deviations', collapsed=True)
        card3 = pn.Card(pn.Row(hscalevars, pn.widgets.TooltipIcon(value='Choose a variable', align='start')),
                        pn.Row(vertical_log_hs, pn.widgets.TooltipIcon(value='Log vertical axis', align='start')),
                        title='Horizontal Length Scales', collapsed=True)
        card4 = pn.Card(pn.Row(vscalevars, pn.widgets.TooltipIcon(value='Choose a variable', align='start')),
                        pn.Row(vertical_log_vs, pn.widgets.TooltipIcon(value='Log vertical axis', align='start')),
                        title='Vertical Length Scales', collapsed=True)

        # Função para alternar os estados dos cards
        def toggle_cards(event):
            if event.new == False:  # Se um card foi aberto, fecha o outro
                if event.obj is card1:
                    card2.collapsed = True
                    card3.collapsed = True
                    card4.collapsed = True
                elif event.obj is card2:
                    card1.collapsed = True
                    card3.collapsed = True
                    card4.collapsed = True
                elif event.obj is card3:
                    card1.collapsed = True
                    card2.collapsed = True
                    card4.collapsed = True
                elif event.obj is card4:
                    card1.collapsed = True
                    card2.collapsed = True
                    card3.collapsed = True

        # Monitorando mudanças no estado `collapsed`
        card1.param.watch(toggle_cards, 'collapsed')
        card2.param.watch(toggle_cards, 'collapsed')
        card3.param.watch(toggle_cards, 'collapsed')
        card4.param.watch(toggle_cards, 'collapsed')

        card_parameters = pn.Card('Click to expand cards.', card1, card2, card3, card4,
                pn.Row(colormap, pn.widgets.TooltipIcon(value='Choose a colormap', align='start')),
                pn.Row(invert_colors, pn.widgets.TooltipIcon(value='Invert the color range in the colormap', align='start')),
                title='Parameters', collapsed=False)

        return pn.Column(card_parameters)

    def LayoutMainBerror():
        main_text = pn.Column("""
        # Background Error Covariance

        Se the parameters on the left to update the map below.
        """)
        return pn.Column(main_text, pn.Row(plotBalProjs, plotStDev), pn.Row(plotHScale, plotVScale), monitor_warning_bottom_main, sizing_mode='stretch_width')

else:

    def LayoutSidebarBerror():
        main_text = pn.Column("""
        # Background Error Covariance

        Se the parameters on the left to update the map below.
        """)
        return pn.Column(main_text, sizing_mode='stretch_width')

    def LayoutMainBerror():
        main_text = pn.Column("""
        # Background Error Covariance

        Se the parameters on the left to update the map below.
        """)
        return pn.Column(main_text, sizing_mode='stretch_width')
