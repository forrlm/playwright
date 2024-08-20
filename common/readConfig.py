import os
import yaml
import argparse
from core.path import CONFIG_PATH
from typing import Dict, Callable
from configparser import ConfigParser

yml_config_path = os.path.join(CONFIG_PATH, 'config.yml')
method_mapping = os.path.join(CONFIG_PATH, 'method_mapping.ini')


def config_reader(section_name: str, filename: str = method_mapping) -> Callable[
    [Callable[[Dict[str, str]], Dict[str, str]]], Callable[[], Dict[str, str]]]:
    def decorator(func: Callable[[Dict[str, str]], Dict[str, str]]) -> Callable[[], Dict[str, str]]:
        def wrapper() -> Dict[str, str]:
            parser = ConfigParser()
            parser.optionxform = lambda option: option  # 不转换大小写
            parser.read(filename, encoding='utf-8')
            config = {}
            if parser.has_section(section_name):
                params = parser.items(section_name)
                for param in params:
                    config[param[0]] = param[1]
            else:
                raise KeyError(f'Section {section_name} not found in {filename}')

            return func(config)

        return wrapper

    return decorator


@config_reader('mapping')
def get_mapping(config: Dict[str, str]) -> Dict[str, str]:
    return config


@config_reader('page_locator_method_mapping')
def get_page_locator_method_mapping(config: Dict[str, str]) -> Dict[str, str]:
    return config


def _load_config(file_path=yml_config_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config


def get_application_config(environment, config_path=yml_config_path):
    config = _load_config(config_path)
    return config['application'][environment]


def get_loans_config(environment, config_path=yml_config_path):
    config = _load_config(config_path)
    return config['loans'][environment]


def parse_args():
    parser = argparse.ArgumentParser(description='Process environment.')
    parser.add_argument('--env', default='prod', type=str, required=False,
                        choices=['prod', 'test', 'local'],
                        help='选择执行的环境，说明：prod: com, test: us, local: 本地环境，./config/config.yml中可修改')
    parser.add_argument('--logLevel', default='INFO', type=str, required=False,
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='设置控制台日志打印等级')
    parser.add_argument('--browser', default='chrome', type=str, required=False,
                        choices=['chrome', 'firefox', 'webkit'], help='设置测试所选择的浏览器')
    return parser.parse_args()
