#!/usr/bin/env python
# coding: utf-8

import os
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import panel as pn
import hvplot.xarray
import numpy as np
import intake
import geopandas as gpd
import geoviews as gv

pn.extension(sizing_mode="stretch_width")

catalog_berror = intake.open_catalog('http://ftp1.cptec.inpe.br/pesquisa/das/carlos.bastarz/GSIMonitor/berror/catalog_berror.yml')

level_lst = np.arange(0,64, 1).tolist()
level = pn.widgets.IntSlider(name='Level', value=0, start=level_lst[0], step=1, end=level_lst[-1])

balproj_lst = ['agvin', 'bgvin', 'wgvin']
balproj = pn.widgets.Select(name='Balance Projection Matrix', value=balproj_lst[0], options=balproj_lst)

stdevvars_lst = ['sf', 'vp', 't', 'q', 'qin', 'oz', 'ps', 'cw', 'sst']
stdevvars = pn.widgets.Select(name='Standard Deviation', value=stdevvars_lst[0], options=stdevvars_lst)

show_profile = pn.widgets.Checkbox(name='Profile', value=False)

hscalevars_lst = ['sf', 'vp', 't', 'q', 'oz', 'cw', 'ps', 'sst']
hscalevars = pn.widgets.Select(name='Horizontal Length Scale', value=hscalevars_lst[0], options=hscalevars_lst)

vscalevars_lst = ['sf', 'vp', 't', 'q', 'oz', 'cw']
vscalevars = pn.widgets.Select(name='Vertical Length Scale', value=vscalevars_lst[0], options=vscalevars_lst)

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

vertical_log_bp = pn.widgets.Checkbox(name='Vertical Log', value=False)
vertical_log_am = pn.widgets.Checkbox(name='Vertical Log', value=False)
vertical_log_hs = pn.widgets.Checkbox(name='Vertical Log', value=False)
vertical_log_vs = pn.widgets.Checkbox(name='Vertical Log', value=False)

height=400
height_sst=325

@pn.depends(balproj, level, vertical_log_bp, colormap, invert_colors)
def plotBalProjs(balproj, level, vertical_log_bp, colormap, invert_colors):
    if invert_colors == True:
        cmap = colormap + '_r'
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
        cmap = colormap + '_r'
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

        ax = ax_sst * gv.feature.land.options(fill_color='k', line_color='k')      
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
        cmap = colormap + '_r'
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

        ax = ax_sst * gv.feature.land.options(fill_color='k', line_color='k')       
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
        cmap = colormap + '_r'
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
        ax = ax_sst * gv.feature.land.options(fill_color='k', line_color='k')
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
    card_parameters = pn.Card('Click to expand cards.',
            pn.Card(balproj, level, vertical_log_bp, title='Balance Projection Matrices', collapsed=False), 
            pn.Card(stdevvars, show_profile, vertical_log_am, title='Standard Deviations', collapsed=True),
            pn.Card(hscalevars, vertical_log_hs, title='Horizontal Length Scales', collapsed=True),
            pn.Card(vscalevars, vertical_log_vs, title='Vertical Length Scales', collapsed=True),
            colormap, invert_colors,
            title='Parameters', collapsed=False)
    return pn.Column(card_parameters)

def LayoutMainBerror():
    main_text = pn.Column("""
    # Background Error Covariance

    Se the parameters on the left to update the map below.
    """)
    return pn.Column(main_text, pn.Row(plotBalProjs, plotStDev), pn.Row(plotHScale, plotVScale))