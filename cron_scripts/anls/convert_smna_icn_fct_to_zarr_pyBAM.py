#!/usr/bin/env python
# coding: utf-8

# In[1]:

import os
import pyBAM as pb
import matplotlib.pyplot as plt
import xarray as xr
import hvplot.xarray


# In[2]:

lpath = '/share/das/dist/carlos.bastarz/SMNAMonitoringApp/anls'

ficn = os.path.join(lpath, 'spec_tmp', '2025101600', 'GFCTCPT20251016002025101600F.dic.TQ0299L064')
ffct = os.path.join(lpath, 'spec_tmp', '2025101600', 'GFCTCPT20251016002025101606F.dir.TQ0299L064')

icn = pb.openBAM(ficn)
fct = pb.openBAM(ffct)


# In[3]:


#%%time

vars3d_spec = [
    'DIVERGENCE',
    'VORTICITY'
    'SPECIFIC HUMIDITY',
    'VIRTUAL TEMPERATURE',
]

vars3d_grid = [
    'LIQ MIXING RATIO PROGNOSTIC',
    'ICE MIXING RATIO PROGNOSTIC',
    'CLOUD TOTAL PROGNOSTIC',
]    

icn_lst = []

for field in icn.VarNames:
    if field in vars3d_spec:
        icn_lst.append(icn.getField3D(field))
    else:
        if field in vars3d_grid:
            icn_lst_z = []
            for level in range(icn.nlevels):
                icn_lst_z.append(icn.getField(field, zlevel=level))
            #icn_lst.append(xr.merge(icn_lst_z, compat='override'))
            icn_lst.append(xr.concat(icn_lst_z, dim='lev'))
        else:
            icn_lst.append(icn.getField(field))   

icn_dset = xr.merge(icn_lst)


# In[ ]:


icn.close()


# In[4]:


#%%time

icn_dset.to_zarr(os.path.join(lpath, '2025101600','GFCTCPT20251016002025101600F.icn.TQ0299L064.zarr'), mode='w', consolidated=True)


# In[5]:


#%%time

vars3d_spec = [
    'DIVERGENCE',
    'VORTICITY'
    'SPECIFIC HUMIDITY',
    'VIRTUAL TEMPERATURE',
]

vars3d_grid = [
    'LIQ MIXING RATIO PROGNOSTIC',
    'ICE MIXING RATIO PROGNOSTIC',
    'CLOUD TOTAL PROGNOSTIC',
    'OZONE MIXING RATIO',
]    

fct_lst = []

for field in fct.VarNames:
    if field in vars3d_spec:
        fct_lst.append(fct.getField3D(field))
    else:
        if field in vars3d_grid:
            fct_lst_z = []
            for level in range(fct.nlevels):
                fct_lst_z.append(fct.getField(field, zlevel=level))
            #fct_lst.append(xr.merge(fct_lst_z, compat='override'))
            fct_lst.append(xr.concat(fct_lst_z, dim='lev'))
        else:
            fct_lst.append(fct.getField(field))
            
fct_dset = xr.merge(fct_lst)


# In[6]:


#%%time

fct_dset.to_zarr(os.path.join(lpath, '2025101600','GFCTCPT20251016002025101606F.fct.TQ0299L064.zarr'), mode='w', consolidated=True)


# In[7]:


fct.close()    


# In[ ]:




