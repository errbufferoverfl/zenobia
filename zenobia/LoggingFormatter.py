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
__application__ = "zenobia"
__scriptname__ = "zenobia"
__maintainer__ = "errbufferoverfl"
__maintainer_email__ = ""
__description__ = ""
__long_description__ = ""
__url__ = ""
__download_url__ = ""
__license__ = "GPLv3"
__version__ = "0.0.0"

import logging

from colored import fg, attr


class FileFormatter(logging.Formatter):
    """
    A custom formatter for logging to a file. This allows us to retain our dumb symbols and colors on the console with
    out having that issue where you write out the color codes and make the logs terrible to read.
    """
    dbg_fmt = "[%(asctime)s][-] %(msg)s"
    info_fmt = "[%(asctime)s][+] %(msg)s"
    war_fmt = "[%(asctime)s][!] %(msg)s"
    err_fmt = "[%(asctime)s][!!] %(msg)s"
    cri_fmt = "[%(asctime)s][!!!] %(msg)s"

    def __init__(self):
        super().__init__(fmt="%(levelno)d: %(msg)s", datefmt=None, style="%")

    def format(self, record):
        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._style._fmt

        # Replace the original format with one customized by logging level
        if record.levelno == logging.DEBUG:
            self._style._fmt = self.dbg_fmt
        elif record.levelno == logging.INFO:
            self._style._fmt = self.info_fmt
        elif record.levelno == logging.WARNING:
            self._style._fmt = self.war_fmt
        elif record.levelno == logging.ERROR:
            self._style._fmt = self.err_fmt
        elif record.levelno == logging.CRITICAL:
            self._style._fmt = self.cri_fmt

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._style._fmt = format_orig

        return result


class ConsoleFormatter(logging.Formatter):
    """
    A custom formatter for logging to the console. This allows us to retain our dumb symbols and colors on the console with
    out having that issue where you write out the color codes and make the logs terrible to read.
    """
    dbg_fmt = f"[{fg(12)}-{attr(0)}] %(msg)s"
    info_fmt = f"[{fg(4)}+{attr(0)}] %(msg)s"
    war_fmt = f"[{fg(226)}!{attr(0)}] %(msg)s"
    err_fmt = f"[{fg(208)}!!{attr(0)}] %(msg)s"
    cri_fmt = f"[{fg(1)}!!!{attr(0)}] %(msg)s"

    def __init__(self):
        super().__init__(fmt="%(levelno)d: %(msg)s", datefmt=None, style="%")

    def format(self, record):
        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._style._fmt

        # Replace the original format with one customized by logging level
        if record.levelno == logging.DEBUG:
            self._style._fmt = self.dbg_fmt
        elif record.levelno == logging.INFO:
            self._style._fmt = self.info_fmt
        elif record.levelno == logging.WARNING:
            self._style._fmt = self.war_fmt
        elif record.levelno == logging.ERROR:
            self._style._fmt = self.err_fmt
        elif record.levelno == logging.CRITICAL:
            self._style._fmt = self.cri_fmt

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._style._fmt = format_orig

        return result
