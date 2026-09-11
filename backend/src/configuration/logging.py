import inspect
import logging
import sys
import typing

_PARENT_NAME: str = "pinard.app"


def create_parent_logger(
    name: str = "pinard.app",
    level: int = logging.INFO,
    fmt: str = "%(asctime)s [%(name)s] %(levelname)s %(message)s",
    datefmt: str = "%Y-%m-%d %H:%M:%S",
) -> logging.Logger:
    global _PARENT_NAME
    _PARENT_NAME = name

    logging.basicConfig(level=level, format=fmt, datefmt=datefmt)

    logger = logging.getLogger(name)

    def _handle_uncaught(exc_type, exc_value, exc_tb):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return
        logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_tb))

    sys.excepthook = _handle_uncaught
    return logger


@typing.override
def Logger(child: bool = False, **kwargs) -> logging.Logger:
    if not child:
        return logging.getLogger(_PARENT_NAME)

    caller_module = inspect.stack()[1].frame.f_globals.get("__name__", "unknown")
    return logging.getLogger(f"{_PARENT_NAME}.{caller_module}")
