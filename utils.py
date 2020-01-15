import sys
import logging
from typing import Optional, Callable

LOGGING_LEVELS = {
    'info': logging.INFO,
    'debug': logging.DEBUG,
    'warning': logging.WARNING,
    'error': logging.ERROR,
}

__generated_loggers__ = {}


def set_all_loggers(fn: Callable[[logging.Logger], None]):
    for _, logger in __generated_loggers__.items():
        fn(logger)


def generate_logger(name: str = "", level: str = 'info',
                    format: str = '%(filename)s - %(lineno)d - %(message)s') -> logging.Logger:
    try:
        name = name or __file__ + "_logger"
        logger = logging.getLogger(name)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(format))
        logger.addHandler(handler)
        logger.setLevel(LOGGING_LEVELS[level])
        __generated_loggers__[name] = logger
        return logger
    except Exception as e:
        raise Exception(f"Failed to generate logger: {e}")


UTIL_LOGGER = generate_logger('UtilLogger')


def connect_wifi(ssid: str, password: Optional[str] = None) -> bool:
    UTIL_LOGGER.debug(f"connecting to {ssid}")
    if sys.platform == 'linux':
        from wireless import Wireless
        return Wireless().connect(ssid=ssid, password=password)
    elif sys.platform == 'win32' or sys.platform == 'cygwin':
        import winwifi
        return winwifi.WinWiFi.connect(ssid)
    else:
        UTIL_LOGGER.error(f"Can't auto-connect to wifi on {sys.platform}")
        return False
