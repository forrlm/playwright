
# 项目介绍 🚀
Pytest + Playwright + Allure zeitro_UI自动化
目前有的功能：
- 🎯 UI自动化 Page Object 设计模式 
- 💻 Playwright 的基本使用（打开网页，元素定位，元素操作，网络等待，断言） 
- ⚙️ Pytest fixture 常见的使用方式
- 📝 Pytest 命令行各种常用的参数配置
- 📊 Allure 报告基本的装饰器使用 (开发中)




# 项目结构 📚
```text
├── README.md                         # 📝 项目介绍及使用指南
├── allure-results                    # 📊 Allure测试报告结果
├── cases                             # 📁 测试用例
│    ├── web                          # 📁 web相关的测试用例
│    │    └── test_preapplication.py  # 🌐 预申请页面测试用例          
│    └── conftest.py                  # 🔧 存放pytest的fixture
├── common                            # 📁 公共函数
│   ├── decorator.py                  # 📑 函数装饰器
│   └── readConfig.py                 # 📑 配置读取
├── config                            # 📁 配置文件夹
│   ├── config.yml                    # 🔧 环境配置
│   └── method_mapping.ini            # 🔧 方法映射
├── core                              # 📁 项目核心
│   ├── loggerManager.py              # 📑 日志管理器
│   ├── webManger.py                  # 📑 浏览器管理器
│   ├── path.py                       # 📑 基本路径配置
│   └── propertyResolver.py           # 📑 属性解析器      
├── logs                              # 📂 日志存放
│   ├── xxxx.log                      # 📎 日志文件
├── pages                             # 📂 页面方法脚本 
│   ├── application                   # 📂 application系统
│   │   └── preapplication.py         # 📑 预申请自动化脚本
│   └── loans                         # 📂 loan officer管理端
│       └── 1003_view.py              # 1003 view 页面自动化脚本          
├── conftest.py                       # 🔧 存放pytest的fixture
├── pytest.ini                        # ⚙️ pytest配置文件
└── requirements.txt                  # 📃 存放项目依赖的Python库
 

```

# 快速开始 ⏩
## 环境准备 🛠️
- Python 3.11+ 🐍
- Java 8+ (Allure依赖Java) ☕
- Allure [安装参考](https://github.com/allure-framework/allure2) 🎈

## 创建虚拟环境 🌐
```shell
$ python3 -m venv .venv

$ .\venv\Scripts\activate
```

## 安装依赖 📌
```shell
$ pip3 install -r requirements.txt
```

## 安装浏览器 🌐
```shell
$ playwright install
```

## 运行测试 🚀
```shell
$ pytest
```

## 可选参数
``` shll
--env --logLevel  --browser, 参数详情使用以下命令
$ pytest --help
```

## 生成测试报告 📊 (暂无)
```shell
allure serve allure-results
```