# SMNAMonitoringApp

SMNAMonitoringApp - a Python Dashboard based on Panel developed to monitor the status of the global operational data assimilation system from the Center for Weather Forecasts and Climate Studies ([CPTEC](https://www.cptec.inpe.br)), a center from the National Institute for Space Research ([INPE](https://www.gov.br/inpe/)) in Brazil.

## Test

First, create the correct environment by using the provided `environment.yml` file:

```
conda env create -f environment.yml
conda activate SMNAMonitoringApp
```

Then, run the command:


```
panel serve --show --autoreload monitor.py
```

Or, just use the script:

```
./SMNAMonitoringApp
```

carlos.bastarz@inpe.br (April, 2024).
