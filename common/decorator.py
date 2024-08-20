import sys
import inspect
import functools
import importlib
from pathlib import Path


class Decorator:
    """函数装饰处理器"""

    @classmethod
    def decorate_module_functions(cls, module, decorator):
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj):
                setattr(module, name, decorator(obj))
            elif inspect.ismodule(obj) and obj.__name__.startswith('pages'):
                decorate_module_functions(obj, decorator)

    @classmethod
    def import_and_decorate_modules(cls, package_dir, decorator):
        package_path = Path(package_dir).resolve()
        for path in package_path.rglob('*.py'):
            if path.name == "__init__.py":
                continue
            relative_path = path.relative_to(package_path.parent)
            module_name = '.'.join(relative_path.with_suffix('').parts)
            if module_name not in sys.modules:
                module = importlib.import_module(module_name)
                cls.decorate_module_functions(module, decorator)
            else:
                module = sys.modules[module_name]
                cls.decorate_module_functions(module, decorator)
