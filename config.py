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
    parser.add_argument('--log-file', metavar='FILE', type=str, help='Log everything to this file')
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


def set_logger_handlers(log_systemd=None, log_file=None):
    if log_systemd:
        systemdhandler = JournalHandler()
        formatter = logging.Formatter("%(levelname)8s - %(name)s - %(message)s")
        systemdhandler.setFormatter(formatter)
        logger.addHandler(systemdhandler)
    if log_file:
        filehandler = logging.FileHandler(os.path.expanduser(log_file))
        formatter = logging.Formatter("%(asctime)s - %(levelname)8s - %(name)s - %(message)s")
        filehandler.setFormatter(formatter)
        logger.addHandler(filehandler)
    if (not log_systemd) and (not log_file):
        streamhandler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)8s - %(name)s - %(message)s")
        streamhandler.setFormatter(formatter)
        logger.addHandler(streamhandler)



class Configuration:
    DEFAULT_CONFIG_FILE_PATH = "~/.rtorrent_low_space_driver.cf"

    def __init__(self, args):
        self.arguments = parse_arguments(args)
        set_logger_handlers(self.arguments.get('log_systemd'), self.arguments.get('log_file'))
        try:
            self._config_file_path = self.arguments.get('config') or self.DEFAULT_CONFIG_FILE_PATH
            self.configs = parse_configfile(os.path.expanduser(self._config_file_path))
        except FileNotFoundError:
            critical('Config file not found! Exiting.')
            sys.exit(1)

        set_logger_level(self.arguments.get('log_level') or self.configs.get('main', 'log_level', fallback='INFO'))
