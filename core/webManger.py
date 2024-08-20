import threading
from common.readConfig import get_application_config
from playwright.sync_api import sync_playwright, Playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError


class SingletonMeta(type):
    """实现线程安全的单例模式基类，确保page在多处调用时是同一个实例 """
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


class WebManager(metaclass=SingletonMeta):

    def __init__(self, env='prod', browser_type='chrome'):
        self._page: Page | None = None
        self._playwright: Playwright | None = None
        self._env = env
        self._browser_type = browser_type
        self._config = get_application_config(self._env)
        self._proxy_settings = self._config['proxy_settings']
        self._url_settings = self._config['url_settings']
        self._options = {
            'args': ['--start-maximized'],
            'headless': False,
        }
        self._stat_playwright()

    def _stat_playwright(self):
        self._playwright = sync_playwright().start()

    def get_page(self) -> Page:
        if self._page is None:
            return self.create_page()
        return self._page

    def create_page(self) -> Page:
        if self._browser_type == 'firefox':
            self._page = self._init_page(self._playwright.firefox)
        elif self._browser_type == 'webkit':
            self._page = self._init_page(self._playwright.webkit)
        else:
            self._page = self._init_page(self._playwright.chromium)
        return self._page

    def _init_page(self, page_type, retries=3):
        attempt = 0
        if self._proxy_settings['enable_proxy']:
            self._options['proxy'] = {
                'server': f'{self._proxy_settings["host"]}:{self._proxy_settings["port"]}'
            }
        browser = page_type.launch(**self._options)
        context = browser.new_context(no_viewport=True)
        self.page = context.new_page()
        print()
        while attempt < retries:
            try:
                self.page.goto(f"{self._url_settings['url']}{self._url_settings['path']}", timeout=20000)
                return self.page
            except Exception:
                attempt += 1
                print(f"打开网页失败，开始第 {attempt}/{retries} 次重试")
                if attempt >= retries:
                    raise Exception("已达到最大重连次数")
        return self.page

    def close(self):
        if self._page:
            self._page.close()
            self._page = None
        if self._playwright:
            self._playwright.stop()
