#!/usr/bin/env python
# coding: utf-8
"""Painel de diagnósticos convencionais do GSI para XC50 e Egeon."""

import intake
import pandas as pd
import panel as pn

from monitor_texts import MonitoringAppTexts

pn.extension()
monitor_app_texts = MonitoringAppTexts()
monitor_warning_bottom_main = monitor_app_texts.warnings()

CATALOG_URLS = {
    'xc50': {
        '01': 'https://dataserver.cptec.inpe.br/dataserver_dimnt/das/carlos.bastarz/sandbox/SMNAMonitoringApp/cron_scripts/rdiag/xc50/catalog_diag_conv_01.yml',
        '03': 'https://dataserver.cptec.inpe.br/dataserver_dimnt/das/carlos.bastarz/sandbox/SMNAMonitoringApp/cron_scripts/rdiag/xc50/catalog_diag_conv_03.yml',
    },
    'egeon': {
        '01': 'https://dataserver.cptec.inpe.br/dataserver_dimnt/das/carlos.bastarz/sandbox/SMNAMonitoringApp/cron_scripts/rdiag/egeon/catalog_diag_conv_01.yml',
        '03': 'https://dataserver.cptec.inpe.br/dataserver_dimnt/das/carlos.bastarz/sandbox/SMNAMonitoringApp/cron_scripts/rdiag/egeon/catalog_diag_conv_03.yml',
    },
}

KX_VALUES = {
    'q': [181, 120, 187, 180, 183],
    'ps': [181, 180, 120, 187, 183],
    't': [181, 180, 120, 187, 183, 130, 126],
    'uv': [257, 258, 281, 280, 253, 243, 254, 220, 287, 221, 284, 230, 244, 259, 252, 242, 250, 210, 229, 224, 282],
    'gps': [42, 269, 5, 44, 43, 3, 754, 752, 755, 753, 751, 750],
}
TILES = ['CartoDark', 'CartoLight', 'EsriImagery', 'EsriNatGeo', 'EsriUSATopo',
         'EsriTerrain', 'EsriStreet', 'EsriReference', 'OSM', 'OpenTopoMap']


class RdiagExperiment:
    """Estado e visualizações de um experimento de diagnósticos."""

    def __init__(self, name, urls):
        self.name = name
        self.key = name.lower()
        self.catalogs = {}
        self.errors = []
        self._data_cache = {}
        for loop, url in urls.items():
            try:
                self.catalogs[loop] = intake.open_catalog(url)
                print(f'✅ [ANALYSIS DIAG] {name} loop {loop}: catálogo acessível')
            except Exception as exc:
                self.errors.append(f'loop {loop}: {exc}')
                print(f'⚠️ [ANALYSIS DIAG] {name} loop {loop}: {exc}')
        self.available = bool(self.catalogs)
        if self.available:
            self.create_widgets()

    def source_names(self, loop=None):
        catalogs = [self.catalogs[loop]] if loop else self.catalogs.values()
        return {source for catalog in catalogs for source in catalog}

    def create_widgets(self):
        source_names = self.source_names()
        variables = sorted({source.split('_', 1)[0] for source in source_names})
        dates = sorted({source.rsplit('_', 1)[-1] for source in source_names if source.rsplit('_', 1)[-1].isdigit()}, reverse=True)
        loops = sorted(self.catalogs)
        self.date = pn.widgets.Select(name='Date', options=dates, value=dates[0], width=235)
        self.loop = pn.widgets.Select(name='Loop', options=loops, value=loops[0], width=230)
        self.variable = pn.widgets.Select(name='Variable', options=variables, value=variables[0], width=230)
        self.kx = pn.widgets.MultiChoice(name='kx', options=[], value=[], solid=False, width=230)
        self.level = pn.widgets.Select(name='Level', options=[1000.0, 900.0, 800.0, 700.0, 600.0, 500.0, 400.0, 300.0, 250.0, 200.0, 150.0, 100.0, 50.0, 0.0], value=1000.0, width=230)
        self.iuse = pn.widgets.Select(name='iuse', options=[-1, 1], value=1, width=230)
        self.tile = pn.widgets.Select(name='Tiles', options=TILES, value='OSM', width=230)
        self.by_level = pn.widgets.Toggle(name='by Level', value=False, button_type='success', width=230)
        self.by_kx = pn.widgets.Toggle(name='by kx', value=False, button_type='success', width=230)
        self._update_kx()
        self.variable.param.watch(lambda event: self._update_kx(), 'value')

    def _update_kx(self):
        options = KX_VALUES.get(self.variable.value, [])
        self.kx.options = options
        self.kx.value = options

    def source_name(self, variable, loop, date):
        return f'{variable}_diag_conv_{loop}_{date}'

    def load_data(self, source_name, loop):
        cache_key = (source_name, loop)
        if cache_key in self._data_cache:
            return self._data_cache[cache_key]
        try:
            source = self.catalogs[loop][source_name]
            # Os catálogos publicados ainda apontam para o diretório legado
            # ``SMNAMonitoringApp/rdiag``. Os Parquets estão publicados sob
            # ``cron_scripts/rdiag`` para ambos os experimentos.
            source.urlpath = source.urlpath.replace(
                '/SMNAMonitoringApp/rdiag/',
                '/SMNAMonitoringApp/cron_scripts/rdiag/',
            )
            result = (source.read(), None)
        except Exception as exc:
            result = (None, str(exc))
        self._data_cache[cache_key] = result
        return result

    def filtered_data(self, variable, kx, level, iuse, date, loop):
        source_name = self.source_name(variable, loop, date)
        data, error = self.load_data(source_name, loop)
        if error:
            return None, f'Não foi possível ler `{source_name}`: {error}'
        frame = data.reset_index() if 'kx' not in data.columns else data.copy()
        if kx:
            frame = frame[frame['kx'].isin(kx)]
        if 'press' in frame:
            frame = frame[frame['press'] == level]
        if 'iuse' in frame:
            frame = frame[frame['iuse'] == iuse]
        return frame, None

    def plot_counts(self, variable, kx, by_level, by_kx, date, loop):
        source_name = self.source_name(variable, loop, date)
        data, error = self.load_data(source_name, loop)
        if error:
            return pn.pane.Alert(f'🛑 {error}', alert_type='danger')
        frame = data.reset_index() if 'kx' not in data.columns else data.copy()
        if kx:
            frame = frame[frame['kx'].isin(kx)]
        if frame.empty:
            return pn.pane.Alert('Nenhuma observação encontrada para a seleção.', alert_type='warning')
        title = f'{variable} | loop {loop} | valid for {date}'
        if by_level:
            result = frame.groupby('press').size().reset_index(name='counts')
            return result.hvplot.bar(x='press', y='counts', rot=45, height=600, responsive=True, ylabel='Number of Observations', title=title)
        if by_kx:
            result = frame.groupby(['press', 'kx']).size().reset_index(name='counts')
            return result.hvplot.barh(y='press', x='counts', by='kx', height=700, responsive=True, ylabel='Pressure (hPa)', title=title).opts(invert_yaxis=True)
        result = frame.groupby('kx').size().reset_index(name='counts')
        return result.hvplot.bar(x='kx', y='counts', rot=45, height=600, responsive=True, ylabel='Number of Observations', title=title)

    def plot_map(self, variable, kx, level, iuse, date, loop, tile):
        frame, error = self.filtered_data(variable, kx, level, iuse, date, loop)
        if error:
            return pn.pane.Alert(f'🛑 {error}', alert_type='danger')
        if frame.empty:
            return pn.pane.Alert('Nenhuma observação encontrada para a seleção.', alert_type='warning')
        if not {'lon', 'lat'}.issubset(frame.columns):
            return pn.pane.Alert('O diagnóstico não contém as colunas geográficas esperadas (`lon`, `lat`).', alert_type='danger')
        return frame.hvplot.points(x='lon', y='lat', geo=True, by='kx', tiles=tile, frame_height=650, responsive=True, title=f'{variable} | kx={kx} | {level} hPa | iuse={iuse} | loop={loop} | {date}')

    def sidebar(self):
        if not self.available:
            return pn.Column(pn.pane.Alert(f'🛑 {self.name}: ' + ('; '.join(self.errors) or 'catálogos indisponíveis'), alert_type='danger'))
        counts = pn.Card(
            pn.Row(self.variable, pn.widgets.TooltipIcon(value='Choose a variable', align='start')),
            pn.Row(self.loop, pn.widgets.TooltipIcon(value='Choose a loop', align='start')),
            pn.Row(self.by_level, pn.widgets.TooltipIcon(value='Group counts by pressure level', align='start')),
            pn.Row(self.by_kx, pn.widgets.TooltipIcon(value='Group counts by kx and pressure', align='start')),
            pn.Row(self.kx, pn.widgets.TooltipIcon(value='Choose one or more kx values', align='start')),
            title='Number of Observations', collapsed=False,
        )
        spatial = pn.Card(
            pn.Row(self.tile, pn.widgets.TooltipIcon(value='Choose a basemap', align='start')),
            pn.Row(self.level, pn.widgets.TooltipIcon(value='Choose a pressure level', align='start')),
            pn.Row(self.iuse, pn.widgets.TooltipIcon(value='1 = used; -1 = not used', align='start')),
            title='Spatial Distribution', collapsed=True,
        )
        return pn.Column(pn.Card(pn.Row(self.date, pn.widgets.TooltipIcon(value='Choose a date', align='start')), counts, spatial, title='Parameters', collapsed=False))

    def main(self):
        if not self.available:
            return pn.pane.Alert(f'🛑 Analysis diagnostics for {self.name} are unavailable.', alert_type='danger')
        counts = pn.bind(self.plot_counts, self.variable, self.kx, self.by_level, self.by_kx, self.date, self.loop)
        spatial = pn.bind(self.plot_map, self.variable, self.kx, self.level, self.iuse, self.date, self.loop, self.tile)
        return pn.Tabs(
            ('NUMBER OF OBSERVATIONS', pn.Column('Number of observations by kx and pressure.', counts)),
            ('SPATIAL DISTRIBUTION', pn.Column('Spatial distribution of observations.', spatial)),
            dynamic=True,
        )


_experiments = {name: RdiagExperiment(name.upper(), urls) for name, urls in CATALOG_URLS.items()}
_order = [name for name in ('xc50', 'egeon') if name in _experiments]
_sidebar = pn.Column()
_tabs = pn.Tabs(dynamic=True)
for name in _order:
    _tabs.append((name.upper() if name == 'xc50' else 'Egeon', _experiments[name].main()))


def _update_sidebar(event=None):
    _sidebar[:] = [_experiments[_order[_tabs.active]].sidebar()]


_tabs.param.watch(_update_sidebar, 'active')
_update_sidebar()


def LayoutSidebarRdiag():
    return _sidebar


def LayoutMainRdiag():
    main_text = pn.Column('''
    # Analysis Diagnostics

    Select an experiment, then use the controls on the left to explore conventional-observation diagnostics.
    ''')
    return pn.Column(main_text, _tabs, monitor_warning_bottom_main, sizing_mode='stretch_both')
