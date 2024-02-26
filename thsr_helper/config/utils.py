import logging
import os
from typing import Optional

import typer
import tomli
from tomlkit import dump, dumps, table, document, comment

from thsr_helper.settings import settings

logger = logging.getLogger(__name__)


class ConfigManager:
    @classmethod
    def _get_config_path(cls):
        dir = os.path.dirname(os.path.abspath(__file__ + "/.."))
        return os.path.join(dir, settings.config_file_path)

    @classmethod
    def _create_default_config(
        cls, config_file_path: str, options: Optional[dict[str, any]]
    ):
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
        conditions.add("child_ticket_num", condition_params.get("child_ticket_num", 0))
        conditions.add(
            "disabled_ticket_num", condition_params.get("disabled_ticket_num", 0)
        )
        conditions.add("elder_ticket_num", condition_params.get("elder_ticket_num", 0))
        conditions.add(
            "college_ticket_num", condition_params.get("college_ticket_num", 0)
        )
        conditions.add(
            "train_requirement", condition_params.get("train_requirement", "0")
        )
        conditions.add("date", condition_params.get("date", "2024-1-1"))
        conditions.add("thsr_time", condition_params.get("thsr_time", ""))
        conditions.add("time_range", condition_params.get("time_range", []))

        doc["conditions"] = conditions
        with open(config_file_path, mode="wt", encoding="utf-8") as fp:
            dump(doc, fp)

    @classmethod
    def get_config(cls) -> Optional[dict[str, any]]:
        config_file_path = cls._get_config_path()
        try:
            with open(config_file_path, mode="rb") as fp:
                config = tomli.load(fp)
                return config
        except FileNotFoundError as e:
            logger.warning(
                f"[gray37]Failed to get config file: {e}[/]", extra={"markup": True}
            )
            cls._create_default_config(config_file_path, {})
            typer.secho(
                "Create the default config file, remember to update config",
                fg=typer.colors.BRIGHT_YELLOW,
            )
            return None

    @classmethod
    def update_config(cls, options: dict):
        config_file_path = cls._get_config_path()
        try:
            with open(config_file_path, mode="r+b") as fp:
                config = tomli.load(fp)
                for section_name, section_data in options.items():
                    for key, value in section_data.items():
                        if value:
                            config[section_name][key] = value

                fp.seek(0)
                fp.write(dumps(config).encode("utf-8"))
                fp.truncate()
                typer.secho(
                    "Update config file successfully", fg=typer.colors.BRIGHT_BLUE
                )
        except FileNotFoundError as e:
            logger.warning(
                f"[gray37]Failed to get config file: {e}[/]", extra={"markup": True}
            )
            cls._create_default_config(config_file_path, options)
            typer.secho(
                "Create the config file, please check it", fg=typer.colors.BRIGHT_YELLOW
            )
