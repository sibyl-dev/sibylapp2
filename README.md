<p align="left">
<img width=15% src="https://dai.lids.mit.edu/wp-content/uploads/2018/06/Logo_DAI_highres.png" alt=“DAI-Lab” />
<i>An open source project from Data to AI Lab at MIT.</i>
</p>

<!-- Uncomment these lines after releasing the package to PyPI for version and downloads badges -->
<!--[![PyPI Shield](https://img.shields.io/pypi/v/pyreal.svg)](https://pypi.python.org/pypi/pyreal) -->
<!--[![Downloads](https://pepy.tech/badge/pyreal)](https://pepy.tech/project/pyreal)-->
<!--[![Travis CI Shield](https://travis-ci.org/DAI-Lab/pyreal.svg?branch=stable)](https://travis-ci.org/DAI-Lab/pyreal)-->
<!--[![Coverage Status](https://codecov.io/gh/DAI-Lab/pyreal/branch/stable/graph/badge.svg)](https://codecov.io/gh/DAI-Lab/pyreal)-->
<!--[![Build Action Status](https://github.com/DAI-Lab/pyreal/workflows/Test%20CI/badge.svg)](https://github.com/DAI-Lab/pyreal/actions)-->
# Sibylapp2

Library for visualizing explanations.

- License: MIT
- Homepage: https://sibyl-ml.dev/

# Overview

**Sibylapp2** generates usable interfaces to interact with ML explanations. The app 
reads RESTful APIs from [sibyl-api](https://github.com/sibyl-dev/sibyl-api)

# Install

## Requirements

**Sibylapp2** has been developed and tested on [Python 3.9, and 3.10](https://www.python.org/downloads/).
The library uses Poetry for package management and runs on Streamlit.

## Install from source
If you do not have **poetry** installed, please head to [poetry installation guide](https://python-poetry.org/docs/#installation)
and install poetry according to the instructions.\
Run the following command to make sure poetry is activated. You may need to close and reopen the terminal.

```
poetry --version
```

Finally, you can clone this repository and install it from
source by running `poetry install`, with the optional `examples` extras if you'd like to run our tutorial scripts.

```
git clone https://github.com/sibyl-dev/sibylapp2.git
cd sibylapp2
poetry install 
```

# Running Sibylapp2

1. First, you will need to head over to the [sibyl-api](https://github.com/sibyl-dev/sibyl-api) repo,
and follow the instructions there to load in your database. You can run your APIs once your 
database in setup from the parent `sibyl-api` folder with:
```bash
poetry run sibyl run -v
```
2. Open `sibylapp2/config.py`, and update `BASE_URL` to the URL your APIs are running on. You can also set 
configurations specific to your application here.
3. From the root project folder, run:
```bash
poetry run streamlit run 1_Explore_a_Prediction.py
```

