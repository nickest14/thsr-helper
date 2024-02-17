import logging
import os
from typing import Optional

import typer
import tomli
from tomlkit import dump, dumps, table, document, comment, nl

from thsr_helper.settings import settings

logger = logging.getLogger(__name__)


class ConfigManager:
    def __init__(self):
        self.config_file_path = self._get_config_path()

    def _get_config_path(self):
        dir = os.path.dirname(os.path.abspath(__file__ + "/.."))
        return os.path.join(dir, settings.config_file_path)

    def _create_default_config(self, options: Optional[dict[str, any]]):
        user_params = options.get("user", {})
        condition_params = options.get("conditions", {})

        doc = document()
        doc.add(comment("This is a TOML document."))

        user = table()
        user.add("personal_id", user_params.get("personal_id", ""))
        user.add("phone_number", user_params.get("phone_number", ""))
        doc.add("user", user)

        conditions = table()
        conditions.add("adult_ticket_num", condition_params.get("adult_ticket_num", 1))
        conditions.add("date", condition_params.get("date", "2024-1-1"))
        conditions.add("thsr_time", condition_params.get("thsr_time", ""))
        conditions.add("time_range", condition_params.get("time_range", []))


        doc["conditions"] = conditions
        with open(self.config_file_path, mode="wt", encoding="utf-8") as fp:
            dump(doc, fp)

    def get_config(self) -> Optional[dict[str, any]]:
        try:
            with open(self.config_file_path, mode="rb") as fp:
                config = tomli.load(fp)
                return config
        except FileNotFoundError as e:
            logger.warning(
                f"[gray37]Failed to open config file: {e}[/]", extra={"markup": True}
            )
            self._create_default_config({})
            typer.secho("Create the default config file, remember to update config", fg=typer.colors.BRIGHT_YELLOW)
            return None

    def update_config(self, options: dict):
        try:
            with open(self.config_file_path, mode="r+b") as fp:
                config = tomli.load(fp)
                for section_name, section_data in options.items():
                    for key, value in section_data.items():
                        if value:
                            config[section_name][key] = value

                fp.seek(0)
                fp.write(dumps(config).encode("utf-8"))
                fp.truncate()
        except FileNotFoundError as e:
            logger.warning(
                f"[gray37]Failed to open config file: {e}[/]", extra={"markup": True}
            )
            self._create_default_config(options)
            typer.secho("Create the config file, please check it", fg=typer.colors.BRIGHT_YELLOW)