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

### 数据生成和验证
```python
from utilities.data_generator import data_generator
from utilities.data_validator import data_validator

# 生成测试用户数据
users = data_generator.generate_user_data(count=5)

# 验证用户数据
result = data_validator.validate_user_data(users[0])
```

### 页面对象模型
```python
from page_objects import LoginPage, HomePage, UserManagementPage

# 使用登录页面
login_page = LoginPage(selenium_wrapper)
login_page.navigate_to_login_page()
login_page.login("user@example.com", "password123")

# 使用主页
home_page = HomePage(selenium_wrapper)
home_page.search("产品")
```

## 🚀 快速运行

### 使用Python脚本运行
```bash
# 运行所有测试
python run_tests.py

# 运行冒烟测试
python run_tests.py --type smoke --browser chrome --env dev

# 运行API测试（并行）
python run_tests.py --type api --parallel --env staging

# 只运行框架验证
python run_tests.py --validate

# 生成Allure报告
python run_tests.py --report

# 启动Allure报告服务器
python run_tests.py --serve

# 清理报告目录
python run_tests.py --clean
```

### 使用部署脚本运行

#### Linux/Mac
```bash
# 赋予执行权限
chmod +x scripts/deploy.sh

# 运行测试
./scripts/deploy.sh --env dev --type smoke --browser chrome

# 使用Docker运行
./scripts/deploy.sh --docker --env staging --type all --parallel

# 清理环境
./scripts/deploy.sh --clean
```

#### Windows
```cmd
# 运行测试
scripts\deploy.bat --env dev --type smoke --browser chrome

# 使用Docker运行
scripts\deploy.bat --docker --env staging --type all --parallel

# 清理环境
scripts\deploy.bat --clean
```

## 🐳 Docker支持

### 构建和运行
```bash
# 构建Docker镜像
docker build -t argus-test .

# 运行单个容器
docker run --rm -v $(pwd)/reports:/app/reports argus-test

# 使用Docker Compose运行完整环境
docker-compose up --build

# 后台运行
docker-compose up -d

# 查看日志
docker-compose logs -f test-runner

# 停止服务
docker-compose down
```

### 服务访问
- **Selenium Grid Hub**: http://localhost:4444
- **Allure报告服务器**: http://localhost:5050
- **Grafana监控**: http://localhost:3000 (admin/admin)
- **Kibana日志分析**: http://localhost:5601
- **Prometheus监控**: http://localhost:9090

## 🔄 CI/CD集成

### GitHub Actions
项目包含完整的GitHub Actions工作流配置（`.github/workflows/test.yml`），支持：

- **多Python版本测试** (3.8, 3.9, 3.10, 3.11)
- **多浏览器支持** (Chrome, Firefox)
- **并行测试执行**
- **自动报告生成**
- **安全扫描**
- **性能测试**
- **Slack/邮件通知**

触发方式：
- 推送到main/develop分支
- Pull Request
- 定时执行（每天凌晨2点）
- 手动触发

### Jenkins
项目包含Jenkinsfile配置，支持：

- **参数化构建**
- **多阶段并行执行**
- **代码质量检查**
- **安全扫描**
- **多环境部署**
- **报告发布**
- **通知集成**

### 环境变量配置
```bash
# API配置
export API_BASE_URL="https://api.yourproject.com"
export API_TOKEN="your-api-token"
export API_USERNAME="your-username"
export API_PASSWORD="your-password"

# Web配置
export WEB_BASE_URL="https://yourproject.com"
export BROWSER="chrome"
export HEADLESS="true"

# 数据库配置
export DB_HOST="db.yourproject.com"
export DB_USERNAME="db-user"
export DB_PASSWORD="db-password"

# 通知配置
export SLACK_WEBHOOK_URL="your-slack-webhook"
export NOTIFICATION_EMAIL="team@yourproject.com"
```

## 📊 数据管理

### 测试数据生成
```python
from utilities.data_generator import DataGenerator

generator = DataGenerator()

# 生成用户数据
users = generator.generate_user_data(count=10)

# 生成产品数据
products = generator.generate_product_data(count=5)

# 生成API测试数据
api_data = generator.generate_api_test_data("/api/users", "POST")

# 批量生成数据
bulk_data = generator.generate_bulk_test_data(
    ["users", "products", "orders"],
    {"users": 10, "products": 5, "orders": 8}
)

# 保存到文件
generator.save_test_data_to_file(bulk_data, "generated_data.json")
```

### 数据验证
```python
from utilities.data_validator import DataValidator

validator = DataValidator()

# 验证用户数据
user_data = {"username": "test", "email": "test@example.com"}
result = validator.validate_user_data(user_data)

# 验证表单数据
form_rules = {
    "email": {"required": True, "type": "email"},
    "password": {"required": True, "min_length": 8}
}
form_result = validator.validate_form_data(form_data, form_rules)

# 验证测试数据文件
file_result = validator.validate_test_data_file("data/test_data.json")
```

### 配置管理
```python
from utilities.config_reader import config

# 加载配置
config.load_config("dev")

# 获取API配置
api_config = config.get_api_config()

# 获取Web配置
web_config = config.get_web_config()

# 验证配置
is_valid = config.validate_config()
```

## 🧪 页面对象模型

### 基础页面对象
```python
from page_objects.base_page import BasePage

class MyPage(BasePage):
    def __init__(self, selenium_wrapper):
        super().__init__(selenium_wrapper)

    def custom_action(self):
        # 自定义页面操作
        pass
```

### 现有页面对象

#### 登录页面
```python
from page_objects.login_page import LoginPage

login_page = LoginPage(selenium_wrapper)
login_page.navigate_to_login_page()
login_page.login("user@example.com", "password123")
```

#### 主页
```python
from page_objects.home_page import HomePage

home_page = HomePage(selenium_wrapper)
home_page.navigate_to_home_page()
home_page.search("关键词")
home_page.click_products_link()
```

#### 用户管理页面
```python
from page_objects.user_management_page import UserManagementPage

user_page = UserManagementPage(selenium_wrapper)
user_page.navigate_to_user_management_page()
user_page.create_user({
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "password123"
})
```

#### 搜索页面
```python
from page_objects.search_page import SearchPage

search_page = SearchPage(selenium_wrapper)
search_page.navigate_to_search_page()
search_page.search("产品")
results = search_page.get_search_results()
```

#### 表单页面
```python
from page_objects.form_page import FormPage

form_page = FormPage(selenium_wrapper)
form_data = {
    "name": "张三",
    "email": "zhangsan@example.com",
    "message": "测试消息"
}
form_page.fill_form_data(form_data)
form_page.submit_form()
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
