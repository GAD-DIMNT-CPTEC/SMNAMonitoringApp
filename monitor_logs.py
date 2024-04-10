#! /usr/bin/env python3

import panel as pn
import pandas as pd
from urllib.request import urlopen
from datetime import datetime, timedelta

from monitor_dates import MonitoringAppDates
from monitor_texts import MonitoringAppTexts

pn.extension('texteditor')

monitor_app_texts = MonitoringAppTexts()
#monitor_error_logs = monitor_app_texts.warnings_logs()

monitoring_app_dates = MonitoringAppDates()
sdate = monitoring_app_dates.getDates()[0].strip()
edate = monitoring_app_dates.getDates()[1].strip()

start_date = datetime(int(sdate[0:4]), int(sdate[4:6]), int(sdate[6:8]), int(sdate[8:10]))
end_date = datetime(int(edate[0:4]), int(edate[4:6]), int(edate[6:8]), int(edate[8:10]))

date_range = [d.strftime('%Y%m%d%H') for d in pd.date_range(start_date, end_date, freq='6h')][::-1]
date = pn.widgets.Select(name='Date', value=date_range[-1], options=date_range)
      
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

@pn.depends(date)
def showLogs(date):   
    datemfct = calcDate(date, int(9))
    datepfct = calcDate(date, int(264))

    gsi_log = "http://ftp1.cptec.inpe.br/pesquisa/das/carlos.bastarz/SMNAMonitoringApp/logs/gsi/gsi_" + str(date) + ".log"           
    model_log = "http://ftp1.cptec.inpe.br/pesquisa/das/carlos.bastarz/SMNAMonitoringApp/logs/model/model_" + str(date) + "." + str(datemfct) + ".log"
    pos_log = "http://ftp1.cptec.inpe.br/pesquisa/das/carlos.bastarz/SMNAMonitoringApp/logs/pos/pos_" + str(date) + "." + str(datepfct) + ".log"
    pre_log = "http://ftp1.cptec.inpe.br/pesquisa/das/carlos.bastarz/SMNAMonitoringApp/logs/pre/pre_" + str(date) + ".log"

    try:
        read_log_gsi = openFile(gsi_log)
        show_log_gsi = pn.Column(pn.pane.Str(read_log_gsi, styles={'font-size': '10pt', 
                                        'line-height': '120%',
                                        'letter-spacing': '0px'}),
                                        auto_scroll_limit=10,
                                        view_latest=True,
                                        scroll=True,
                                        styles=dict(background='WhiteSmoke'),
                                        height=500)
    except:
        show_log_gsi = monitor_app_texts.warnings_logs(gsi_log)

    try:
        read_log_pre = openFile(pre_log)
        show_log_pre = pn.Column(pn.pane.Str(read_log_pre, styles={'font-size': '10pt', 
                                        'line-height': '120%',
                                        'letter-spacing': '0px'}),
                                        auto_scroll_limit=10,
                                        view_latest=True,
                                        scroll=True,
                                        styles=dict(background='WhiteSmoke'),
                                        height=500)        
    except:
        show_log_pre = monitor_app_texts.warnings_logs(pre_log)

    try:
        read_log_model = openFile(model_log)
        show_log_model = pn.Column(pn.pane.Str(read_log_model, styles={'font-size': '10pt', 
                                        'line-height': '120%',
                                        'letter-spacing': '0px'}),
                                        auto_scroll_limit=10,
                                        view_latest=True,
                                        scroll=True,
                                        styles=dict(background='WhiteSmoke'),
                                        height=500)    
    except:
        show_log_model = monitor_app_texts.warnings_logs(model_log)

    try:
        read_log_pos = openFile(pos_log)
        show_log_pos = pn.Column(pn.pane.Str(read_log_pos, styles={'font-size': '10pt', 
                                        'line-height': '120%',
                                        'letter-spacing': '0px'}),
                                        auto_scroll_limit=10,
                                        view_latest=True,
                                        scroll=True,
                                        styles=dict(background='WhiteSmoke'),
                                        height=500)    
    except:
        show_log_pos = monitor_app_texts.warnings_logs(pos_log)

    tabs = pn.Tabs(
                ('GSI', pn.Column('Log from the GSI run.', show_log_gsi)), 
                ('PRE', pn.Column('Log from the pre-processing run.', show_log_pre)), 
                ('MODEL', pn.Column('Log from the model run.', show_log_model)), 
                ('POST', pn.Column('Log from the post-processing run.', show_log_pos))
                )

    main_text = pn.Column("""
    # Full Logs

    Navigate trough the tabs below to visualize the logs from the latest run.
    """)

    return pn.Column(main_text, tabs)

def LayoutSidebar():
    card_parameters = pn.Card(date, title='Parameters', collapsed=False)
    return pn.Column(card_parameters)
