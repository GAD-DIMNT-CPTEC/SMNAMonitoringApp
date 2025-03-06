#!/bin/bash -x

cd /home/carlos/GitHub/SMNAMonitoringApp.repo

#source ~/.bashrc
#source "$(conda info --base)/etc/profile.d/conda.sh"
source ~/miniconda3/etc/profile.d/conda.sh
#conda init bash

conda activate SCANPLOT_PANEL_UP
#source activate SCANPLOT_PANEL_UP

/home/carlos/miniconda3/envs/SCANPLOT_PANEL_UP/bin/panel serve monitor.py --port 5006 &

sleep 3

npx electron .
#npm start
