import requests
import pandas as pd
import panel as pn
import io
from bokeh.models import HTMLTemplateFormatter

from monitor_texts import MonitoringAppTexts

monitor_app_texts = MonitoringAppTexts()
monitor_warning_bottom_main = monitor_app_texts.warnings()

class MonitoringAppCStatus:
    def __init__(self):
        pn.extension('floatpanel')
        pn.extension('tabulator')

    def LogoINPE(self):
        inpe_logo = pn.pane.PNG('img/logo_mcti_vertical_positiva_02.png', width=300)
        #inpe_logo = pn.pane.WebP('img/img_sidebar1.webp', width=300)
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
        self.logs = "https://dataserver.cptec.inpe.br/dataserver_dimnt/das/carlos.bastarz/SMNAMonitoringApp/logs/logs.csv"

        # --- Verifica se a URL existe antes de ler ---
        try:
            response = requests.head(self.logs, allow_redirects=True, timeout=5)
            if response.status_code >= 400:
                print(f"❌ [CURRENT STATUS] Logs não encontrados: {self.logs} (status {response.status_code})")
                df = pd.DataFrame()  # cria um DataFrame vazio
            else:
                print(f"✅ [CURRENT STATUS] Logs acessíveis: {self.logs}")
                df = pd.read_csv(self.logs)
        except requests.RequestException as e:
            print(f"⚠️ [CURRENT STATUS] Erro ao acessar {self.logs}: {e}")
            df = pd.DataFrame()  # cria um DataFrame vazio

        # --- Configuração do Tabulator ---
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
                show_index=False,
                disabled=True,
                theme="bootstrap4",
                text_align='center',
                selectable='toggle',
                stylesheets=[stylesheet],
                formatters=link_formatters)

        def get_csv():
            io_buffer = io.BytesIO()
            df.to_csv(io_buffer, index=False)
            io_buffer.seek(0)
            return io_buffer

        file_download = pn.widgets.FileDownload(
          icon='download',
          callback=get_csv,
          filename='current_status.csv',
          button_type='success',
          width=310
        )

        welcomeText1 = pn.pane.Markdown("""
        # Current Status
        Check the current status from the operational system in the table below.
        """)

        welcomeText2 = pn.pane.Markdown("""
        **Legend:**
        * **A** = Awaiting
        * **C** = Completed
        * **P** = Processing
        """)

        return pn.Column(welcomeText1, cs_table, file_download, welcomeText2, monitor_warning_bottom_main, sizing_mode='stretch_width')
