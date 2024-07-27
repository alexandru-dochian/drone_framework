# Multi Agent Framework

## Supported operating systems

<p align="center">
  <img src="https://assets.ubuntu.com/v1/a7e3c509-Canonical%20Ubuntu.svg" alt="Ubuntu" width="auto" height="50" />  &nbsp;&nbsp;&nbsp;&nbsp;
  &nbsp;&nbsp;&nbsp;
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/640px-Apple_logo_black.svg.png" alt="MacOS" width="auto" height="50" />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="https://upload.wikimedia.org/wikipedia/commons/0/05/Windows_10_Logo.svg" alt="Windows 10" width="auto" height="50" />

</p>

## Recommended tools:

<p align="center">
  <a href="https://www.jetbrains.com/pycharm/download/">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/JetBrains_PyCharm_Product_Icon.svg/640px-JetBrains_PyCharm_Product_Icon.svg.png" alt="PyCharm" width="auto" height="50" />
  </a>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <a href="https://code.visualstudio.com/download">
    <img src="https://code.visualstudio.com/assets/favicon.ico" alt="Visual Studio Code" width="50" height="50" />
  </a>
</p>

## Required dependencies

<p align="center">
  <a href="https://www.python.org/downloads/release/python-3110/">
    <img src="https://www.python.org/static/favicon.ico" alt="Python 3.11" width="50" height="50" />
  </a>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <a href="https://docs.docker.com/get-docker/">
    <img src="https://www.docker.com/favicon.ico" alt="Docker" width="50" height="50" />
  </a>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <a href="https://python-poetry.org/docs/#installation">
    <img src="https://python-poetry.org/images/favicon-origami-32.png" alt="Poetry" width="50" height="50" />
  </a>
</p>

## Installation

```shell
python install.py
```

### Run experiment

#### Start Redis communicator

```shell
docker compose up

```

#### Start experiment

Config files in json format are used to start an experiment. They are stored under `maf/config/` directory.

```bash
# No args => it will automatically use `config/maf/default.json`
python3 main.py 
```

New config `new_config.json` should be added in `maf/config/` directory.

Thus `maf/config/new_config.json` can be used as follows:

```bash
python3 main.py maf/config/new_config.json
```

### On-the-edge deployment of crazyflie drones

![DevelopmentLayer](docs/static-resources/DevelopmentLayer.png)

## LICENCE

This project is released under [AGPLv3](https://www.gnu.org/licenses/agpl-3.0.txt)
and it applies specifically to the [**maf**](maf) package.