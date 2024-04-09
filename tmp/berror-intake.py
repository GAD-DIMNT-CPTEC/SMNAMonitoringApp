#!/usr/bin/env python
# coding: utf-8

# In[1]:


import gsiberror as gb
import os
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import panel as pn
import hvplot.xarray
import numpy as np
import intake

pn.extension()


# In[2]:


catalog_berror = intake.open_catalog('http://ftp1.cptec.inpe.br/pesquisa/das/carlos.bastarz/GSIMonitor/berror/catalog_berror.yml')


# In[3]:


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

vertical_log = pn.widgets.Checkbox(name='Vertical Log', value=False)


# In[4]:


@pn.depends(balproj, level, vertical_log)
def plotBalProjs(balproj, level, vertical_log):
    vname = 'balprojs_' + str(balproj)
    dset = catalog_berror[vname].to_dask()
    if balproj == 'wgvin':
        ax = dset.isel(level=0, latitude=slice(0,-2)).hvplot.line(x='latitude', 
                                                                  title='Projection of the Stream Function over the balanced part of Surface Pressure')      
    elif balproj == 'bgvin':
        if vertical_log:
            ax = dset.hvplot.quadmesh(y='level', 
                                      x='latitude',
                                      logy=True,
                                      #clabel='Km',
                                      aspect=1,
                                      cmap='jet',
                                      frame_height=500,
                                      title='Projection of the Stream Function over the balanced part of Velocity Potential')
        else:
            ax = dset.hvplot.quadmesh(y='level', 
                                      x='latitude',
                                      logy=False,
                                      #clabel='Km',
                                      aspect=1,
                                      cmap='jet',
                                      frame_height=500,
                                      title='Projection of the Stream Function over the balanced part of Velocity Potential')            
    elif balproj == 'agvin':
        if vertical_log:
            ax = dset.isel(level_2=level).hvplot.quadmesh(y='level', 
                                                          x='latitude',
                                                          logy=True,
                                                          #clabel='Km',
                                                          aspect=1,
                                                          cmap='jet',
                                                          frame_height=500,
                                                          title='Projection of Stream Function at level ' + str(level) + ' over the vertical \nprofile of the balanced part of Virtual Temperature')
        else:        
            ax = dset.isel(level_2=level).hvplot.quadmesh(y='level', 
                                                          x='latitude',
                                                          logy=False,
                                                          #clabel='Km',
                                                          aspect=1,
                                                          cmap='jet',
                                                          frame_height=500,
                                                          title='Projection of Stream Function at level ' + str(level) + ' over the vertical \nprofile of the balanced part of Virtual Temperature')        
    return ax


# In[5]:


pn.Column(balproj, level, vertical_log, plotBalProjs).servable()


# In[6]:


@pn.depends(stdevvars, show_profile, vertical_log)
def plotStDev(stdevvars, show_profile, vertical_log):
    if stdevvars == 'sf': 
        vfname = 'Stream Function'
    elif stdevvars == 'vp':
        vfname = 'Velocity Potential'
    elif stdevvars == 't':
        vfname = 'Unbalanced part of Temperature'
    elif stdevvars == 'q':
        vfname = 'Relative Humidity'
    elif stdevvars == 'qin':
        vfname = 'Relative Humidity'
    elif stdevvars == 'oz':
        vfname = 'Ozone'
    elif stdevvars == 'cw':
        vfname = 'Liquid Water Content'
    elif stdevvars == 'ps':
        vfname = 'Surface Pressure'
    elif stdevvars == 'sst':
        vfname = 'Sea Surface Temperature'

    if vertical_log:
        logy=True
    else:
        logy=False
    
    if stdevvars == 'qin':
        vname = 'amplitudes_' + str(stdevvars)
        dset = catalog_berror[vname].to_dask()*1e2
        if show_profile:
            ax = dset.isel(latitude=slice(0,25)).mean(dim='latitude').hvplot.line(#y='level',
                                                                 #x='latitude',
                                                                 #clabel='Km',
                                                                 aspect=1,
                                                                 cmap='jet',
                                                                 frame_height=500,
                                                                 invert=True,
                                                                 logy=logy,
                                                                 title='Standard Deviation of ' + str(vfname))
        else:
            ax = dset.isel(latitude=slice(0,25)).hvplot.quadmesh(y='level',
                                                                 x='latitude',
                                                                 #clabel='Km',
                                                                 aspect=1,
                                                                 cmap='jet',
                                                                 frame_height=500,
                                                                 logy=logy,
                                                                 title='Standard Deviation of ' + str(vfname))            
    elif stdevvars == 'ps':
        vname = 'amplitudes_' + str(stdevvars)
        dset = catalog_berror[vname].to_dask() 
        ax = dset.hvplot.line(x='latitude',
                              #clabel='Km',
                              aspect=1,
                              cmap='jet',
                              frame_height=500,
                              title='Standard Deviation of ' + str(vfname))  
    elif stdevvars == 'sst':
        vname = 'amplitudes_' + str(stdevvars)
        dset = catalog_berror[vname].to_dask() 
        ax = dset.hvplot.quadmesh(y='latitude',
                                  x='longitude',
                                  #clabel='Km',
                                  aspect=1,
                                  cmap='jet',
                                  frame_height=500,
                                  geo=True,
                                  coastline=True,  
                                  title='Standard Deviation of ' + str(vfname))          
    else:
        vname = 'amplitudes_' + str(stdevvars)
        dset = catalog_berror[vname].to_dask()         
        if show_profile:
            ax = dset.mean(dim='latitude').hvplot.line(#y='level',
                                      #x='latitude',
                                      #clabel='Km',
                                      aspect=1,
                                      cmap='jet',
                                      frame_height=500,
                                      invert=True,
                                      #show_grid=True,
                                      logy=logy,
                                      title='Standard Deviation of ' + str(vfname))        
        else:
            ax = dset.hvplot.quadmesh(y='level',
                                      x='latitude',
                                      #clabel='Km',
                                      aspect=1,
                                      cmap='jet',
                                      frame_height=500, 
                                      logy=logy,
                                      title='Standard Deviation of ' + str(vfname))         
    return ax


# In[7]:


pn.Column(stdevvars, show_profile, vertical_log, plotStDev).servable()


# In[8]:


@pn.depends(hscalevars, vertical_log)
def plotHScale(hscalevars, vertical_log):
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

    if vertical_log:
        logy=True
    else:
        logy=False
        
    vname = 'hscales_' + str(hscalevars)
    dset = catalog_berror[vname].to_dask()*1e-3
    
    if hscalevars == 'ps':
        ax = dset.hvplot.line(x='latitude',
                              clabel='Km',
                              aspect=1,
                              cmap='jet',
                              frame_height=500,
                              title='Horizontal Length Scale of ' + str(vfname))  
    elif hscalevars == 'sst':       
        ax = dset.hvplot.quadmesh(y='latitude',
                                  x='longitude',
                                  clabel='Km',
                                  aspect=1,
                                  cmap='jet',
                                  frame_height=500,
                                  geo=True,
                                  coastline=True,  
                                  title='Horizontal Length Scale of ' + str(vfname))          
    else:       
        ax = dset.hvplot.quadmesh(y='level',
                                  x='latitude',
                                  clabel='Km',
                                  aspect=1,
                                  cmap='jet',
                                  frame_height=500, 
                                  logy=logy,
                                  title='Horizontal Length Scale of ' + str(vfname))        
    return ax


# In[9]:


pn.Column(hscalevars, vertical_log, plotHScale).servable()


# In[12]:


@pn.depends(vscalevars, vertical_log)
def plotVScale(vscalevars, vertical_log):
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

    if vertical_log:
        logy=True
    else:
        logy=False
    
    if vscalevars == 'qin':
        vname = 'vscales_' + str(vscalevars)
        dset_tmp = catalog_berror[vname].to_dask()*1e2
        ax = dset.isel(latitude=slice(0,25)).hvplot.quadmesh(y='level',
                                                             x='latitude',
                                                             clabel='Grid Units',
                                                             aspect=1,
                                                             cmap='jet',
                                                             frame_height=500,
                                                             logy=logy,
                                                             title='Vertical Length Scale of ' + str(vfname))
    elif vscalevars == 'ps':
        vname = 'vscales_' + str(vscalevars)
        dset = catalog_berror[vname].to_dask()           
        ax = dset.hvplot.line(x='latitude',
                              clabel='Grid Units',
                              aspect=1,
                              cmap='jet',
                              frame_height=500,
                              title='Vertical Length Scale of ' + str(vfname))  
    elif vscalevars == 'sst':
        vname = 'vscales_' + str(vscalevars)
        dset = catalog_berror[vname].to_dask()          
        ax = dset.hvplot.quadmesh(y='latitude',
                                  x='longitude',
                                  clabel='Grid Units',
                                  aspect=1,
                                  cmap='jet',
                                  frame_height=500,
                                  geo=True,
                                  coastline=True,  
                                  title='Vertical Length Scale of ' + str(vfname))          
    else:
        vname = 'vscales_' + str(vscalevars)
        dset = catalog_berror[vname].to_dask()          
        ax = dset.hvplot.quadmesh(y='level',
                                  x='latitude',
                                  clabel='Grid Units',
                                  aspect=1,
                                  cmap='jet',
                                  frame_height=500, 
                                  logy=logy,
                                  title='Vertical Length Scale of ' + str(vfname))        
    return ax


# In[13]:


pn.Column(vscalevars, vertical_log, plotVScale).servable()


# In[ ]:




