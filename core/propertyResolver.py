import re
import json
import functools
from .webManger import WebManager
from .loggerManager import LoggerManager
from common.readConfig import get_mapping
from playwright.sync_api import Locator, Page
from typing import Any, Callable, Dict, Tuple

mapping_dict = get_mapping()
logger = LoggerManager().get_logger()


class PropertyResolver:
    """properties参数解析器"""

    @classmethod
    def __custom_encoder(cls, obj):
        if isinstance(obj, re.Pattern):
            return {"__type__": "regex", "pattern": obj.pattern, "flags": obj.flags}
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    @classmethod
    def __custom_decoder(cls, obj):
        if "__type__" in obj and obj["__type__"] == "regex":
            return re.compile(obj["pattern"], obj["flags"])
        return obj

    @classmethod
    def __update_page_properties(cls, func: Callable[..., Dict[str, Any]], page_description: Dict[str, Any],
                                 **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        properties = page_description.get("properties")
        if properties is None:
            raise ValueError("page中不存在properties属性")
        events = {}
        for key, value in kwargs.items():
            if key in properties:
                if isinstance(value, dict):
                    properties[key].update(value)
                events[key] = properties[key]
            else:
                logger.warning(f"Property '{key}' 在{func.__name__}中不存在，将忽略该事件")

        logger.debug(
            f"当前properties属性为: {json.dumps(events, indent=4, ensure_ascii=False, default=cls.__custom_encoder)}")
        return events

    @classmethod
    def __get_page_data(cls, func: Callable[..., Dict[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        page_func = func(**kwargs)
        try:
            page_data = page_func['page']
        except KeyError:
            logger.info(f"Function {func.__name__} did not return a dictionary with a 'page' key.")
            raise KeyError(f"Function {func.__name__} did not return a dictionary with a 'page' key.")
        logger.info(f"开始处理事件: {func.__name__}")
        return page_data

    @classmethod
    def __operation_processor(cls, obj: Page | Locator, parsed_method: str, operation_events: Dict | None,
                              log_msg: str) -> (
            Tuple)[Any, str]:

        if parsed_method == '':
            logger.error("无效的方法")
        parsed_parameters = cls.__arguments_parse(operation_events)
        logger.info(f'原参数: {operation_events}, 解析后的参数: {parsed_parameters}')
        if parsed_parameters is None:
            log_str = f"{log_msg}.{parsed_method}"
            logger.info(f"执行操作: {log_str}")
            return getattr(obj, parsed_method), log_str

        elif isinstance(parsed_parameters, (str, int, float)):
            if parsed_parameters == "":
                log_str = f"{log_msg}.{parsed_method}()"
                logger.info(f"执行: {log_str}")
                return getattr(obj, parsed_method)(), log_str
            else:
                log_str = f"{log_msg}.{parsed_method}({parsed_parameters})"
                logger.info(f'执行: {log_str}')
                return getattr(obj, parsed_method)(parsed_parameters), log_str

        elif isinstance(parsed_parameters, dict):
            _str = ", ".join([f"{key}={value}" for key, value in parsed_parameters.items()])
            log_str = f"{log_msg}.{parsed_method}({_str})"
            logger.info(f'执行: {log_str}')
            return getattr(obj, parsed_method)(**parsed_parameters), log_str

        else:
            logger.warning(f"不匹配的方法: {method_name}, 当前方法: {locator_method_mapping.keys()}")

        return obj, log_msg

    @classmethod
    def __handle_locator(cls, locator_events: Dict | None) -> Tuple[Locator | Page, str]:
        page = WebManager().get_page()
        log_str = 'page'
        locator = page
        if locator_events is None:
            logger.debug('当前没有可处理的Locator，将跳过Locator处理')
            return page, log_str
        logger.info(f"分解以下操作: {locator_events}")
        for locator_method, para in locator_events.items():
            logger.debug(f"原始操作: {locator_method}, 参数: {para}")
            target_method = mapping_dict.get(locator_method.lower()) or locator_method.lower()
            if target_method is None:
                raise ValueError("mapping 中不存在该方法")
            logger.info(f'{locator_method} 解析为 {target_method}')
            locator = locator
            print(f'locator: {locator}')
            locator, log_str = cls.__operation_processor(locator, target_method, para,
                                                         log_str)

        if isinstance(locator, Page):
            logger.error(f"locator为None，检查页面元素: {log_str}是否存在")
            assert False
        return locator, log_str

    @classmethod
    def __handle_operation(cls, locator: Locator | Page, operation_events: Dict | None, log_msg: str):
        if operation_events is None:
            logger.error(f"不存在操作对象Locator 或者 Page，无法执行操作: {log_msg}.{operation_events}")
            return
        result = None
        logger.info(f"分解以下操作: {operation_events}")
        for method, para in operation_events.items():
            logger.debug(f"原始操作: {method}, 参数: {para}")
            target_method = mapping_dict.get(method.lower()) or method.lower()
            if target_method is None:
                raise ValueError("mapping 中不存在该方法")
            logger.info(f'{method} 解析为 {target_method}')
            result, _log = cls.__operation_processor(locator, target_method, para, log_msg)
        return result

    @classmethod
    def __arguments_parse(cls, param: Any) -> None | Dict[str, Any] | str:
        if param is None:
            return None
        if isinstance(param, str):
            if param.strip() == "":
                return ''
            return param.strip()
        if isinstance(param, dict):
            return param
        return param

    @classmethod
    def __handle_assert(cls):
        return None

    @classmethod
    def __process_page(cls, func: Callable[..., Dict[str, Any]], event: str, events: Dict[str, Any] | None,
                       parent_event: str = "") -> Any:
        if events is None:
            if parent_event == "":
                logger.warning("当前操作事件为None，停止进行操作")
            return

        details = events
        locator_events = details.get('loc') or details.get('locator')
        current_operation_events = details.get('op') or details.get('operation')
        # page_events = details.get('page')

        event_node = f"{func.__name__}::{event}" if parent_event == '' else f"{parent_event}::next_operation"

        flag = not locator_events and not current_operation_events
        if flag:
            logger.warning(f"{event_node} 中不存在locator和page事件，将跳过本次执行")
            return

        next_operation_events = details.get('next_operation') or details.get('next')
        slider_events = details.get('slider')
        assert_values = details.get('assert')

        logger.debug(
            f"当前提取的方法: {json.dumps(current_operation_events, indent=4, ensure_ascii=False, default=cls.__custom_encoder)}, "
            f"下一次要处理的操作: {json.dumps(next_operation_events, indent=4, ensure_ascii=False, default=cls.__custom_encoder)}")

        locator, _log_string = cls.__handle_locator(locator_events)
        result = cls.__handle_operation(locator, current_operation_events, _log_string)
        cls.__process_page(func, event, next_operation_events, event_node)

    @classmethod
    def base(cls, func):
        @functools.wraps(func)
        def wrapper(**kwargs):
            page_data = cls.__get_page_data(func)
            events = cls.__update_page_properties(func, page_data, **kwargs)
            for event, details in events.items():
                cls.__process_page(func, event, details)

        return wrapper
