import structlog
from environs import Env

from nostr_sdk import (
    init_logger,
    LogLevel,
)
from structlog.dev import Column, KeyValueColumnFormatter

env = Env()
env.read_env()

DEFAULT_RELAYS = ["wss://relay.damus.io", "wss://nos.lol"]


class ConsoleRenderer(structlog.dev.ConsoleRenderer):
    event_key = 'log'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        log_level_col = self._columns[1]
        self._columns = [
            self._columns[0],
            log_level_col,
            Column("logger_name", KeyValueColumnFormatter(
                key_style=None,
                value_style=self._styles.timestamp,
                reset_style=self._styles.reset,
                value_repr=str,
            )),
            self._columns[2],
            self._columns[3],
        ]


# Init logger
def init_logging():
    init_logger(LogLevel.DEBUG)

    # Default config only replacing last two processors
    structlog.configure(processors=structlog.get_config()["processors"][:-2] + [
        structlog.processors.TimeStamper(fmt="%Y-%m-%dT%H:%M:%S.%fZ", utc=True),
        ConsoleRenderer()
    ])

