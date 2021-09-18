import argparse
import configparser
import logging
from logging import debug, info, error, warning, critical
import os
import sys

from systemd.journal import JournalHandler

logger = logging.getLogger()


def parse_arguments(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-level', metavar="LEVEL", type=str, help="Log level", default=None)
    parser.add_argument('--config', metavar="FILE", type=str, help='Config file.')
    parser.add_argument('--log-systemd', action='store_true', help='Activate systemd integration for the logger.')
    parser.add_argument('rest_args', metavar="ARGS", nargs='*')
    ns = parser.parse_args(args)
    return vars(ns)


def parse_configfile(config_file):
    cfg = configparser.ConfigParser()
    with open(config_file, 'r') as f:
        cfg.read_file(f)
    return cfg


def set_logger_level(log_level):
    logger.setLevel(getattr(logging, log_level))


def set_logger_handler(log_systemd):
    if log_systemd:
        hdl = JournalHandler()
        formatter = logging.Formatter("%(levelname)8s - %(name)s - %(message)s")
    else:
        hdl = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)8s - %(name)s - %(message)s")
    hdl.setFormatter(formatter)
    logger.addHandler(hdl)



class Configuration:
    DEFAULT_CONFIG_FILE_PATH = "~/.rtorrent_low_space_driver.cf"

    def __init__(self, args):
        self.arguments = parse_arguments(args)
        set_logger_handler(self.arguments.get('log_systemd'))
        try:
            self._config_file_path = self.arguments.get('config') or self.DEFAULT_CONFIG_FILE_PATH
            self.configs = parse_configfile(os.path.expanduser(self._config_file_path))
        except FileNotFoundError:
            critical('Config file not found! Exiting.')
            sys.exit(1)

        set_logger_level(self.arguments.get('log_level') or self.configs.get('main', 'log_level', fallback='INFO'))
