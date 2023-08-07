# AstroSA: Astronomical Observation Scheduler Assessment

This project is an assessment framework for astronomical observation schedulers.

这是一个评价天文观测调度器的框架。

## Usage

Refers to `main.py`

参见：`main.py`

## Requirements

```shell
python -m pip install -r requirements.txt
```

## Install

AstroSA is available in Pypi.

```shell
pip install astrosa
```

Also, you can install from source code.

```shell
git clone https://github/h-xie/astrosa
cd astrosa
pip install .
```

## Data

AstroSA provide a sqlite database in directory `astrosa/data/astrosa.sqlite`.It contains experimental data from the
paper, including a
priority plan, a sequential plan, and corresponding cloud data on the date 2023-06-08 at location JLO.

You can use by

```python
import sqlite3
import astrosa

database = astrosa.DATA_DIR
conn = sqlite3.connect(database + '/astrosa.sqlite')
```

### Catalogue

We also provide a data converter from `VizieR` to `sqlite` in `tyc2_to_sql.ipynb`. You can use it to convert tycho-2
from FITS format to sqlite format. Tycho-2 catalogue can be downloaded via:
[Tycho-2 catalogue in FITS](https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=I/259)

### Cloud

We provide cloud image to score script `cloud_to_data.py`. You can use it to convert cloud image to cloud data. It only
counts NIGHT.

```shell
python cloud_to_data.py -f path_to_your_cloud_image
```