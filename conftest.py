import pytest
import logging
from time import sleep
from common.decorator import Decorator
from core.propertyResolver import PropertyResolver as p
from core.webManger import WebManager
from core.loggerManager import logger_init, logger_end

from common.readConfig import parse_args, get_application_config


def pytest_addoption(parser):
    args = parse_args()
    parser.addoption(
        "--env",
        action="store",
        default=args.env,
        choices=['prod', 'test', 'local'],
        help='选择执行的环境，说明：prod: com, test: us, local: 本地环境，./config/config.yml中可修改'
    )
    parser.addoption(
        "--logLevel",
        action="store",
        default=args.logLevel,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='设置控制台日志打印等级'
    )
    parser.addoption(
        '--browser',
        action="store",
        default=args.browser,
        choices=['chrome', 'firefox', 'webkit'],
        help='设置测试所选择的浏览器'
    )


@pytest.fixture(scope='class', autouse=True)
def setup_logger(request):
    log_level = request.config.getoption("--logLevel")
    log_level_mapping = {
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'DEBUG': logging.DEBUG,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    logger_init(case_filepath=request.fspath.strpath, default_level=log_level_mapping[log_level])
    yield
    logger_end()


@pytest.fixture(scope='session', autouse=True)
def setup_environment(request):
    environment = request.config.getoption("--env")
    browser = request.config.getoption("--browser")
    page = WebManager(env=environment, browser_type=browser).get_page()
    yield
    sleep(2)
    page.close()


def pytest_collection_modifyitems(session: "Session", config: "Config", items: list["Item"]):
    appoint_classes = {"TestPreApplication": [],
                       }

    for item in items:
        for cls_name in appoint_classes:
            if item.parent.name == cls_name:
                appoint_classes[cls_name].append(item)
    items.clear()
    for cases in appoint_classes.values():
        items.extend(cases)

    for item in items:
        item.name = item.name.encode("utf-8").decode("unicode_escape")
        item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")


# def pytest_configure(config):
#     Decorator.import_and_decorate_modules('pages', p.base)
