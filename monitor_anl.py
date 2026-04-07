#!/usr/bin/env python
# coding: utf-8

import panel as pn
import requests
import io
import time
import pandas as pd
from datetime import datetime
from urllib.parse import urljoin

from monitor_texts import MonitoringAppTexts
from monitor_dates import MonitoringAppDates

pn.extension()

BASE_URL = "https://dataserver.cptec.inpe.br/dataserver_dimnt/das/carlos.bastarz/SMNAMonitoringApp/anls_imgs/imgs/"

monitor_app_texts = MonitoringAppTexts()
monitor_warning_bottom_main = monitor_app_texts.warnings()

monitoring_app_dates = MonitoringAppDates()
sdate = monitoring_app_dates.getDates()[0].strip()
edate = monitoring_app_dates.getDates()[1].strip()

start_date = datetime(int(sdate[0:4]), int(sdate[4:6]), int(sdate[6:8]), int(sdate[8:10]))
end_date = datetime(int(edate[0:4]), int(edate[4:6]), int(edate[6:8]), int(edate[8:10]))

datas = [d.strftime('%Y%m%d%H') for d in pd.date_range(start_date, end_date, freq='6h')][::-1]

variaveis = [
    "10_metre_u-wind_component",
    "10_metre_v-wind_component",
    "Geopotential_height",
    "Meridional_wind_v"
]

niveis = ["925", "850", "500"]
tempos = [str(i) for i in range(0, 73, 6)]

data = pn.widgets.Select(name="Date", options=datas, width=245)
var = pn.widgets.Select(name="Variable", options=variaveis, width=245)
lev = pn.widgets.Select(name="Level", options=niveis, width=245)
tmp = pn.widgets.Select(name="Time", options=tempos, width=245)

def build_filename(prefix, d, v, l, t):
    return f"{prefix}_{d}_{v}_l{l}_f{t}.jpg"

def fetch_image(url):
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    bio = io.BytesIO(r.content)
    bio.seek(0)
    return bio

@pn.depends(data, var, lev, tmp)
def smna_url(d, v, l, t):
    if not (d and v and l and t):
        return None
    return urljoin(BASE_URL, f"SMNA/{d}/{v}/{l}/{t}.jpg")

@pn.depends(data, var, lev, tmp)
def bam_url(d, v, l, t):
    if not (d and v and l and t):
        return None
    return urljoin(BASE_URL, f"BAM/{d}/{v}/{l}/{t}.jpg")

@pn.depends(data, var, lev, tmp)
def img_smna(d, v, l, t):
    if not (d and v and l and t):
        return pn.pane.Markdown("Selecione parâmetros")

    url = urljoin(BASE_URL, f"SMNA/{d}/{v}/{l}/{t}.jpg")
    return pn.pane.JPG(f"{url}?t={int(time.time())}", width=800)

@pn.depends(data, var, lev, tmp)
def img_bam(d, v, l, t):
    if not (d and v and l and t):
        return pn.pane.Markdown("Selecione parâmetros")

    url = urljoin(BASE_URL, f"BAM/{d}/{v}/{l}/{t}.jpg")
    return pn.pane.JPG(f"{url}?t={int(time.time())}", width=800)

download_smna = pn.widgets.FileDownload(
    icon="download",
    label="Download SMNA",
    callback=pn.bind(
        fetch_image,
        pn.bind(lambda d, v, l, t: urljoin(BASE_URL, f"SMNA/{d}/{v}/{l}/{t}.jpg"), data, var, lev, tmp)),
    #filename=pn.bind(build_filename, "SMNA", data, var, lev, tmp),
    button_type="success",
    width=310
)

download_bam = pn.widgets.FileDownload(
    icon="download",
    label="Download BAM",
    callback=pn.bind(
        fetch_image,
        pn.bind(lambda d, v, l, t: urljoin(BASE_URL, f"BAM/{d}/{v}/{l}/{t}.jpg"), data, var, lev, tmp)),
    #filename=pn.bind(build_filename, "BAM", data, var, lev, tmp),
    button_type="success",
    width=310
)

def update_filename(event=None):
    if not (data.value and var.value and lev.value and tmp.value):
        return

    d = data.value
    v = var.value
    l = lev.value
    t = tmp.value

    download_smna.filename = build_filename("SMNA", d, v, l, t)
    download_bam.filename  = build_filename("BAM", d, v, l, t)

for w in [data, var, lev, tmp]:
    w.param.watch(update_filename, "value")

update_filename()        

def LayoutSidebarAnl():
    return pn.Column(
        pn.Card(
            pn.Row(data, pn.widgets.TooltipIcon(value='Choose a date')),
            pn.Row(var, pn.widgets.TooltipIcon(value='Choose a variable')),
            pn.Row(lev, pn.widgets.TooltipIcon(value='Choose a level')),
            pn.Row(tmp, pn.widgets.TooltipIcon(value='Choose forecast time')),
            title='Parameters',
            collapsed=False
        )
    )

def LayoutMainAnl():
    main_text = pn.pane.Markdown("""
    # Analysis Plots

    Set the parameters on the left to update the maps.
    """)

    plots = pn.Row(
        pn.Column("### SMNA", img_smna, download_smna),
        pn.Column("### BAM", img_bam, download_bam)
    )

    return pn.Column(
        main_text,
        plots,
        monitor_warning_bottom_main,
        sizing_mode="stretch_both"
    )