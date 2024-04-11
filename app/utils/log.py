import logging
from sys import stdout

from loguru import logger


class InterceptHandler(logging.Handler):
    """InterceptHandler class, used to intercept standard logging messages and redirect them to Loguru."""

    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        # Log with logger
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def init_logging():
    """init_logging function, used to initialize the logging configuration."""
    # Intercept standard logging messages and redirect them to Loguru
    intercept_handler = InterceptHandler()

    # Remove every handler associated with the uvicorn logger, to avoid duplicated logs
    loggers = (
        logging.getLogger(name)
        for name in logging.root.manager.loggerDict
        if name.startswith("uvicorn.")
    )

    # Replace every handler associated with the uvicorn logger
    for uvicorn_logger in loggers:
        uvicorn_logger.handlers = [intercept_handler]

    # Replace every handler associated with the root logger
    logging.getLogger().handlers = [intercept_handler]

    # Remove every handler associated with the uvicorn logger
    logging.getLogger("uvicorn").handlers = []

    # Configure Loguru to output logs to stdout and to a file
    logger.configure(handlers=[{"sink": stdout, "level": logging.DEBUG}])
    logger.add("logs/{time:YYYY-MM-DD--HH-mm}.log", rotation="500 MB")
