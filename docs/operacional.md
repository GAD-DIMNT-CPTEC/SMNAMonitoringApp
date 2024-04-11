# Operacional

O SMNAMonitoringApp possui um conjunto de scripts que são responsáveis pelo download e processamento dos dados antes de serem apresentados na interface. Quando o usuário visualiza os dados na interface, ele está vendo os dados que já foram processados e armazenados em um servidor de dados. Dessa forma, a cada novo ciclo de assimilação de dados, estes script são executados para atualizar os dados a serem apresentados na interface. Para a interface, são fornecidos sempre os últimos 7 dias (ou 28 ciclos) de dados que incluem, análise, background (previsão de curto prazo), logs das simulações (pré-processamento do modelo, modelo, pós-processamento do modelo e sistema de assimilação de dados), além de dados com os diagnósticos da assimilação de dados e a contabilização do uso do disco pelas observações.

## Processamento dos dados da Tabela de Status

O processamento dos dados da tabela de status utiliza o seguinte algorítmo:

1. Verificação de quantas vezes cada componente do sistema foi realizada (conta quantos arquivos de log foram gerados);
2. Atribuição dos emojis para cada situação (e.g., ✅  GOOD, ⚙ WAIT FINISH, ⚠ CHECK LOGS e 🕓 WAIT START);
3. Em determinadas situações, quando um número de realizações for maior do que o necessário, um link para o último log é fornecido;
4. Escrita do arquivo `CSV` final.

## Processamento dos dados de Análise e Previsão

O processamento dos dados de análise e previsão utiliza o seguinte algorítmo:

1. Download dos dados binários de análise e previsão de 6 horas;
2. Leitura dos dados a partir do software pyBAM e escrita no formato Zarr;
3. Atualização do arquivo de catálogo que o SMNAMonitoringApp utilizará para acessar os dados.

O software pyBAM foi escrito para acessar e fornecer estruturas de dados adequadas com o Xarray para a visualização com o matplotlib. No contexto do SMNAMonitoringApp, é utilizado apenas para preparar os dados e convetê-los para o formato Zarr (o que é feito com a biblioteca Zarr do Python). Na interface, é utilizada a biblioteca Intake para ler o catálogo de dados. Como o volume de dados é relativamente grande para o tráfego pela internet (entre o servidor de dados e o navegador do usuário), utiliza-se a biblioteca Dask para adicionar uma camada de processamento paralelo (i.e., todos os núcleos do processador da máquina do usuário são utilizados).

A seguir, um exemplo de como os dados de análise são acessados pelo SMNAMonitoringApp:

```python linenums="1"
import intake
...
catalog_anl = intake.open_catalog('http://ftp1.cptec.inpe.br/pesquisa/das/carlos.bastarz/SMNAMonitoringApp/anls/catalog_anl.yml')
...
def loadData(lfname):
    canl = catalog_anl[lfname].to_dask()
    return canl
```

No exemplo acima, a função `loadData` recebe como argumento a variável `lfname` a qual é utilizada como o nome da fonte de dados a ser acessada no catálogo. O ajuste desta variável é feito através da widget de nome `date` (`date = pn.widgets.Select(name='Date', value=date_range[0], options=date_range)`) no script `monitor_anl.py` na interface do SMNAMonitoringApp.

A seguir, um exemplo de fonte de dados do catálogo `catalog_anl.yml`:

```yaml linenums="1"
sources:

  '2024040412':
    args:
      consolidated: true
      urlpath: https://s0.cptec.inpe.br/pesquisa/das/dist/carlos.bastarz/SMNAMonitoringApp/anls/2024040412/GFCTCPT20240404122024040412F.icn.TQ0299L064.zarr
    description: SMNA Analysis for 2024040412
    driver: intake_xarray.xzarr.ZarrSource
    metadata: 
      catalog_dir: https://s0.cptec.inpe.br/pesquisa/das/dist/carlos.bastarz/SMNAMonitoringApp/anls/2024040412
      tags:
        - atmosphere
        - analysis
        - data_assimilation
        - smna
        - field
      url: https://s0.cptec.inpe.br/pesquisa/das/dist/carlos.bastarz/SMNAMonitoringApp/anls/2024040412
...
```

## Processamento dos dados do Constrain de Massa

O processamento dos dados de contrain de massa utiliza o seguinte algorítmo:

1. Download do arquivo com o banco de dados com os dados do constrain de massa armazenados;
2. Utilização do Sqlite3 para abrir o arquivo de banco de dados e recuperar as informações.

## Processamento dos dados de Minimização da Função Custo

O processamento dos dados de minimização da função custo utiliza o seguinte algorítmo:

1. Download do arquivo de log da última realização do sistema de assimilação de dados;
2. Organização das informações:
  * Quanto aos outer e inner loops;
  * Quanto às variáveis;
  * Quanto ao horário sinótico;
3. Criação de uma tabela com as informações necessárias;
4. Escrita do arquivo `CSV` com as informações.

A seguir, um exemplo de como os dados de minimização da função custo são acessados pelo SMNAMonitoringApp:

```python linenums="1"
import pandas as pd
...
dfs = pd.read_csv('http://ftp1.cptec.inpe.br/pesquisa/das/carlos.bastarz/SMNAMonitoringApp/jo/jo_table_series.csv', header=[0, 1], parse_dates=[('df_preOper', 'Date'), ('df_JGerd', 'Date')])
...
def plotCurves(variable, experiment, synoptic_time, iter_fcost, date_range):
    ...
    df_s = df2.loc[df2['Observation Type'] == variable].loc[df2['Iter'] == iter_fcost].set_index('Date').at_time(str(time_fmt0)).reset_index()    
    ...
    ax_nobs = df_s.hvplot.line(x='Date', y='Nobs', xlabel='Date', ylabel=str('Nobs'), persist=True, rot=90, grid=True, label=str(i), line_width=3, height=height, responsive=True)
    ...
    return ax_nobs
```

## Processamento dos Diagnósticos da Análise

O processamento dos diagnósticos da análise utiliza o seguinte algorítmo:

1. Download dos arquivos de diagnósticos do sistema de assimilação de dados;
2. Leitura dos arquivos de diagnósticos com o readDiag e escrita dos arquivos de diagnósticos (geodataframes) no formato Parquet para cada variável;
3. Atualização dos catálogos que o SMNAMonitoringApp utilizará para acessar os dados.

O software readDiag foi escrito com o objetivo de facilitar o acesso aos arquivos de diagnóstico do sistema de assimilação de dados, fornecendo estruturas de dados adequados para a sua visualização.

A seguir um exemplo de como o SMNAMonitoringApp acessa o catálogo com os dados de diagnósticos:

```python linenums="1"
import intake
...
catalog_diag_conv_01 = intake.open_catalog('http://ftp1.cptec.inpe.br/pesquisa/das/carlos.bastarz/SMNAMonitoringApp/rdiag/catalog_diag_conv_01.yml')
...
def loadData(lfname):
    ax = catalog_diag_conv_01[lfname].read()
    return ax
...
```

A seguir, um exemplo do catálogo de dados com os diagnósticos da análise:

```yaml linenums="1"
sources:

  'ps_diag_conv_01_2024032700':
    driver: geoparquet
    args:
      urlpath: https://s0.cptec.inpe.br/pesquisa/das/dist/carlos.bastarz/SMNAMonitoringApp/rdiag/2024032700/ps-diag_conv_01.2024032700.parquet
    description: SMNA PS Conventional Diagnostics (01) for 2024032700
    metadata: 
      catalog_dir: https://s0.cptec.inpe.br/pesquisa/das/dist/carlos.bastarz/SMNAMonitoringApp/rdiag/2024032700
      tags:
        - atmosphere
        - data_assimilation
        - smna
        - observational diagnostic data
      url: https://s0.cptec.inpe.br/pesquisa/das/dist/carlos.bastarz/SMNAMonitoringApp/rdiag/2024032700
...
```

## Processamento das Covariâncias dos Erros de Previsão

O processamento das covariâncias dos erros de previsão é mais simples do que os demais processamentos, visto que a matriz de covariâncias em uso pelo SMNA é estática (i.e., não é atualizada a cada ciclo de previsão). O seu processamento é feito da seguinte forma:

1. Download do arquivo com a matriz de covariâncias;
2. Leitura com o GSIBerror e escrita no formato Zarr;
3. Escrita do arquivo de catálogo com as fontes de dados da matriz de covariâncias.

O software GSIBerror foi escrito para permitir a leitura do arquivo binário da matriz de covariâncias dos erros de previsão em uso pelo sistema de assimilação do SMNA.

Um exemplo da leitura do catálogo de dados da matriz de covariâncias:

```python linenums="1"
import intake
...
catalog_berror = intake.open_catalog('http://ftp1.cptec.inpe.br/pesquisa/das/carlos.bastarz/SMNAMonitoringApp/berror/catalog_berror.yml')
...

```

Um exemplo do catálogo de dados da matriz de covariâncias:

```yaml linenums="1"
sources:

  'balprojs_agvin':
    args:
      consolidated: true
      urlpath: https://s0.cptec.inpe.br/pesquisa/das/dist/carlos.bastarz/SMNAMonitoringApp/berror/smna_berror_balprojs_agvin.zarr
    description: Vertical Projection of the Stream Function over the Vertical Profile of the Balanced Part of Virtual Temperature
    driver: intake_xarray.xzarr.ZarrSource
    metadata:
      catalog_dir: https://s0.cptec.inpe.br/pesquisa/das/dist/carlos.bastarz/SMNAMonitoringApp/berror
      tags:
        - atmosphere
        - ocean
        - analysis
        - data_assimilation
        - smna
        - background error covariance matrix
      url: https://s0.cptec.inpe.br/pesquisa/das/dist/carlos.bastarz/SMNAMonitoringApp/anls/berror
...      
```