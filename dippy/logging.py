from typing import Sequence
import dippy
import logging
import pydantic


class LoggingConfigModel(pydantic.BaseModel):
    @pydantic.validator("level", "global_level", pre=True)
    def validate_level(cls, value: str) -> int:
        levels = {
            "*": logging.DEBUG,
            "all": logging.DEBUG,
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warn": logging.WARN,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
        }
        if value.casefold() not in levels:
            raise ValueError(
                f"Invalid logging level: {value}, must be one of {', '.join(levels)}"
            )
        return levels[value.casefold()]

    format: str = "%(asctime)s: %(levelname)-9s %(name)-16s :: %(message)s"
    date_format: str = "%m/%d/%Y %I:%M:%S %p"

    level: int = dippy.config.EnvField(
        env_var="DIPPY_LOG_LEVEL", converter=validate_level, default=logging.WARN,
    )
    global_level: int = dippy.config.EnvField(
        env_var="DIPPY_LOG_GLOBAL_LEVEL",
        converter=validate_level,
        default=logging.WARN,
    )


class Logging:
    config: dippy.config.ConfigFactory[LoggingConfigModel]

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def setup_logger(self, *config_files: str):
        settings = self.config(*config_files, key="logging")
        self.logger.setLevel(settings.level)
        logging.basicConfig(
            format=settings.format,
            datefmt=settings.date_format,
            level=settings.global_level,
        )

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)
