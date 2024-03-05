"""Log Settings."""

import logging
from enum import Enum

from prettyconf import config

AMBIENT_LOG = config("AMBIENT", default="DEV")

user_str = "Usuário"


class TypeLog(Enum):
    """Types of Log Status."""

    debug = 0
    error = 1
    info = 2
    warning = 3
    critical = 4


class SystemMessages(Enum):
    """Standard messages created for use in the log."""

    not_exists = "{} não existe. method={} route=/v1/{}"
    exists = "{} {} já existe no sistema. method={} route=/v1/{}"
    requested = "{} requisitad{}. method={} route=/v1/{}"
    all_data = "Obtendo todos os dados. method={} route=/v1/{}"
    recorded = "{} {} gravado. method={} route=/v1/{}"
    updated = "{} atualizado. method={} route=/v1/{}"
    blocked = "Usuário {} bloqueado. method={} route=/v1/{}"
    blocked_24_hours = ("Usuário {} bloqueado por 24 horas. "
                        "method={} route=/v1/{}")


class SysLog:
    """Log for monitoring system."""

    def __init__(self, name_call):
        """Class initialization.

        :param name_call: name of log monitoring system
        """
        self.raid_logs = logging.getLogger(name_call)
        self.raid_logs.setLevel(logging.DEBUG)
        if not self.raid_logs.handlers:
            stream_format = logging.Formatter(
                f"SysLog: time=%(asctime)s log_level=%(levelname)s "
                f"ref=pokeservice ambient={AMBIENT_LOG} nivel=3 "
                f"origin=%(name)s "
                f"message=%(message)s",
                datefmt="%d/%m/%Y %H:%M:%S")
            stream = logging.StreamHandler()
            stream.setLevel(logging.DEBUG)
            stream.setLevel(logging.DEBUG)
            stream.setFormatter(stream_format)
            self.raid_logs.addHandler(stream)

    def show_log(self, type_log, msg):
        """Show the logs according to the type of log.

        :param type_log: type of log
        :param msg: message to log
        """
        if type_log == 0:
            self.raid_logs.debug(msg)
        elif type_log == 1:
            self.raid_logs.error(msg)
        elif type_log == 2:
            self.raid_logs.info(msg)
        elif type_log == 3:
            self.raid_logs.warning(msg)
        elif type_log == 4:
            self.raid_logs.critical(msg)
