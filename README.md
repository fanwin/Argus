# Pytest自动化测试框架

一个基于Pytest的现代化自动化测试框架，支持API测试和Web UI测试，具有完善的报告系统和多环境配置能力。

## 🚀 特性

- **分层架构清晰**：测试用例、页面对象、工具方法、配置分离
- **多环境支持**：支持dev/staging/prod环境配置切换
- **丰富的报告**：集成Allure报告系统，支持HTML报告
- **并行测试**：支持pytest-xdist并行执行测试
- **完善的日志**：基于loguru的日志记录机制
- **数据驱动**：支持参数化测试和外部数据文件
- **自动截图**：UI测试失败时自动截图
- **全局Fixture**：统一的测试环境管理

## 📁 项目结构

```
project/
│
├── configs/                 # 配置文件
│   ├── dev.yaml            # 开发环境配置
│   ├── staging.yaml        # 预发布环境配置
│   ├── prod.yaml           # 生产环境配置
│   └── __init__.py
│
├── tests/                   # 测试用例
│   ├── api/                # API测试
│   │   └── test_user_api.py
│   ├── web/                # Web UI测试
│   │   └── test_login.py
│   └── __init__.py
│
├── page_objects/           # 页面对象模型
│   ├── login_page.py
│   └── __init__.py
│
├── utilities/              # 工具类
│   ├── logger.py           # 日志记录
│   ├── config_reader.py    # 配置读取
│   ├── api_client.py       # API请求封装
│   ├── selenium_wrapper.py # Selenium二次封装
│   └── __init__.py
│
├── fixtures/               # 全局fixture
│   ├── conftest.py
│   └── __init__.py
│
├── data/                   # 测试数据
│   ├── test_data.json
│   └── __init__.py
│
├── reports/                # 测试报告（自动生成）
│
├── .gitignore
├── pytest.ini             # Pytest配置文件
├── requirements.txt        # 依赖文件
└── README.md              # 项目文档
```

## 🛠️ 技术栈

- **Python 3.8+**
- **Pytest** - 测试框架
- **Selenium 4+** - Web UI测试
- **Requests** - API测试
- **Allure-pytest** - 测试报告
- **pytest-xdist** - 并行测试
- **PyYAML** - 配置管理
- **loguru** - 日志记录

## 📦 安装

1. **克隆项目**
```bash
git clone <repository-url>
cd pytest_framework1
```

2. **创建虚拟环境**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **安装Allure（可选）**
```bash
# Windows (使用Scoop)
scoop install allure

# Mac (使用Homebrew)
brew install allure

# Linux
# 下载并解压Allure，添加到PATH
```

## 🚀 快速开始

### 运行所有测试
```bash
pytest
```

### 运行特定类型的测试
```bash
# 运行API测试
pytest -m api

# 运行Web UI测试
pytest -m web

# 运行冒烟测试
pytest -m smoke
```

### 指定环境运行
```bash
# 设置环境变量
export TEST_ENV=staging  # Linux/Mac
set TEST_ENV=staging     # Windows

# 或者在命令行中指定
TEST_ENV=dev pytest
```

### 并行测试
```bash
# 自动检测CPU核心数
pytest -n auto

# 指定进程数
pytest -n 4
```

### 生成Allure报告
```bash
# 运行测试并生成Allure结果
pytest --alluredir=reports/allure-results

# 生成并打开Allure报告
allure serve reports/allure-results
```

## ⚙️ 配置

### 环境配置

在`configs/`目录下有三个环境配置文件：

- `dev.yaml` - 开发环境
- `staging.yaml` - 预发布环境  
- `prod.yaml` - 生产环境

可以通过环境变量`TEST_ENV`来切换环境：

```bash
export TEST_ENV=staging
```

### 环境变量覆盖

支持通过环境变量覆盖配置文件中的设置：

```bash
export API_BASE_URL=https://api.example.com
export API_TOKEN=your_token_here
export WEB_BASE_URL=https://web.example.com
export BROWSER=firefox
export HEADLESS=true
```

## 📝 编写测试

### API测试示例

```python
import pytest
import allure
from utilities.api_client import APIClient

@allure.feature("用户管理")
class TestUserAPI:
    
    @pytest.mark.api
    @pytest.mark.smoke
    def test_create_user(self, api_client_fixture):
        user_data = {
            "name": "测试用户",
            "email": "test@example.com"
        }
        
        response = api_client_fixture.post("/api/users", json_data=user_data)
        api_client_fixture.assert_status_code(response, 201)
        
        response_data = api_client_fixture.get_response_json(response)
        assert response_data["name"] == user_data["name"]
```

### Web UI测试示例

```python
import pytest
import allure
from page_objects.login_page import LoginPage

@allure.feature("用户认证")
class TestLogin:
    
    @pytest.mark.web
    @pytest.mark.smoke
    def test_login_success(self, web_driver, web_config):
        login_page = LoginPage(web_driver)
        login_page.navigate_to_login_page(web_config["base_url"])
        
        login_page.login("admin@example.com", "password123")
        
        assert login_page.is_login_successful()
```

## 🏷️ 测试标记

框架定义了以下测试标记：

- `@pytest.mark.smoke` - 冒烟测试
- `@pytest.mark.regression` - 回归测试
- `@pytest.mark.api` - API测试
- `@pytest.mark.web` - Web UI测试
- `@pytest.mark.slow` - 慢速测试
- `@pytest.mark.critical` - 关键功能测试

使用示例：
```bash
pytest -m "smoke and api"
pytest -m "not slow"
```

## 📊 报告

### HTML报告
```bash
pytest --html=reports/report.html --self-contained-html
```

### Allure报告
```bash
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

### 覆盖率报告
```bash
pytest --cov=. --cov-report=html:reports/coverage
```

## 🔧 高级功能

### 失败重试
```bash
pytest --reruns=2 --reruns-delay=1
```

### 自定义日志级别
```python
from utilities.logger import log

log.info("这是一条信息日志")
log.error("这是一条错误日志")
```

### 数据驱动测试
```python
@pytest.mark.parametrize("user_data", [
    {"username": "user1", "password": "pass1"},
    {"username": "user2", "password": "pass2"},
])
def test_login_multiple_users(login_page, user_data):
    login_page.login(user_data["username"], user_data["password"])
    assert login_page.is_login_successful()
```

## 🤝 贡献

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 支持

如有问题或建议，请：

1. 查看 [Issues](../../issues)
2. 创建新的 Issue
3. 联系维护者

---

**Happy Testing! 🎉**
