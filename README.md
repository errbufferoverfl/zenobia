# Zenobia

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python: 3.8](https://img.shields.io/badge/Python-3.8-blue.svg)](https://www.python.org/downloads/release/python-386/)

> Septimia Zenobia was a third century queen of the Palmyrene Empire in Syria.

Zenobia is a KeePassXC database backup script that can be run, hourly, daily, monthly or yearly using cron.

## Getting Started

### Prerequisites

#### Installing via pipenv

Zenobia has a few dependencies, if you are using `pipenv` these can be installed by running:

```console
pipenv install
```

## Configuring Zenobia

In order to run Zenobia a few things should be configured in the `config.yaml` file found in the root directory.

```yaml
general:
  maximum retrys: 5
  console logging level: 20
  file logging level: 10
devices:
- name:
  uuid:
  backup destination:
```

### General

You can configure the amount of detail you get in your logs, of course if you are using cron this will require
you to mess around a little more than usual, but the feature is there. This should be configured using the 
Python logging numeric values. These are provided below for ease of access:

| Level | Numeric Value |
|-------|:-------------:|
| `CRITICAL` | 50 |
| `ERROR` | 40 |
| `WARNING` | 30 |
| `INFO` | 20 |
| `DEBUG` | 10 |

By default the configuration file comes configured with the console logging level set to `ERROR` where as file logging is
set to `DEBUG`, that way if you experience any issues you should be able to go back and see what happened, and you 
should only get mail from `cron` in cases where the backup was unsuccessful.

Finally, you can define how many times Zenobia should run, should the first backup attempt fail. This is by default set
to 5.

### Devices 

The name of the device is what it appears as when it is mounted on your computer - this could be something like "untitled",
"aaaaaaaaaaaa", "My very secure password vault" - you get the idea!

The UUID can also be defined if you have a number of USB devices named the same thing, or you just prefer using UUIDs.
In the case there is a name conflict it will check if one of these values matches and then continue.

Finally, you will need to configure where you want to save the backups, this could be a Dropbox or another location on your
system. But it should be the absolute file path.

## Running Zenobia

This can be run as a stand-alone script as well as a `crontab`, keep in mind if you run it as a cron tab, because the user
environment normally changes you might experience some 👽 cybernormal 👽 activity.

I install the `crontab` using the following configuration:

```console
# sudo crontab -u yourusername -e

PATH=/usr/bin:/bin:/usr/sbin:/sbin:/Library/Frameworks/Python.framework/Versions/3.6/bin
0 * * * * cd /absolute/path/to/script/directory && python3.8 zenobia.py
```

To backup your password database hourly:

```console
0 * * * * cd /absolute/path/to/script/directory && ./zenobia.py
```

To backup your password database at 12:05:00 AM in August:

```console
5 0 * 8 * cd /absolute/path/to/script/directory && ./zenobia.py
```

To backup your password database at 02:15:00 PM on the first of the month:

```console
15 14 1 * * cd /absolute/path/to/script/directory && ./zenobia.py
```

To backup you password database at 10:00:00 PM every day from Monday through to Friday:

```console
0 22 * * 1-5 cd /absolute/path/to/script/directory && ./zenobia.py
```
## Built With

* [Python 3.8](https://www.python.org/downloads/release/python-386/)
* [psutil](https://pypi.org/project/psutil/) - A cross-platform lib for process and system monitoring in Python.

## Contributing

See the [CONTRIBUTING](CONTRIBUTING.md) file for details.

## Versioning

We use [SemVar](https://semver.org/) a simple major.minor.patch versioning where

* A major version change will make changes that are incompatible with previous versions
* A minor version change will add backwards-compatible functionality or bug-fixes
* A patch version change will add backwards-compatible bug-fixes

## Authors

* errbufferoverfl

## License

This project is licensed under the GNU GPLv3 License - see the [LICENSE](LICENSE.md) file for details.

## Acknowledgements

* To Twitter for linking my tweet when I was upset at computers.
