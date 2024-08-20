# import pytest
# import os
# import logging
# from core.loggerManager import logger_init, logger_end


# def pytest_addoption(parser):
#     parser.addoption(
#         "--env",
#         action="store",
#         default="prod",
#         help="The environment to use"
#     )
#     parser.addoption(
#         "--logLevel",
#         action="store",
#         default="INFO",
#         choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
#         help="Set the logging level"
#     )


# @pytest.fixture(scope='class', autouse=True)
# def setup_logger(request):
#     log_level = request.config.getoption("--logLevel")
#
#     log_level_mapping = {
#         'INFO': logging.INFO,
#         'WARNING': logging.WARNING,
#         'DEBUG': logging.DEBUG,
#         'ERROR': logging.ERROR,
#         'CRITICAL': logging.CRITICAL
#     }
#
#     logger_init(request.fspath.basename, log_level_mapping[log_level])