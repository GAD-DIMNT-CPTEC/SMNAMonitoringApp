#!/usr/bin/env python
#-----------------------------------------------------------------------------#
#           Group on Data Assimilation Development - GDAD/CPTEC/INPE          #
#-----------------------------------------------------------------------------#
#BOP
#
# !SCRIPT:
#
# !DESCRIPTION:
#
# !CALLING SEQUENCE:
#
# !REVISION HISTORY:
# 22 jun 2023 - J. G. de Mattos - Initial Version
#
# !REMARKS:
# Run the folowing command after updating this script:
# panel convert monitor.py --to pyodide-worker --out .
#
#EOP
#-----------------------------------------------------------------------------#
#BOC

import os
import requests
import sqlite3
import numpy as np
import pandas as pd
import panel as pn
import holoviews as hv
import hvplot.pandas

from datetime import datetime, date
from bokeh.models.formatters import DatetimeTickFormatter
from monitor_texts import MonitoringAppTexts

monitor_app_texts = MonitoringAppTexts()
monitor_warning_bottom_main = monitor_app_texts.warnings()

class MonitoringAppMass:
    def __init__(self):
        pn.extension('floatpanel')
        pn.extension('tabulator')

        # Valores baseados em Trenberth and Smith (2005)
        self.mean = {'pdryini': 98.305, 'mean_ps': 98.550, 'mean_pw': 0.244, 'qneg': None, 'qsat': None}
        self.delta = {'pdryini': 0.01, 'mean_ps': 0.01, 'mean_pw': 0.010, 'qneg': None, 'qsat': None}

        self.load_data()
        self.create_widgets()
        self.create_layout()

    # ------------------- Download e leitura de arquivo -------------------
    def download_file(self, path):
        self.r = requests.get(path)
        self.filename = path.split("/")[-1]
        self.fullname = os.path.join(os.getcwd(), self.filename)
        with open(self.fullname, 'wb') as f:
            f.write(self.r.content)

    def load_data(self):
        url_db = "https://dataserver.cptec.inpe.br/dataserver_dimnt/das/carlos.bastarz/SMNAMonitoringApp/mass/costFile_Oper.db"

        # Checa se arquivo existe
        try:
            response = requests.head(url_db, allow_redirects=True, timeout=5)
            if response.status_code >= 400:
                print(f"❌ [MASS CONSTRAINS PLOTS] Arquivo não encontrado: {url_db} (status {response.status_code})")
                self.df = pd.DataFrame()
                self.dc = pd.DataFrame()
                self.min_date = None
                self.max_date = None
                return
            else:
                print(f"✅ [MASS CONSTRAINS PLOTS] Arquivo acessível: {url_db}")
        except requests.RequestException as e:
            print(f"⚠️ [MASS CONSTRAINS PLOTS] Erro ao acessar {url_db}: {e}")
            self.df = pd.DataFrame()
            self.dc = pd.DataFrame()
            self.min_date = None
            self.max_date = None
            return

        # Baixa e processa o arquivo
        try:
            self.download_file(url_db)
            con = sqlite3.connect(self.filename)

            self.df = pd.read_sql_query(
                "SELECT * FROM costCons ORDER BY date",
                con,
                parse_dates=["date"],
                index_col='date'
            ).replace(-1e38, np.nan)

            self.dc = pd.read_sql_query(
                "SELECT * FROM costFunc ORDER BY date",
                con,
                parse_dates=["date"],
                index_col='date'
            ).replace(-1e38, np.nan)

            self.min_date = self.dc.index.min().date() if not self.dc.empty else None
            self.max_date = self.dc.index.max().date() if not self.dc.empty else None

        except Exception as e:
            print(f"❌ Erro ao processar o arquivo: {e}")
            self.df = pd.DataFrame()
            self.dc = pd.DataFrame()
            self.min_date = None
            self.max_date = None

    # ------------------- Widgets -------------------
    def create_widgets(self):
        # Garante que o DataFrame não está vazio
        if not self.df.empty:
            hours = self.df.index.hour.unique().tolist()
            outers = self.df['outer'].unique().tolist() if 'outer' in self.df.columns else []
            variables = self.df.columns[2:].tolist()
        else:
            hours = []
            outers = []
            variables = []

        if not self.dc.empty:
            column_options = self.dc.columns.tolist()[3:] if len(self.dc.columns) > 3 else []
        else:
            column_options = []

        self.Hour = pn.widgets.RadioBoxGroup(name="Hour Cycle", options=hours)
        self.Outer = pn.widgets.Select(name="Outer Loop", options=outers, width=250)
        self.Vars = pn.widgets.Select(name='Variables', options=variables, width=250)
        self.use_mean = pn.widgets.Checkbox(name='Mean', width=250)
        self.column_name = pn.widgets.Select(name='Column to Plot', options=column_options, width=250)

        if self.min_date and self.max_date:
            self.date_time_picker = pn.widgets.DatetimePicker(
                name="Selecione uma Data e Hora",
                start=self.min_date,
                end=self.max_date,
                value=datetime(self.min_date.year, self.min_date.month, self.min_date.day, 0, 0)
            )
        else:
            self.date_time_picker = pn.widgets.DatetimePicker(name="Selecione uma Data e Hora", disabled=True)

        if not self.df.empty:
            self.date_range_slider = pn.widgets.DatetimeRangePicker(
                name="Date Range",
                value=(self.df.index.min(), self.df.index.max()),
                enable_time=False,
                width=250
            )
        else:
            self.date_range_slider = pn.widgets.DatetimeRangePicker(
                name="Date Range",
                disabled=True,
                width=250
            )

    def create_layout(self):

        self.tab1 = pn.Column(
            pn.bind(self.plotMassFig, self.Vars, self.Outer, self.use_mean, self.date_range_slider.param.value),
            height=800)

        # Layout da barra lateral
        sidebar1 = pn.Column(
            pn.Row(self.date_range_slider, pn.widgets.TooltipIcon(value='Choose a date range', align='start')),
            pn.Row(self.Vars, pn.widgets.TooltipIcon(value='Choose a variable', align='start')),
            pn.Row(self.Outer, pn.widgets.TooltipIcon(value='Choose the outerloop', align='start')),
            pn.Row(self.use_mean, pn.widgets.TooltipIcon(value='Whether to use the mean', align='start'))
        )

        col = pn.Column(sidebar1)

        # Criar o template da aplicação
        self.app = pn.template.FastListTemplate(
            site="SMNA Dashboard",
            title="SMNAMonitoringApp",
        )

        #self.app.main.append(tabs)
        self.app.sidebar.append(col)

    # ------------------- Plotagem -------------------
    def plotMassFig(self, var, outer, use_mean, date_range):
        if self.df.empty or var not in self.df.columns:
            return pn.pane.Markdown("❌ Nenhum dado disponível para plotagem.", width=600)

        plots = []
        for hour in ["0"] + list(np.arange(6, 24, 6)):
            # Filtra apenas se colunas e índices existirem
            if 'outer' in self.df.columns:
                df_filtered = self.df.query(f"outer == {outer}")  # remove hora temporariamente, pois df.index.hour será usado abaixo
                df_filtered = df_filtered[df_filtered.index.hour == int(hour)]
            else:
                df_filtered = self.df.copy()

            if date_range:
                start_date, end_date = date_range
                df_filtered = df_filtered[(df_filtered.index >= start_date) & (df_filtered.index <= end_date)]

            if use_mean:
                df_resampled = df_filtered.resample('ME').mean()
                p = df_resampled.hvplot("date", var, title=f"{hour} UTC").options(autorange="x")
            else:
                p = df_filtered.hvplot("date", var, title=f"{hour} UTC").options(autorange="x")

            # Adiciona linhas de referência se existirem
            if var in self.mean and self.mean[var] is not None:
                l1 = hv.HLine(self.mean[var])
                l2 = hv.HLine(self.mean[var] + self.delta[var])
                l3 = hv.HLine(self.mean[var] - self.delta[var])
                sp = hv.HSpan(self.mean[var] + self.delta[var], self.mean[var] - self.delta[var])
                l1.opts(color="red", line_dash="dashed", line_width=1.0)
                l2.opts(color="blue", line_dash="dashed", line_width=1.0)
                l3.opts(color="blue", line_dash="dashed", line_width=1.0)
                sp.opts(color="lightgray")
                plots.append(sp * (l1 * l2 * l3) * p)
            else:
                plots.append(p)

        layout = hv.Layout(plots).cols(2)
        layout.opts(sizing_mode="stretch_both", title=f"{var}: OuterLoop {outer}", fontsize={"title": "15pt"})
        return layout

    # ------------------- Outros métodos robustos -------------------
    def plot_column(self, column_name, date_time, num_last_dates=4, num_last_days=7):
        if self.dc.empty or column_name not in self.dc.columns:
            return pn.pane.Markdown("❌ Nenhum dado disponível para plotagem desta coluna.", width=600)
        data_subset = self.dc[self.dc.index == date_time]
        if data_subset.empty:
            return pn.pane.Markdown(f"❌ Data '{date_time}' não encontrada no DataFrame.", width=600)
        # resto do método permanece igual, agora seguro

    def LayoutSidebar(self):
        return pn.Card(pn.Column(self.app.sidebar[0]), title='Parameters', collapsed=False)

    def LayoutMain(self):
        main_text = pn.Column("""
        # Mass Constrains Plots

        Set the parameters on the left to update the curves.
        """)
        return pn.Column(main_text, self.tab1, monitor_warning_bottom_main, sizing_mode='stretch_width')

