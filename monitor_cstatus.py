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
        logs_urls = {
            "XC50": "https://dataserver.cptec.inpe.br/dataserver_dimnt/das/carlos.bastarz/sandbox/SMNAMonitoringApp/cron_scripts/logs/xc50/logs.csv",
            "Egeon": "https://dataserver.cptec.inpe.br/dataserver_dimnt/das/carlos.bastarz/sandbox/SMNAMonitoringApp/cron_scripts/logs/egeon/logs.csv",
        }

        # --- Verifica cada URL antes de ler ---
        def read_logs(name, url):
            try:
                response = requests.head(url, allow_redirects=True, timeout=5)
                if response.status_code >= 400:
                    print(f"❌ [CURRENT STATUS] Logs {name} não encontrados: {url} (status {response.status_code})")
                    return pd.DataFrame()
                print(f"✅ [CURRENT STATUS] Logs {name} acessíveis: {url}")
                return pd.read_csv(url)
            except requests.RequestException as e:
                print(f"⚠️ [CURRENT STATUS] Erro ao acessar logs {name}: {e}")
                return pd.DataFrame()

        df_xc50 = read_logs("XC50", logs_urls["XC50"])
        df_egeon = read_logs("Egeon", logs_urls["Egeon"])

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

        def status_table(df):
            return pn.widgets.Tabulator(df,
                show_index=False,
                disabled=True,
                theme="bootstrap4",
                text_align='center',
                selectable='toggle',
                stylesheets=[stylesheet],
                formatters=link_formatters)

        def csv_download(df, filename):
            def get_csv():
                io_buffer = io.BytesIO()
                df.to_csv(io_buffer, index=False)
                io_buffer.seek(0)
                return io_buffer

            return pn.widgets.FileDownload(
                icon='download',
                callback=get_csv,
                filename=filename,
                button_type='success',
                width=310,
            )

        cs_table1 = status_table(df_xc50)
        cs_table2 = status_table(df_egeon)
        download_xc50 = csv_download(df_xc50, 'current_status_xc50.csv')
        download_egeon = csv_download(df_egeon, 'current_status_egeon.csv')

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

        return pn.Column(
            welcomeText1,
            pn.Tabs(
                ("XC50", pn.Column(cs_table1, download_xc50)),
                ("Egeon", pn.Column(cs_table2, download_egeon)),
                dynamic=True,
            ),
            welcomeText2,
            monitor_warning_bottom_main,
            sizing_mode='stretch_width',
        )
