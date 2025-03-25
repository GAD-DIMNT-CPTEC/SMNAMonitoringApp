#! /usr/bin/env python3

import panel as pn

from monitor_info import MonitoringAppInfo
from monitor_cstatus import MonitoringAppCStatus
from monitor_anl import LayoutSidebarAnl, LayoutMainAnl
from monitor_about import MonitoringAppAbout
from monitor_jo import monitor_jo_sidebar, monitor_jo_main
from monitor_mass import MonitoringAppMass
from monitor_armobs import monitor_armobs_sidebar, monitor_armobs_main
from monitor_berror import LayoutSidebarBerror, LayoutMainBerror
from monitor_rdiag import LayoutSidebarRdiag, LayoutMainRdiag
from monitor_objeval import LayoutSidebarObjEval, LayoutMainObjEval

from monitor_texts import MonitoringAppTexts
from monitor_floatpanel import MonitoringAppFloatPanel
from monitor_logs import showLogs, LayoutSidebar

# Info
monitoring_app_info = MonitoringAppInfo()
monitor_info_sidebar = monitoring_app_info.LayoutSidebar()
monitor_info_sidebar_logoinpe = monitoring_app_info.LogoINPE()
monitor_info_sidebar_logocptec = monitoring_app_info.LogoCPTEC()
monitor_info_main = monitoring_app_info.LayoutMain()

# CStatus
monitoring_app_cstatus = MonitoringAppCStatus()
monitor_cstatus_sidebar = monitoring_app_cstatus.LayoutSidebar()
monitor_cstatus_main = monitoring_app_cstatus.LayoutMain()

# Anl
monitor_anl_main = LayoutMainAnl
monitor_anl_sidebar = LayoutSidebarAnl

# Rdiag
monitor_rdiag_main = LayoutMainRdiag
monitor_rdiag_sidebar = LayoutSidebarRdiag

# Berror
monitor_berror_main = LayoutMainBerror
monitor_berror_sidebar = LayoutSidebarBerror

# About
monitoring_app_about = MonitoringAppAbout()
monitor_about_sidebar = monitoring_app_about.LayoutSidebar()
monitor_about_main = monitoring_app_about.LayoutMain()

# Mass
monitoring_app_mass = MonitoringAppMass()
monitor_mass_sidebar = monitoring_app_mass.LayoutSidebar()
monitor_mass_main = monitoring_app_mass.LayoutMain()

# ObjEval
monitor_objeval_main = LayoutMainObjEval
monitor_objeval_sidebar = LayoutSidebarObjEval

# Texts
monitor_app_texts = MonitoringAppTexts()
monitor_warning_bottom_main = monitor_app_texts.warnings()

# Logs 
monitor_logs_main = showLogs
monitor_logs_sidebar = LayoutSidebar

# Float Panel
monitor_app_float_panel = MonitoringAppFloatPanel()
monitor_float_panel = monitor_app_float_panel.floatPanel()

class MonitoringApp:
    def __init__(self):
        pn.extension('floatpanel')
        pn.extension('tabulator')

        self.create_layout()

    def create_layout(self):

        self.tab1 = pn.Column(monitor_cstatus_main, sizing_mode="stretch_both")
        self.tab2 = pn.Column(monitor_anl_main,     sizing_mode="stretch_both")
        self.tab3 = pn.Column(monitor_mass_main,    sizing_mode="stretch_both")   
        self.tab4 = pn.Column(monitor_jo_main(),    sizing_mode="stretch_both")
        self.tab5 = pn.Column(monitor_rdiag_main,   sizing_mode="stretch_both")
        self.tab6 = pn.Column(monitor_berror_main,  sizing_mode="stretch_both")
        self.tab7 = pn.Column(monitor_objeval_main, sizing_mode="stretch_both")
        self.tab8 = pn.Column(monitor_armobs_main,  sizing_mode="stretch_both")   
        self.tab9 = pn.Column(monitor_logs_main,    sizing_mode="stretch_both")
        self.tab10 = pn.Column(monitor_about_main,  sizing_mode="stretch_both")
                
        # Conteúdo da aplicação
        tabs = pn.Tabs(dynamic=True, active=0)
        tabs.append(("◾CURRENT STATUS",        self.tab1))
        tabs.append(("◾ANALYSIS PLOTS",        self.tab2))
        tabs.append(("◾MASS CONSTRAINS PLOTS", self.tab3))
        tabs.append(("◾MINIMIZATION PLOTS",    self.tab4))
        tabs.append(("◾ANALYSIS DIAG",         self.tab5))
        tabs.append(("◾B ERROR COVARIANCE",    self.tab6))
        tabs.append(("◾OBJ EVALUATION",        self.tab7))
        tabs.append(("◾OBS STORAGE",           self.tab8))
        tabs.append(("◾FULL LOGS",             self.tab9))
        tabs.append(("◾ABOUT",                 self.tab10))

        # Layout da barra lateral
        sidebar_info    = pn.Column(monitor_info_sidebar_logoinpe,                          monitor_info_sidebar_logocptec)
        sidebar_anl     = pn.Column(monitor_anl_sidebar,     self.modal_about_anl(),        monitor_info_sidebar_logocptec)
        sidebar_mass    = pn.Column(monitor_mass_sidebar,    self.modal_about_mass(),       monitor_info_sidebar_logocptec)
        sidebar_jo      = pn.Column(monitor_jo_sidebar(),    self.modal_about_jo(),         monitor_info_sidebar_logocptec)
        sidebar_rdiag   = pn.Column(monitor_rdiag_sidebar,   self.modal_about_rdiag(),      monitor_info_sidebar_logocptec)
        sidebar_berror  = pn.Column(monitor_berror_sidebar,  self.modal_about_berror(),     monitor_info_sidebar_logocptec)
        sidebar_objeval = pn.Column(monitor_objeval_sidebar, self.modal_about_objeval(),    monitor_info_sidebar_logocptec)
        sidebar_armobs  = pn.Column(monitor_armobs_sidebar,  self.modal_about_obsstorage(), monitor_info_sidebar_logocptec)
        sidebar_logs    = pn.Column(monitor_logs_sidebar,    self.modal_about_logs(),       monitor_info_sidebar_logocptec)
        sidebar_about   = pn.Column(monitor_info_sidebar_logoinpe,                          monitor_info_sidebar_logocptec)
        
        col = pn.Column(sidebar_info)
        
        @pn.depends(tabs.param.active, watch=True)
        def insert_widget(active_tab):
            if active_tab == 0:
                col[0] = sidebar_info
            elif active_tab == 1: 
                col[0] = sidebar_anl
            elif active_tab == 2: 
                col[0] = sidebar_mass
            elif active_tab == 3:
                col[0] = sidebar_jo
            elif active_tab == 4:
                col[0] = sidebar_rdiag                  
            elif active_tab == 5:
                col[0] = sidebar_berror
            elif active_tab == 6:
                col[0] = sidebar_objeval                
            elif active_tab == 7:
                col[0] = sidebar_armobs
            elif active_tab == 8:
                col[0] = sidebar_logs
            elif active_tab == 9:
                col[0] = sidebar_about

        placeholder = pn.Column(height=0, width=0) 

        self.app = pn.template.BootstrapTemplate(
            title="SMNA Monitoring App 📊",
            meta_description="SMNA Monitoring App",
            meta_keywords="python, dashboard, gridpoint-statistical-interpolation",
            meta_author="CPTEC-INPE",
#            meta_refresh="10",
#            site_url="https://gad-dimnt-cptec.github.io/SMNAMonitoringApp/monitor.html",
#            sidebar_footer="CPTEC-INPE, 2025.",
        )
    
        self.app.main.append(tabs)
        self.app.main.append(monitor_float_panel)
        #self.app.main.append(monitor_warning_bottom_main)
        self.app.main.append(placeholder)
        self.app.sidebar.append(col)
        self.app.sidebar.append(pn.Row(pn.layout.HSpacer(), '##### CPTEC-INPE, 2025.', pn.layout.HSpacer()))
        self.app.modal.append(pn.Column())
        self.app.sidebar.append(pn.layout.Divider())
        self.app.sidebar.append(self.modal_geninfo())
        self.app.sidebar.append(self.modal_help())
#
    def modal_about_logs(self):
        text_logs_txt = """
        # Full Logs

        The SMNA logs encompasses the logs from the atmospheric model (the pre-processing of boundary conditions, the model itself and post-processing of analyses and forecasts), the observation processing and the assimilation system (GSI).

        These full logs can be useful to check the system for error and or inspect the system behaviour much more close to the code level.

        ## What to check?

        * In the `GSI` logs check for the keyword `PROGRAM GSI_ANL HAS ENDED`.
        * In the `PRE` logs check for the keyword `PRE execution ends`.
        * In the `MODEL` logs check for the keyword `MODEL EXECUTION ENDS NORMALY`.
        * In the `POST` logs check for the keyword `THE FILE LIST WAS FINALIZED`.

        **Note:** The `POST` runs only at 00Z. You should see an error message for the other synopitc times.

        ---

        ##### CPTEC-INPE, 2025.
        """
        self.modal_btn = pn.widgets.Button(name='📊 About', button_type='success')
        self.text_about_logs = pn.Column(text_logs_txt)
        self.modal_btn.on_click(self.show_modal_about_logs)
        return pn.Column(self.modal_btn)

    def show_modal_about_logs(self, event):
        self.app.modal[0].clear()
        self.app.modal[0].append(self.text_about_logs)
        self.app.open_modal()
#
    def modal_about_jo(self):
        text_jo_txt = """
        # Minimization Plots

        The following information obtained from the GSI log file is addressed:
        
        ```
        Begin Jo table outer loop
            Observation Type           Nobs                        Jo        Jo/n
        surface pressure             101588    3.6963295810242533E+04       0.364
        temperature                   54009    8.4362268122117763E+04       1.562
        wind                         174592    2.2575676441332555E+05       1.293
        moisture                      21242    9.4984707783307513E+03       0.447
        gps                          280594    5.4391758277321467E+05       1.938
        radiance                     171806    1.8338082096514766E+05       1.067
                                       Nobs                        Jo        Jo/n
                   Jo Global         803831    1.0838792028623789E+06       1.348
        End Jo table outer loop
        ```
        
        Depending on the number of outer and inner loops, GSI records different information about the number of observations considered (`Nobs`), the cost of minimizing the observational term (`Jo`), and the cost of minimizing the observational term normalized by the number of observations (`Jo/n`). The configuration of GSI/3DVar applied to SMNA (valid for the date of writing this notebook) considers `miter=2` and `niter=3`, i.e., 2 outer loops with 3 inner loops each. For the considered experiments, each inner loop (`niter`) is performed with 0, 50, and 100 iterations, respectively. In this sense, the information obtained from the iterations of the observational term minimization process considers the following:
        
        * OMF: beginning of the first outer loop, where the system state is given by the background;
        * OMF (1st INNER LOOP): end of the first inner loop of the first outer loop, where the system state is still given by the background;
        * OMF (2nd INNER LOOP): end of the second inner loop of the first outer loop, where the system state is still given by the background;
        * OMA (AFTER 1st OUTER LOOP): beginning of the second outer loop, where the system state is given by the analysis;
        * OMA (1st INNER LOOP): end of the first inner loop of the second outer loop, where the system state is given by the analysis;
        * OMA (2nd INNER LOOP): end of the second inner loop of the second outer loop, where the system state is given by the analysis;
        * OMA (AFTER 2nd OUTER LOOP): end of the second outer loop, final analysis.
        
        **Note:** The information from the iterations `OMF` and `OMF (1st INNER LOOP)` is the same, as well as the information from the iterations `OMA (AFTER 1st OUTER LOOP)` and `OMA (1st INNER LOOP)`.
        
        The information from the GSI log is organized into a dataframe with date markings and the inclusion of information about outer and inner loops:
        
        ```
             Date                Observation Type Nobs   Jo            Jo/n  Iter
           0 2023-02-16 06:00:00 surface pressure 104308 32537.652151  0.312 OMF
           1 2023-02-16 06:00:00 temperature      25065  9857.265337   0.393 OMF
           2 2023-02-16 06:00:00 wind             127888 61267.072233  0.479 OMF
           3 2023-02-16 06:00:00 moisture         8705   2103.832442   0.242 OMF
           4 2023-02-16 06:00:00 gps              291665 600962.196931 2.060 OMF
         ...                 ...              ...    ...           ...   ... ...
        5399 2023-03-16 00:00:00 wind             203048 129312.187759 0.637 OMA (AFTER 2nd OUTER LOOP)
        5400 2023-03-16 00:00:00 moisture         22219  4948.997007   0.223 OMA (AFTER 2nd OUTER LOOP)
        5401 2023-03-16 00:00:00 gps              264466 392890.280946 1.486 OMA (AFTER 2nd OUTER LOOP)
        5402 2023-03-16 00:00:00 radiance         183884 56169.185410  0.305 OMA (AFTER 2nd OUTER LOOP)
        5403 2023-03-16 00:00:00 Jo
        
         Global        832986 645663.456547 0.775 OMA (AFTER 2nd OUTER LOOP)
        ```
        
        ---

        ##### CPTEC-INPE, 2025.
        """
        self.modal_btn = pn.widgets.Button(name='📊 About', button_type='success')
        self.text_about_jo = pn.Column(text_jo_txt)
        self.modal_btn.on_click(self.show_modal_about_jo)
        return pn.Column(self.modal_btn)

    def show_modal_about_jo(self, event):
        self.app.modal[0].clear()
        self.app.modal[0].append(self.text_about_jo)
        self.app.open_modal()
#
    def modal_about_mass(self):
        text_mass_txt = """
        # Mass Constrains Plots

        ## What to check?

        In the plots for the mass constrains, you should check wether or not the curves are within the range denoted by the blue dotted curves.

        ---

        ##### CPTEC-INPE, 2025.
        """
        self.modal_btn = pn.widgets.Button(name='📊 About', button_type='success')
        self.text_about_mass = pn.Column(text_mass_txt)
        self.modal_btn.on_click(self.show_modal_about_mass)
        return pn.Column(self.modal_btn)

    def show_modal_about_mass(self, event):
        self.app.modal[0].clear()
        self.app.modal[0].append(self.text_about_mass)
        self.app.open_modal()
#
    def modal_about_berror(self):
        text_berror_txt = """
        # Background Error Covariance

        ## What to check?

        The background error covariance plots show the spatial distribution of the balance projection matrices, standard deviations, horizontal and vertical length scales.
        
        **Note:** Since the SMNA minimizes a 3DVar cost function, the plots shown will not vary with time.

        ---

        ##### CPTEC-INPE, 2025.
        """
        self.modal_btn = pn.widgets.Button(name='📊 About', button_type='success')
        self.text_about_berror = pn.Column(text_berror_txt)
        self.modal_btn.on_click(self.show_modal_about_berror)
        return pn.Column(self.modal_btn)

    def show_modal_about_berror(self, event):
        self.app.modal[0].clear()
        self.app.modal[0].append(self.text_about_berror)
        self.app.open_modal()
#
    def modal_about_objeval(self):
        text_objeval_txt = """
        # Objective Analysis

        ## What to check?

        In the plots show, check for the analysis and forecasts bias, root mean square errors and anomaly correlation. You can also check the scorecard with a summary of these statistics or check the spatial distribution it.

        **Note:** You can also change the climatology used in the calculation of the anomaly correlation.

        ---

        ##### CPTEC-INPE, 2025.
        """
        self.modal_btn = pn.widgets.Button(name='📊 About', button_type='success')
        self.text_about_objeval = pn.Column(text_objeval_txt)
        self.modal_btn.on_click(self.show_modal_about_objeval)
        return pn.Column(self.modal_btn)

    def show_modal_about_objeval(self, event):
        self.app.modal[0].clear()
        self.app.modal[0].append(self.text_about_objeval)
        self.app.open_modal()
#
    def modal_about_obsstorage(self):
        text_obsstorage_txt = """
        # Observation Storage

        ## What to check?

        Check for the sizes of the different data types used in the assimilation process and the total amount of space used.

        ---

        ##### CPTEC-INPE, 2025.
        """
        self.modal_btn = pn.widgets.Button(name='📊 About', button_type='success')
        self.text_about_obsstorage = pn.Column(text_obsstorage_txt)
        self.modal_btn.on_click(self.show_modal_about_obsstorage)
        return pn.Column(self.modal_btn)

    def show_modal_about_obsstorage(self, event):
        self.app.modal[0].clear()
        self.app.modal[0].append(self.text_about_obsstorage)
        self.app.open_modal()
#
    def modal_about_anl(self):
        text_anl_txt = """
        # Analysis Plots

        The analysis plots show the analysis fields as they are generated by the assimilation system. The goal is to provide a first glance at the system output and check for inconsystencies.

        The user can set the parameters on the left to update the plot, by choosing the abalysis variables, levels, region of interest and date. Use the widgets to zoom in and out, pan the field and save an image.

        The analysis plots always will provide information for the last week and is updated once a day.

        ## What to check?
        
        With the analysis plots, you can take a first look at the SMNA analysis and background. The analysis is the result of updating the background by making use of the observations. You can also plot the differences between the analysis and the background and check which parts of the globe where updated the most.

        **Note:** The vertical levels are given in sigma layers.

        ---

        ##### CPTEC-INPE, 2025.
        """
        self.modal_btn = pn.widgets.Button(name='📊 About', button_type='success')
        self.text_about_anl = pn.Column(text_anl_txt)
        self.modal_btn.on_click(self.show_modal_about_anl)
        return pn.Column(self.modal_btn)

    def show_modal_about_anl(self, event):
        self.app.modal[0].clear()
        self.app.modal[0].append(self.text_about_anl)
        self.app.open_modal()
#
    def modal_help(self):
        text_help_txt = """
        # Help

        The dashboard is organized in tabs showing different aspects from the data assimilation system. Basic information on each application is provided through buttons on the sidebar.
        
        To use the dashboard, click on the tabs to select between the analysis fields, mass contrains and minimization plots or to check the data assimilation system full logs. Depending on the selection, the user will be given some parameter to ajust and update the information shown.

        ---

        ##### CPTEC-INPE, 2025.
        """
        self.modal_btn = pn.widgets.Button(name='🛟 Help', button_type='primary')
        self.text_help = pn.Column(text_help_txt)
        self.modal_btn.on_click(self.show_modal_help)
        return pn.Column(self.modal_btn)

    def show_modal_help(self, event):
        self.app.modal[0].clear()
        self.app.modal[0].append(self.text_help)
        self.app.open_modal()
#
    def modal_geninfo(self):
        text_geninfo_txt = """
        # General Info
        
        This is the **SMNA Monitoring App** - a Python Dashboard based on Panel developed to monitor the status of the global operational data assimilation system from the **Center for Weather Forecasts and Climate Studies ([CPTEC](https://www.cptec.inpe.br))**, a center from the **National Institute for Space Research ([INPE](https://www.gov.br/inpe/))** in Brazil.
        
        This dashboard is hosted at GitHub pages and data are loaded from different sources. 
        
        This dashboard is build with the Python [Panel](https://panel.holoviz.org/index.html) library. Altought it isn't a typical dashboard (an actual dashboard allows for cross-referencing information and gaining insights about the displayed data), the library has proven to be a perfect fit for our purpouses.

        Besides the Panel library, all data are displayed with the help of [Intake](https://intake-xarray.readthedocs.io/en/latest/), [Zarr](https://zarr.readthedocs.io/en/stable/), [Xarray](https://xarray.dev/), [Matplotlib](https://matplotlib.org/) and [Pandas](https://pandas.pydata.org/) libraries. We greatly appreciate the effort from developers out there that enables us to make apps that powers our work.

        The SMNA Monitoring App is also partially powered by the [readDiag](https://github.com/GAD-DIMNT-CPTEC/readDiag), [GSIBerror](https://github.com/GAD-DIMNT-CPTEC/GSIBerror), [SCANTEC](https://github.com/GAD-DIMNT-CPTEC/SCANTEC) and [SCANPLOT](https://github.com/GAD-DIMNT-CPTEC/SCANPLOT) projects all developed by the CPTEC staff in the [GAD-DIMNT-CPTEC](https://github.com/GAD-DIMNT-CPTEC) and [GAM-DIMNT-CPTEC](https://github.com/GAM-DIMNT-CPTEC) organizations.

        If you find this content interesting, please drop us a line at the [discussion page in the SMNA Monitoring App repository](https://github.com/GAD-DIMNT-CPTEC/SMNAMonitoringApp/discussions).

        ---

        ##### CPTEC-INPE, 2025.
        """
        self.modal_btn = pn.widgets.Button(name='📖 General Info', button_type='primary')
        self.text_geninfo = pn.Column(text_geninfo_txt)
        self.modal_btn.on_click(self.show_modal_geninfo)
        return pn.Column(self.modal_btn)

    def show_modal_geninfo(self, event):
        self.app.modal[0].clear()
        self.app.modal[0].append(self.text_geninfo)
        self.app.open_modal()
#
    def modal_about_rdiag(self):
        text_rdiag_txt = """
        # Analysis Diagnostics

        ## What to check?

        In the plots show you can check for the counting of observations by type (kx) and level, or check how the observations are distributed spatially. Use the controls on the plots to zoom in and out and pan.

        ---

        ##### CPTEC-INPE, 2025.
        """
        self.modal_btn = pn.widgets.Button(name='📊 About', button_type='success')
        self.text_about_rdiag = pn.Column(text_rdiag_txt)
        self.modal_btn.on_click(self.show_modal_about_rdiag)
        return pn.Column(self.modal_btn)

    def show_modal_about_rdiag(self, event):
        self.app.modal[0].clear()
        self.app.modal[0].append(self.text_about_rdiag)
        self.app.open_modal()
#
    def run(self):
        self.app.servable()

monitoring_app = MonitoringApp()
monitoring_app.run()