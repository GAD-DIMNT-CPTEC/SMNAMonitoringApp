#! /usr/bin/env python3

import panel as pn
import pandas as pd

#from bokeh.models import HTMLTemplateFormatter
from bokeh.models import ColumnDataSource, HTMLTemplateFormatter

class MonitoringAppCStatus:
    def __init__(self):
        pn.extension('floatpanel')
        pn.extension('tabulator')

    def LogoINPE(self):
        inpe_logo = pn.pane.PNG('img/logo_mcti_vertical_positiva_02.png', width=300)
        logo_inpe = pn.Column(
                pn.Row(
                  pn.layout.HSpacer(),
                  inpe_logo, 
                  pn.layout.HSpacer(),
                ))
        return logo_inpe

    def LogoCPTEC(self):
        cptec_logo = pn.pane.PNG('img/cptec.png', width=100)
        logo_cptec = pn.Column(
                pn.Row(
                  pn.layout.HSpacer(),
                  cptec_logo,
                  pn.layout.HSpacer(),
                ))
        return logo_cptec

    def LogoSMNAMonitoringApp(self):
        gsimonitor_logo = pn.pane.PNG('img/gsimonitor.png', width=150)
        logo_gsimonitor = pn.Column(
                pn.Row(
                  pn.layout.HSpacer(),
                  gsimonitor_logo,
                  pn.layout.HSpacer(),
                ))
        return logo_gsimonitor

    def LayoutSidebar(self):
        inpe_logo = self.LogoINPE(),
        cptec_logo = self.LogoCPTEC(),
        logos = pn.Column(
                pn.Row(
                  pn.layout.HSpacer(),
                  inpe_logo, 
                  pn.layout.HSpacer(),
                ),
                pn.Row(
                  pn.layout.HSpacer(),
                  cptec_logo,
                  pn.layout.HSpacer(),
                ))
        #return pn.Column(logos, show_modal())
        return pn.Column(logos)

    def LayoutMain(self):

        self.logs = "http://ftp1.cptec.inpe.br/pesquisa/das/carlos.bastarz/SMNAMonitoringApp/logs/logs.csv"           
        df = pd.read_csv(self.logs)

        link_formatters = {
            "Action GSI": HTMLTemplateFormatter(template="<code><%= value %></code>"),
            "Action PRE": HTMLTemplateFormatter(template="<code><%= value %></code>"),
            "Action MODEL": HTMLTemplateFormatter(template="<code><%= value %></code>"),
            "Action POS": HTMLTemplateFormatter(template="<code><%= value %></code>"),
        }

        stylesheet = """
        .tabulator-cell {
            font-size: 12px;
        }
        """

        cs_table = pn.widgets.Tabulator(df, 
                selectable=False,
                show_index=False,
                disabled=True,
                theme="bootstrap4",
                #frozen_rows=[-2, -1],
                text_align='center',
                stylesheets=[stylesheet],
                formatters=link_formatters)

        welcomeText1 = pn.Column("""
        # Current Status
        
        Check the current status from the operational system in the table below.
        """)

        welcomeText2 = pn.Column("""
        **Legend:**

        * **A** = Awaiting
        * **C** = Completed
        * **P** = Processing
        """)
        return pn.Column(welcomeText1, cs_table, welcomeText2, sizing_mode='stretch_width')
