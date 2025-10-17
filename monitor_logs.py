#! /usr/bin/env python3

import os
import requests
import panel as pn
import pandas as pd
from urllib.request import urlopen
from datetime import datetime, timedelta

from monitor_dates import MonitoringAppDates
from monitor_texts import MonitoringAppTexts

pn.extension('texteditor')
#pn.extension('codeeditor')

monitor_app_texts = MonitoringAppTexts()
monitor_warning_bottom_main = monitor_app_texts.warnings()

monitoring_app_dates = MonitoringAppDates()
sdate = monitoring_app_dates.getDates()[0].strip()
edate = monitoring_app_dates.getDates()[1].strip()

start_date = datetime(int(sdate[0:4]), int(sdate[4:6]), int(sdate[6:8]), int(sdate[8:10]))
end_date = datetime(int(edate[0:4]), int(edate[4:6]), int(edate[6:8]), int(edate[8:10]))

date_range = [d.strftime('%Y%m%d%H') for d in pd.date_range(start_date, end_date, freq='6h')][::-1]
date = pn.widgets.Select(name='Date', value=date_range[0], options=date_range, width=240)
      
def openFile(log):
    open_log = urlopen(log)
    contents_log = open_log.read()
    decoded_line = contents_log.decode("utf-8")
    open_log.close()
    return decoded_line

def calcDate(date, delta):
    datefct = datetime.strptime(str(date), "%Y%m%d%H")
    datefct = datefct + timedelta(hours=delta)
    return str(datefct.strftime("%Y%m%d%H"))

def check_url_exists(url):
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False  

def create_download_button(log_url):
    log_local = os.path.basename(log_url)

    def log_download():
        try:
            response = requests.get(log_url, timeout=10)
            response.raise_for_status()

            with open(log_local, "wb") as f:
                f.write(response.content)

            return log_local
        except requests.exceptions.RequestException as e:
            print(f"❌ Error downloading file {log_local}: {e}")
            return None

    return pn.widgets.FileDownload(
        icon='download',
        button_type='success',
        callback=log_download if check_url_exists(log_url) else None,
        filename=log_local,
        width=310,
        disabled=not check_url_exists(log_url),
    )

@pn.depends(date)
def showLogs(date):   
    datemfct = calcDate(date, int(9))
    datepfct = calcDate(date, int(264))

    logs = {
        "GSI": f"https://dataserver.cptec.inpe.br/dataserver_dimnt/das/carlos.bastarz/SMNAMonitoringApp/logs/gsi/gsi_{date}.log",
        "MODEL": f"https://dataserver.cptec.inpe.br/dataserver_dimnt/das/carlos.bastarz/SMNAMonitoringApp/logs/model/model_{date}.{datemfct}.log",
        "POS": f"https://dataserver.cptec.inpe.br/dataserver_dimnt/das/carlos.bastarz/SMNAMonitoringApp/logs/pos/pos_{date}.{datepfct}.log",
        "PRE": f"https://dataserver.cptec.inpe.br/dataserver_dimnt/das/carlos.bastarz/SMNAMonitoringApp/logs/pre/pre_{date}.log"
    }

    tabs = []
    
    for name, log_url in logs.items():
        log_local = os.path.basename(log_url)
        
        if check_url_exists(log_url):
            read_log = openFile(log_url)
            log_display = pn.Column(
                pn.pane.Str(read_log, styles={'font-size': '10pt', 'line-height': '120%'}),
                auto_scroll_limit=10,
                view_latest=True,
                scroll=True,
                styles=dict(background='WhiteSmoke'),
                height=500)
            #log_display = pn.Column( 
            #    pn.widgets.CodeEditor(value=read_log, 
            #                          language="plaintext", 
            #                          height=500, 
            #                          readonly=True))
            download_button = create_download_button(log_url)
        else:
            log_display = pn.pane.Alert(f"🛑 **Error:** Log file is not available. File name is **`{log_local}` (check_url_exists)**.", alert_type='danger')
            download_button = None

        tabs.append((name, pn.Column(f"Log from {name} run.", log_display, download_button)))

    main_text = pn.Column("""
    # Full Logs

    Navigate trough the tabs below to visualize the logs from the latest run.
    """)

    return pn.Column(main_text, pn.Tabs(*tabs, dynamic=True), monitor_warning_bottom_main, sizing_mode='stretch_width')

def LayoutSidebar():
    card_parameters = pn.Card(pn.Row(date, pn.widgets.TooltipIcon(value='Choose a date', align='start')), title='Parameters', collapsed=False)
    return pn.Column(card_parameters)
