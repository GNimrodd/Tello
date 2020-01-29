import sys
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from argparse import ArgumentParser, Namespace
from ast import literal_eval
import re
from uuid import uuid4


def revers_dict(d: Dict[Any, Any]) -> Dict[Any, Any]:
    new_dict = {}
    for key, val in d.items():
        if val in new_dict:
            raise ValueError(f"reversing dictionary with duplicate values: {val}")
        new_dict[val] = key
    return new_dict


LOGGING_LEVELS = {
    'info': logging.INFO,
    'debug': logging.DEBUG,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}

LOGGING_LEVELS_REVERSED = revers_dict(LOGGING_LEVELS)


def __logging_level__(level: Union[str, int]) -> int:
    if isinstance(level, str) and level.lower() in LOGGING_LEVELS:
        level = LOGGING_LEVELS[level.lower()]
    if level not in LOGGING_LEVELS_REVERSED:
        raise ValueError(f"Unknown logging level: {level}")
    return level


__default_log_level__ = logging.INFO
__generated_loggers__ = {}


def set_default_logging_level(level: Union[str, int]):
    global __default_log_level__
    __default_log_level__ = __logging_level__(level)


def set_all_loggers(fn: Callable[[logging.Logger], None]):
    for logger in __generated_loggers__.values():
        fn(logger)


def generate_logger(name: str = "", level: Union[str, int] = 'info',
                    format: str = '%(asctime)s - %(filename)s@%(lineno)d: %(message)s') -> logging.Logger:
    logger = __generated_loggers__.get(name, None)
    if logger is not None:
        return logger
    try:
        level = __logging_level__(level) if level else __default_log_level__
        name = name or __file__ + "_logger"
        logger = logging.getLogger(name)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(format))
        logger.addHandler(handler)
        logger.setLevel(level)
        __generated_loggers__[name] = logger
        return logger
    except Exception as e:
        raise Exception(f"Failed to generate logger: {e}")


def logger_mixin(*args, **kwargs):
    name = kwargs.get('name', None)

    class LoggerMixin:
        @property
        def logger(self):
            logger_name = name or self.__class__.__name__ + "_logger"
            return generate_logger(logger_name, *args, **kwargs)

    return LoggerMixin


UTIL_LOGGER = generate_logger('UtilLogger')

GLOBALS = {}


def update_global(key: str, val: Any, override: bool):
    if override or key not in GLOBALS:
        GLOBALS[key] = val


RUN_ID = uuid4()


class CommandLineParser(ArgumentParser, logger_mixin()):
    __DEFINES_PATTERNS__ = re.compile("([\w_][\w_\d]*)(=(.*))?")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, epilog=f"known defines: {list(GLOBALS.keys())}", **kwargs)
        self.add_argument('--verbose', '-v', default=False, const=True, nargs='?', help="set debugging on")
        self.add_argument('--logging_level', type=str, default="info", help="logging level")
        self.add_argument('-D', '--define', default={}, dest='defs', nargs='*', help="define values")
        self.args = Namespace()

    def add_flag(self, name: str, default: bool = False):
        self.add_argument(name, default=default, const=not default, nargs='?')

    @staticmethod
    def set_debug():
        GLOBALS['debug'] = True
        GLOBALS['logging_level'] = 'debug'
        set_default_logging_level('debug')
        set_all_loggers(lambda l: l.setLevel(__default_log_level__))

    @classmethod
    def __set_defines(cls, defines: List[Any]) -> Tuple[str, Any]:
        for d in defines:
            matches = cls.__DEFINES_PATTERNS__.match(d)
            yield matches.group(1), literal_eval(matches.group(3)) if matches.group(3) else True

    @staticmethod
    def __set_env(args):
        GLOBALS['debug'] = args.verbose
        GLOBALS['logging_level'] = args.logging_level.lower()
        for define, value in CommandLineParser.__set_defines(args.defs):
            GLOBALS[define] = value

        if args.verbose:
            CommandLineParser.set_debug()
        else:
            set_default_logging_level(GLOBALS['logging_level'])
            set_all_loggers(lambda l: l.setLevel(__default_log_level__))

    def parse_args(self, *args, **kwargs):
        args = super().parse_args(*args, **kwargs)
        self.args = args
        CommandLineParser.__set_env(args)
        return args


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
