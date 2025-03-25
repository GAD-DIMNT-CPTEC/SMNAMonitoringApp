#! /usr/bin/env python3

import panel as pn

from monitor_info import MonitoringAppInfo

monitor_info_logos = MonitoringAppInfo()
monitor_logo_cptec = monitor_info_logos.LogoCPTEC()
monitor_gsimonitor_logo = monitor_info_logos.LogoSMNAMonitoringApp()

class MonitoringAppFloatPanel:
    def __init__(self):
        pn.extension('floatpanel')

    def floatPanel(self):

        config1 = {'headerControls':{'maximize': 'remove', 'smallify': 'remove'}}

        text_float_panel = """
        # SMNA Monitoring App V0.0.0a1
        
        SMNA Monitoring App for the SMNA data assimilation system.
        
        ---
        
        CPTEC-INPE, 2025.
        """
        
        float_panel = pn.layout.FloatPanel(
            pn.Tabs(('About',
            #pn.Row(text_float_panel, monitor_logo_cptec)),
            pn.Row(text_float_panel, monitor_gsimonitor_logo)),
                   ('Bug Report', "Found a bug? Open an issue at the [project's GitHub](https://github.com/GAD-DIMNT-CPTEC/SMNAMonitoringApp/issues) or send an email to [carlos.bastarz@inpe.br](mailto:carlos.bastarz@inpe.br)."),
                   ('Contribute', 'Want to contribute with the SMNA Monitoring App development? Send an email to [carlos.bastarz@inpe.br](mailto:carlos.bastarz@inpe.br).'),
                   ), 
            name='SMNA Monitoring App', 
            contained=False, 
            position='center', 
            margin=0, 
            height=260,
            width=600,
            config=config1)

        return float_panel
