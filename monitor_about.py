#! /usr/bin/env python3

import panel as pn

class MonitoringAppAbout:
    def __init__(self):
        pn.extension('floatpanel')

    def LayoutSidebar(self):
        cptec_logo = pn.pane.PNG('img/cptec.png', width=100)
        inpe_logo = pn.pane.PNG(
                'img/logo_mcti_vertical_positiva_02.png', 
                width=300)
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
        return logos


    def LayoutMain(self):
        aboutText = pn.Column("""
# About

The SMNA (Sistema de Modelagem Numérica e Assimilação de Dados - in portuguese) is the global data assimilation system from CPTEC. It is based on the Brazilian Atmospheric Model (BAM) and the Gridpoint Statistical Interpolation system (GSI). Currently, our system is capable of assimilating radiances (from the AMSU-A/B, SATWND, GNSS-RO and radiosondes).

The dashboard code is available at [our GitHub repository](https://github.com/GAD-DIMNT-CPTEC/SMNAMonitoringApp).
        """)
        return aboutText 
