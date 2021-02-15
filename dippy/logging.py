import logging


class Logging:
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WORN = logging.WARN
    ERROR = logging.ERROR
    CRITCAL = logging.CRITICAL
    FATAL = logging.FATAL

    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

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

    @classmethod
    def setup_logger(cls, log_level: int = logging.WARN):
        logging.basicConfig(
            # format=self.settings.format,
            # datefmt=self.settings.date_format,
            level=log_level,
        )
