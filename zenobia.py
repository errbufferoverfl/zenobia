#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# zenobia
# Copyright (C) 2018 errbufferoverfl
#
# This file is part of zenobia.
#
# zenobia is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# zenobia is distributed in the hope that it will be useful,  but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with zenobia.  If not,
# see <http://www.gnu.org/licenses/>.
import errno
import logging
import os
import pprint
import shutil
import subprocess
import sys
import time
from os.path import expanduser
from time import strftime, gmtime

import psutil
import ruamel.yaml

from zenobia.LoggingFormatter import ConsoleFormatter, FileFormatter

__application__ = "zenobia"
__scriptname__ = "zenobia"
__maintainer__ = "errbufferoverfl"
__maintainer_email__ = "zenobia@errbufferoverfl.me"
__description__ = "Zenobia is a KeePassXC database backup script that can be run, hourly, daily, monthly or yearly using cron."
__long_description__ = "Zenobia is a KeePassXC database backup script that can be run, hourly, daily, monthly or yearly using cron."
__url__ = "https://github.com/errbufferoverfl/zenobia"
__download_url__ = "https://github.com/errbufferoverfl/zenobia/releases"
__license__ = "GPLv3"
__version__ = "1.0.0"

config_path = os.getcwd() + '/config.yaml'
logger = logging.getLogger("zenobia")


def open_config():
    """
    Opens and processes the configuration file into a Python friendly dictionary.

    Returns:
        ``dict``: a dictionary containing the pased output of the config.yaml file

    Raises:
        If the configuration file is not in the root directory raise a ``FileNotFoundError`` and terminate.

    Example:
        >>> print(open_config())
        {'devices': [{'backup destination': '/Users/errbufferoverfl/secureenclave',
                    'name': 'passwordvault',
                    'uuid': '421F6B67-B129-3A69-94E7-986C10441337'}],
        'general': {'console logging level': 20,
                    'file logging level': None,
                    'maximum retrys': 5}}
    """
    try:
        with open(config_path, 'r') as config_file:
            config = ruamel.yaml.load(config_file, Loader=ruamel.yaml.Loader)
    except FileNotFoundError as fourohfour:
        logger.critical("Config file not found. Terminating.")
        sys.exit(1)
    else:
        return config


def init_logging(stdout_verbosity: int, file_verbosity: int):
    """
    Initialises file and console logging for the application, file logging is set to ``DEBUG`` (10) and console is set to
    the higher ``INFO`` (20).

    Example:
        >>> logger = logging.getLogger("zenobia")

        def main():
            init_logging()

            # will initialise logger to only report CRITICAL problems to the console and report DEBUG information to log files.
            init_logging(50, 10)

    Raises:
        ``OSError`` when a log directory cannot be successfully created.
    """
    log_path = "logs"
    log_name = f"{__scriptname__}-{time.strftime('%Y%m%d%H%M%S')}"
    try:
        os.makedirs(log_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    init_logger = logging.getLogger("zenobia")
    init_logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    fh = logging.FileHandler(f"{log_path}/{log_name}.log")
    fh.setLevel(file_verbosity)

    # create console handler with a higher log level
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(stdout_verbosity)

    # create formatter and add it to the handlers
    con_fmt = ConsoleFormatter()
    file_fmt = FileFormatter()

    # add custom formatters to handlers
    ch.setFormatter(con_fmt)
    fh.setFormatter(file_fmt)

    # add handler to logger object
    init_logger.addHandler(ch)
    init_logger.addHandler(fh)


def run_backup(device_config: dict, partition_details: dict):
    """
    The function that finds the KeePass file on the mount point. It currently doesn't work recursively so it **MUST** be in
    the root of the mount point to work.

    Once a ``kdbx`` file is mount and it is not the ``lock`` file, it splits the name and generates a new file name with
    the current year, month and date and hour, minute and second. That way if you have many backups a day you can distinguish
    between them.

    Bugs:
        There is a know issue when using this with ``crontab`` that the hour, minute and second isn't set correctly.
        However at the moment I believe this is a ``crontab`` environment configuration problem rather than  a script
        problem.

    Args:
        **device_config** (``dict``): Information about the device we are backup up from, this is a ``dict`` entry from
        ``config.yaml``. Contains information about the backup destination.

        **partition_details** (``dict``): Important information captured from ``psutil`` and ``diskutil``. Contains
        information about the mount point we are copying data from.

    Warning:
        A warning is logged if the backup fails.

    Returns:
        ``bool``: ``True`` if the backup process was completed, ``False`` if the backup process did not complete

    """
    backed_up = False

    device_files = os.listdir(partition_details["mount point"])

    if not device_config["backup destination"]:
        device_config["backup destination"] = expanduser("~")
        logger.warning(f"No backup destination set, defaulting to {expanduser('~')}.")

    for file_name in device_files:
        logger.info("Looking for KeePass database.")
        if ".kdbx" in file_name and ".lock" not in file_name:
            split_name = file_name.split('.')
            new_file_name = f"{split_name[0]}-{strftime('%Y%m%d%I%M%S', gmtime())}.{split_name[1]}.bak"
            logger.info(f"Copying {file_name} from {partition_details['mount point']} to {device_config['backup destination']}.")
            shutil.copyfile(f"{partition_details['mount point']}/{file_name}",
                            f"{device_config['backup destination']}/{new_file_name}")
            backed_up = True
            logger.info(f"Successfully backed up {file_name} to {device_config['backup destination']}")
            return backed_up
    logger.warning(f"Unable to backup KeePass file to {device_config['backup destination']} for some unknown reason.")
    return backed_up


def create_partition_dict(disk_partitions: list):
    """
    Creates a new partition dictionary using information gathered from ``psutil`` and ``diskutil`` this includes:
    - ``partition.mountpoint``: e.g. ``/Volumes/mypasswordusb``.
    - ``partition name`` when using diskutil this is actually refered to as the partition node: e.g. ``disk1s1``
    we remove the /dev/ to make it easier to run ``diskutil info partition name``.
    - ``volume uuid``: the one bit of information that ``psutil`` could not provide me, so we use ``diskutil`` instead
    and then we ended up here, having to create our own ``dict`` because we couldn't add it to the original ``device``
    object.

    Args:
        **disk_partitions** (``list``): A list of ``Device`` objects returned from ``psutil``

    Examples:
        >>> pprint.pprint(create_partition_dict(psutil.disk_partitions()))
        [{'mount point': '/',
            'partition name': 'disk1s1',
            'volume uuid': '97E287D4-2D34-450C-907C-8935F5582F2D'},
        {'mount point': '/private/var/vm',
            'partition name': 'disk1s4',
            'volume uuid': 'A3D8E4BC-0312-4ADC-BC16-C02E875CD6A8'},
        {'mount point': '/Volumes/07061737377',
            'partition name': 'disk2s1',
            'volume uuid': '421F6B67-B129-3A69-94E7-986C10441DB1'}]

    Returns:
        ``list`` of dictionaries containing updated (and useful) information about all the devices currently attached
        to the system.

    """
    updated_partitions = list()

    logger.debug("Creating partition dictionary.")
    for partition in disk_partitions:
        partition_name = partition.device.rsplit('/')[2]
        logger.debug(f"Getting {partition_name} information from diskutil.")
        diskutil_subprocess = subprocess.Popen(['diskutil', 'info', partition_name], stdout=subprocess.PIPE)
        diskutil_output_for_logger = diskutil_subprocess.stdout.read().decode("utf-8")
        diskutil_output = diskutil_output_for_logger.split("\n")
        logger.debug("diskutil details:")
        logger.debug(diskutil_output_for_logger)

        volume_uuid = [line.split(":")[1].strip() for line in diskutil_output if "volume uuid" in line.lower()]
        logger.debug(f"Volume UUID: {volume_uuid[0]}.")
        partition_with_uuid = {"partition name": partition_name, "volume uuid": volume_uuid[0],
                               "mount point": partition.mountpoint}
        logger.debug(f"Created new partition dict: {partition_with_uuid}.")
        updated_partitions.append(partition_with_uuid)

    return updated_partitions


def main():
    try:
        console_verbosity = config["general"]["console logging level"]
    except KeyError:
        console_verbosity = logging.INFO
        logger.critical(f"Console logging level has not been defined in {config_path}. Setting logging level to INFO.")

    try:
        file_verbosity = config["general"]["file logging level"]
    except KeyError:
        file_verbosity = logging.DEBUG
        logger.critical(f"File logging level has not been defined in {config_path}. Setting logging level to DEBUG.")

    if not console_verbosity:
        console_verbosity = logging.INFO
        logger.critical(f"Console logging level has not been set in {config_path}. Setting logging level to INFO.")

    if not file_verbosity:
        file_verbosity = logging.DEBUG
        logger.critical(f"Console logging level has not been set in {config_path}. Setting logging level to DEBUG.")

    init_logging(console_verbosity, file_verbosity)

    partitions = create_partition_dict(psutil.disk_partitions())

    logger.info("Iterating over devices in config file.")
    for device in config["devices"]:
        logger.info("Iterating over partitions.")
        for partition in partitions:
            if device["name"] and device["uuid"]:
                logger.debug("Device name and UUID set.")
                if device["name"].lower() in partition["mount point"].lower() and device["uuid"] == partition["volume uuid"]:
                    logger.debug("Device name and partition name match. UUID and volume UUID match.")
                    if not run_backup(device, partition):  # Backup is not successful
                        logger.warning(f"Unable to backup {device['name']} to {device['backup destination']}")
                        for count in range(int(config["general"]["maximum retrys"])):
                            logger.warning(f"Attempt {count} out of {int(config['general']['maximum retrys'])}")
                            if run_backup(device, partition):
                                break

            elif device["name"]:
                logger.debug("Device name set.")
                if device["name"] in partition["mount point"]:
                    logger.debug("Names match.")
                    if not run_backup(device, partition):  # Backup is not successful
                        logger.warning(f"Unable to backup {device['name']} to {device['backup destination']}")
                        for count in range(int(config["general"]["maximum retrys"])):
                            logger.warning(f"Attempt {count} out of {int(config['general']['maximum retrys'])}")
                            if run_backup(device, partition):
                                break

            elif device["uuid"] and partition["uuid"]:
                logger.debug("UUID on device set, partition has UUID.")
                if device["uuid"] == partition["volume uuid"]:
                    logger.debug("UUIDs match.")
                    if not run_backup(device, partition):  # Backup is not successful
                        logger.warning(f"Unable to backup {device['name']} to {device['backup destination']}")
                        for count in range(int(config["general"]["maximum retrys"])):
                            logger.warning(f"Attempt {count} out of {int(config['general']['maximum retrys'])}")
                            if run_backup(device, partition):
                                break

            else:
                logger.critical("Device name and/or UUID has not been specified. Cannot backup.")
                sys.exit(1)


config = open_config()

if __name__ == '__main__':
    main()
