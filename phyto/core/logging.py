import logging
from logging.handlers import RotatingFileHandler
from typing import Any

from typing_extensions import Self


class RemoveNoise(logging.Filter):
    def __init__(self) -> None:
        super().__init__(name="discord.state")

    def filter(self, record) -> bool:
        return (
            record.levelname != "WARNING" or "referencing an unknown" not in record.msg
        )


class SetupLogging:
    def __init__(self, log: logging.Logger) -> None:
        self.logger = log
        self.max_bytes = 32 * 1024

    def __enter__(self: Self) -> Self:
        logging.getLogger("discord.client").setLevel(logging.WARNING)
        logging.getLogger("discord").setLevel(logging.WARNING)
        logging.getLogger("discord.http").setLevel(logging.WARNING)
        logging.getLogger("wavelink.player").setLevel(logging.WARNING)
        logging.getLogger("discord.state").addFilter(RemoveNoise())

        self.logger.setLevel(logging.INFO)
        handler = RotatingFileHandler(
            filename="logs/phyto.log",
            encoding="utf-8",
            mode="w",
            maxBytes=self.max_bytes,
            backupCount=5,
        )
        dt_fmt = "%Y-%m-%d %H:%M:%S"
        fmt = logging.Formatter(
            "[{asctime}] [{levelname:<7}] {name}: {message}", dt_fmt, style="{"
        )
        handler.setFormatter(fmt)
        self.logger.addHandler(handler)

        return self

    def __exit__(self, *args: Any) -> None:
        handlers = self.logger.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            self.logger.removeHandler(hdlr)
