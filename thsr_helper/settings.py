import os

import click
import logging
from rich.logging import RichHandler

logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, tracebacks_suppress=[click])],
)


class Settings:
    def __init__(self):
        self.load_from_env()

    def load_from_env(self):
        self.config_file_path = os.getenv("CONFIG_FILE_PATH", "config.toml")


settings = Settings()
