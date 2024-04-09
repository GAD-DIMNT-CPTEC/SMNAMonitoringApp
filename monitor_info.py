#! /usr/bin/env python3

import panel as pn

#from monitor_modal import show_modal#, show_modal_1


class MonitoringAppInfo:
    def __init__(self):
        pn.extension('floatpanel')

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

    def LogoGSIMonitor(self):
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
        welcomeText = pn.Column("""
        # Current Status
        
        Check the current status from the operational system in the table below.
        
        | CURRENT DATE | LAST OPERATIONAL RUN | STATUS | NOTE | ACTION |
        |--------------|----------------------|--------|------|--------|
        | 2024-02-22 21:00 | 2024-02-25 00:00 | COMPLETED | 1 TRIAL(S) ||
        | 2024-02-22 03:00 | 2024-02-25 06:00 | COMPLETED | 1 TRIAL(S) ||
        | 2024-02-22 09:00 | 2024-02-25 12:00 | COMPLETED | 1 TRIAL(S) ||
        | 2024-02-22 15:00 | 2024-02-25 18:00 | COMPLETED | 2 TRIAL(S) | CHECK FOR LOGS |
        | 2024-02-23 21:00 | 2024-02-25 00:00 | COMPLETED | 1 TRIAL(S) ||
        | 2024-02-23 03:00 | 2024-02-25 06:00 | COMPLETED | 1 TRIAL(S) ||
        | 2024-02-23 09:00 | 2024-02-25 12:00 | COMPLETED | 1 TRIAL(S) ||
        | 2024-02-23 15:00 | 2024-02-25 18:00 | COMPLETED | 2 TRIAL(S) | CHECK FOR LOGS |
        | 2024-02-24 21:00 | 2024-02-25 00:00 | COMPLETED | 1 TRIAL(S) ||
        | 2024-02-24 03:00 | 2024-02-25 06:00 | COMPLETED | 1 TRIAL(S) ||
        | 2024-02-24 09:00 | 2024-02-25 12:00 | COMPLETED | 1 TRIAL(S) ||
        | 2024-02-24 15:00 | 2024-02-25 18:00 | COMPLETED | 2 TRIAL(S) | CHECK FOR LOGS |
        | 2024-02-25 21:00 | 2024-02-25 00:00 | COMPLETED | 1 TRIAL(S) ||
        | 2024-02-25 03:00 | 2024-02-25 06:00 | COMPLETED | 1 TRIAL(S) ||
        | 2024-02-25 09:00 | 2024-02-25 12:00 | COMPLETED | 1 TRIAL(S) ||
        | 2024-02-25 15:00 | 2024-02-25 18:00 | COMPLETED | 2 TRIAL(S) | CHECK FOR LOGS |
        | 2024-02-26 21:00 | 2024-02-26 00:00 | COMPLETED | 1 TRIAL(S) ||
        | 2024-02-26 03:00 | 2024-02-26 06:00 | COMPLETED | 2 TRIAL(S) | CHECK FOR LOGS |
        | 2024-02-26 09:00 | 2024-02-26 12:00 | COMPLETED | 1 TRIAL(S) ||
        | 2024-02-26 15:00 | 2024-02-26 18:00 | COMPLETED | 1 TRIAL(S) ||
        | 2024-02-27 21:00 | 2024-02-27 00:00 | COMPLETED | 1 TRIAL(S) ||
        | 2024-02-27 03:00 | 2024-02-27 06:00 | COMPLETED | 1 TRIAL(S) ||
        | 2024-02-27 09:00 | 2024-02-27 12:00 | COMPLETED | 2 TRIAL(S) | CHECK FOR LOGS |
        | 2024-02-27 15:00 | 2024-02-27 18:00 | COMPLETED | 1 TRIAL(S) ||
        | 2024-02-28 21:00 | 2024-02-28 00:00 | COMPLETED | 2 TRIAL(S) | CHECK FOR LOGS |
        | 2024-02-28 03:00 | 2024-02-28 06:00 | COMPLETED | 1 TRIAL(S) ||
        | 2024-02-28 09:00 | 2024-02-28 12:00 | PROCESSING |  ||
        """)
        return pn.Column(welcomeText)
