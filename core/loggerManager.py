import logging
import logging.handlers
import os
import time
import colorlog
import threading
from typing import Tuple
from logging import Logger
from core.path import LOG_PATH


class SingletonMeta(type):
    """实现线程安全的单例模式基类，确保日志管理器在多处调用时是同一个实例 """

    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        """
        线程安全地创建实例
        """
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]


class LoggerManager(metaclass=SingletonMeta):
    """日志管理器类，实现了单例模式，确保在整个应用中只有一个日志管理器实例"""

    def __init__(self):
        """初始化LoggerManager实例的属性"""
        self.logger_info = dict()
        self.user_handle = None
        self.default_logger_name = "main"  # 因为pytest串行执行时,只有一个进程线程,脚本执行前后需要注册解注册日志,多线程执行时,线程间独立

    @staticmethod
    def get_log_filename(case_filepath: str) -> Tuple[str, str]:
        """
        获取日志文件路径和UI截图目录路径

        Args:
            case_filepath (str): 用例文件的路径

        Returns:
            Tuple[str, str]: 返回一个包含日志文件路径和UI截图目录路径的元组。
                    - logfile_path (str): 日志文件的绝对路径
                    - ui_screenshot_dir (str): UI截图文件的目录路径
        """
        new_folder_list = []
        py_filename = os.path.split(case_filepath)[1]
        py_filename = py_filename.rsplit(".py")[0]
        current = time.localtime()
        time_suffix = "_%d_%d_%d_%d_%d_%d" % (
            current.tm_year, current.tm_mon, current.tm_mday,
            current.tm_hour, current.tm_min, current.tm_sec
        )
        new_folder_list.append(py_filename)
        filepath = os.path.split(case_filepath)[0]
        cur_folder = ""
        while cur_folder != "cases":
            path_detail = os.path.split(filepath)
            filepath = path_detail[0]
            cur_folder = path_detail[1]
            new_folder_list.append(cur_folder)
        new_folder_list = new_folder_list[::-1]
        t_folder: str = "cases"
        for i in range(1, len(new_folder_list)):
            t_folder = os.path.join(t_folder, new_folder_list[i])
        logfile_dir: str = os.path.join(LOG_PATH, t_folder)
        logfile_name = py_filename + time_suffix + ".log"
        logfile_path = os.path.join(logfile_dir, logfile_name)
        if not os.path.exists(os.path.dirname(logfile_path)):
            os.makedirs(os.path.dirname(logfile_path))
        with open(logfile_path, 'w', encoding='utf-8'):
            pass
        ui_dir = logfile_name.strip(".log")
        ui_screenshot_dir = os.path.join(logfile_dir, ui_dir)
        return logfile_path, ui_screenshot_dir

    def register(self, case_filepath: str, console: bool = True, default_level: int = logging.DEBUG,
                 **kwargs) -> Logger:
        """
        注册一个新的logger实例
        Args:
            case_filepath (str): 用例文件的路径
            console (bool, optional): 是否输出到控制台，默认为True
            default_level (int, optional): 默认的日志级别，默认为DEBUG
            **kwargs: 其他可选参数

        Returns:
            Logger: 返回一个新创建的logger实例
        """
        filename, screenshot_dir = self.get_log_filename(case_filepath)

        # 设置不同级别的日志在终端中显示的颜色
        log_colors_config = {
            'DEBUG': 'white',  # cyan white
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }

        log_format = kwargs.get("format", None)
        if log_format is None:
            log_format = "%(asctime)s %(filename)s::%(module)s::%(funcName)s[%(lineno)d] %(levelname)s: %(message)s"

        # 获取新的logger实例
        logger_name = self.default_logger_name
        logger = logging.getLogger(logger_name)

        """ 
       logger_info[logger_name] = dict(), 其中的key分别表示
       timestamp: 表示创建的时间戳
       filepath: 表示日志存储的路径
       logger: 表示日志器
       thread: 表示所属的线程
       ui_dir: 表示UI截图信息所在的目录
        """
        self.logger_info[logger_name] = dict()
        self.logger_info[logger_name]["timestamp"] = time.localtime()
        self.logger_info[logger_name]["ui_dir"] = screenshot_dir

        # 如果设置了file_size，则默认一个文件大小为10MB
        file_size_limit = kwargs.get("size_limit", 10 * 1024 * 1024)
        file_max = kwargs.get("file_max", 6)
        file_mode = kwargs.get("file_mode", "w")

        file_handler = None
        stream_handler = None

        if filename:
            self.logger_info[logger_name]["filepath"] = os.path.dirname(filename)
            file_handler = logging.handlers.RotatingFileHandler(
                filename=filename,
                maxBytes=file_size_limit,
                backupCount=file_max,
                encoding="utf-8",
                mode=file_mode
            )
            file_handler.setFormatter(logging.Formatter(fmt=log_format))
            file_handler.setLevel(logging.DEBUG)
            self.user_handle = file_handler
            logger.addHandler(self.user_handle)

        if console:
            stream_handler = logging.StreamHandler()
            console_formatter = colorlog.ColoredFormatter(
                fmt='%(log_color)s[%(asctime)s] -> [%(levelname)s] : %(message)s',
                log_colors=log_colors_config
            )
            stream_handler.setFormatter(console_formatter)
            stream_handler.setLevel(default_level)
            logger.addHandler(stream_handler)

        logger.setLevel(logging.DEBUG)  # 设置默认日志打印级别
        self.logger_info[logger_name]["logger"] = logger
        self.logger_info[logger_name]["file_handler"] = file_handler
        self.logger_info[logger_name]["stream_handler"] = stream_handler

        return logger

    def unregister(self, logger_name: str = "main"):
        """
        注销指定的logger实例，并移除相关的句柄
        Args:
            logger_name (str, optional): 要注销的logger名称，默认为"main"
        """
        if logger_name in logging.Logger.manager.loggerDict:
            logging.Logger.manager.loggerDict.pop(logger_name)
            logger = self.get_logger(logger_name="main")
            # 把日志器的句柄移除, 如果不移除, 就会一直打印日志在之前的文件中
            logger.removeHandler(self.logger_info[logger_name]["file_handler"])
            logger.removeHandler(self.logger_info[logger_name]["stream_handler"])
            self.logger_info.pop(logger_name)  # 删除用户的备份信息

    def get_logger(self, logger_name: str = "main") -> Logger:
        """
        获取指定名称的logger实例
        Args:
            logger_name (str, optional): 要获取的logger名称，默认为"main"

        Returns:
            Logger: 返回指定名称的logger实例
        """
        return logging.getLogger(logger_name)


def logger_init(case_filepath: str, default_level: int = logging.INFO, console: bool = True, **kwargs) -> Logger:
    """
    初始化logger并返回其实例
    Args:
        case_filepath (str): 用例文件的路径
        default_level (int): 默认日志输出级别
        console (bool, optional): 是否输出到控制台
    Returns:
        Logger: 返回初始化后的logger实例
    """
    logger_mgt = LoggerManager()
    logger = logger_mgt.register(case_filepath, console, default_level, **kwargs)
    return logger


def get_logger() -> Logger:
    """
        获取日志记录器实例的函数。

        Returns:
            Logger: 返回一个日志记录器实例。
    """
    logger_mgt = LoggerManager()
    logger = logger_mgt.get_logger()
    return logger


def logger_end():
    """结束并注销当前的logger实例"""
    logger_mgt = LoggerManager()
    logger_mgt.unregister()


def get_ui_screenshot_dir() -> str:
    """
    获取UI截图的保存目录路径
    Returns:
        str: 返回UI截图的保存目录路径
    """
    logger_mgt = LoggerManager()
    logger_name = logger_mgt.default_logger_name
    return logger_mgt.logger_info[logger_name]["ui_dir"]


def logger_unregister(logger):
    """
    移除指定logger的所有句柄
    Args:
        logger: 要移除句柄的logger实例
    """
    for handler in logger.handlers:
        logger.removeHandler(handler)
