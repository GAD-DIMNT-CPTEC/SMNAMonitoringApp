#! /usr/bin/env python3

# Script to convert the GSI conventional diagnostic file to the parquet format.

# @cfbastarz (April, 2024)

import os
import gsidiag as gd

lpath = '/share/das/dist/carlos.bastarz/SMNAMonitoringApp/rdiag'

filein = os.path.join(lpath, 'diag_tmp', '2025101600', 'diag_conv_03.2025101600')

diagfile = gd.read_diag(filein)

# Escreve os dataframes das variáveis em disco no formato parquet
for var in diagfile.varNames:
    print(var)
    fileout = os.path.join(lpath, '2025101600', str(var) + '-diag_conv_03.2025101600.parquet')
    diagfile.obsInfo[var].to_parquet(fileout)

diagfile.close()
