# SMNAMonitoringApp

![Under construction](https://upload.wikimedia.org/wikipedia/commons/d/d9/Under_construction_animated.gif)

SMNAMonitoringApp - a Python Dashboard based on Panel developed to monitor the status of the global operational data assimilation system from the Center for Weather Forecasts and Climate Studies (CPTEC).

## Test

First, make sure to have the GNU C and C++ compiler installed. On Debian based distros, install `gcc` and `g++` as such:

```
sudo apt install gcc g++
```

Then, create the correct environment by using the provided `environment.yml` file:

```
conda env create -f environment.yml
conda activate SMNAMonitoringApp
```

**Note:** For Mac OS X users, use the commands:

```
conda create -n SMNAMonitoringApp python==3.12.2
conda activate SMNAMonitoringApp
pip install -e .
```

Finally, run the command:


```
panel serve --show --autoreload monitor.py
```

Or, just use the script:

```
./SMNAMonitoringApp
```

<a href="https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode" target="_blank"><img src="https://mirrors.creativecommons.org/presskit/buttons/88x31/png/by-nc-sa.png" alt="CC-BY-NC-SA" width="100"/></a>

carlos.bastarz@inpe.br (April, 2024).
