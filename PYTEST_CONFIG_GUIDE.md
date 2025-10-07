# Pytest 配置文件说明

本文档详细说明了 `pytest.ini` 配置文件中各个配置项的作用和使用方法。

## 📋 配置文件概览

`pytest.ini` 文件是 pytest 测试框架的主要配置文件，定义了测试运行的默认行为和选项。

## 🔍 配置项详解

### 1. 测试发现配置 (Test Discovery Configuration)

#### testpaths
```ini
testpaths = tests
```
- **作用**: 指定测试文件搜索路径
- **说明**: pytest 会在这些目录中递归搜索测试文件
- **示例**: `testpaths = tests api_tests integration_tests`

#### python_files
```ini
python_files = test_*.py *_test.py
```
- **作用**: 定义测试文件命名规则
- **说明**: 符合这些模式的 .py 文件会被识别为测试文件
- **默认值**: `test_*.py` 和 `*_test.py`

#### python_classes
```ini
python_classes = Test*
```
- **作用**: 定义测试类命名规则
- **说明**: 符合这些模式的类会被识别为测试类
- **默认值**: `Test*`

#### python_functions
```ini
python_functions = test_*
```
- **作用**: 定义测试函数命名规则
- **说明**: 符合这些模式的函数会被识别为测试函数
- **默认值**: `test_*`

### 2. 输出配置 (Output Configuration)

#### addopts
```ini
addopts = -v --strict-markers --strict-config
```
- **作用**: 默认命令行选项
- **说明**: 这些选项会在每次运行 pytest 时自动应用

**常用选项说明**:
- `-v`: 详细模式，显示每个测试的详细信息
- `--strict-markers`: 严格标记模式，未定义的标记会导致错误
- `--strict-config`: 严格配置模式，配置错误会导致失败
- `--tb=short`: 简短的回溯信息格式
- `--html=reports/report.html`: 生成 HTML 格式的测试报告
- `--cov=.`: 启用代码覆盖率检查
- `--alluredir=reports/allure-results`: 生成 Allure 测试报告数据
- `--reruns=1`: 失败测试的重试次数

### 3. 测试标记定义 (Markers Definition)

#### markers
```ini
markers =
    smoke: Smoke tests - Quick verification of core functionality
    api: API tests - Tests for API endpoints and services
    web: Web UI tests - Tests for web user interface
```

**自定义标记说明**:
- **smoke**: 冒烟测试 - 核心功能的快速验证测试
- **regression**: 回归测试 - 验证修复后功能是否正常
- **api**: API测试 - 针对API接口的测试
- **web**: Web UI测试 - 针对Web用户界面的测试
- **slow**: 慢速测试 - 执行时间较长的测试
- **integration**: 集成测试 - 测试多个组件协同工作
- **unit**: 单元测试 - 测试单个功能单元
- **critical**: 关键测试 - 测试核心业务功能
- **security**: 安全测试 - 测试安全相关功能

**使用方法**:
```python
# 标记测试
@pytest.mark.smoke
@pytest.mark.api
def test_user_login():
    pass
```

**运行示例**:
```bash
# 只运行冒烟测试
pytest -m smoke

# 排除慢速测试
pytest -m "not slow"

# 运行既是冒烟又是API的测试
pytest -m "smoke and api"

# 运行冒烟测试或API测试
pytest -m "smoke or api"
```

### 4. 警告过滤配置 (Warning Filters)

#### filterwarnings
```ini
filterwarnings =
    ignore::UserWarning
    ignore::DeprecationWarning
```

**过滤规则**:
- `ignore`: 忽略指定类型的警告
- `error`: 将警告转换为错误
- `default`: 使用默认警告处理
- `always`: 总是显示警告
- `module`: 每个模块只显示一次警告
- `once`: 只显示一次警告

### 5. 版本要求 (Version Requirements)

#### minversion
```ini
minversion = 6.0
```
- **作用**: 指定 pytest 最低版本要求
- **说明**: 确保使用的 pytest 版本支持所需的功能

### 6. 日志配置 (Logging Configuration)

#### 控制台日志配置
```ini
log_cli = true
log_cli_level = INFO
log_cli_format = %(asctime)s [%(levelname)8s] %(name)s: %(message)s
log_cli_date_format = %Y-%m-%d %H:%M:%S
```

**配置说明**:
- `log_cli`: 是否在控制台实时显示日志输出
- `log_cli_level`: 控制台日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
- `log_cli_format`: 控制台日志格式
- `log_cli_date_format`: 控制台日志时间格式

#### 文件日志配置
```ini
log_file = reports/pytest.log
log_file_level = DEBUG
log_file_format = %(asctime)s [%(levelname)8s] %(filename)s:%(lineno)d: %(message)s
log_file_date_format = %Y-%m-%d %H:%M:%S
```

**配置说明**:
- `log_file`: 日志文件保存路径
- `log_file_level`: 文件日志级别（通常比控制台更详细）
- `log_file_format`: 文件日志格式（包含文件名和行号）
- `log_file_date_format`: 文件日志时间格式

## 🚀 使用示例

### 基本测试运行
```bash
# 运行所有测试
pytest

# 运行指定目录的测试
pytest tests/api/

# 运行指定文件的测试
pytest tests/api/test_user_api.py

# 运行指定测试函数
pytest tests/api/test_user_api.py::test_create_user
```

### 使用标记筛选测试
```bash
# 运行冒烟测试
pytest -m smoke

# 运行API测试
pytest -m api

# 运行非慢速测试
pytest -m "not slow"

# 运行关键功能测试
pytest -m critical
```

### 生成报告
```bash
# 生成HTML报告
pytest --html=reports/report.html

# 生成覆盖率报告
pytest --cov=. --cov-report=html

# 生成Allure报告
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

### 并行测试
```bash
# 自动检测CPU核心数并并行运行
pytest -n auto

# 使用4个进程并行运行
pytest -n 4

# 按作用域分发测试
pytest -n auto --dist=loadscope
```

## 📝 最佳实践

### 1. 标记使用建议
- 为不同类型的测试使用合适的标记
- 使用 `smoke` 标记核心功能测试
- 使用 `slow` 标记耗时较长的测试
- 使用环境相关标记 (`dev`, `staging`, `prod`)

### 2. 配置优化建议
- 根据项目需要调整日志级别
- 合理配置警告过滤，避免干扰
- 使用严格模式确保配置正确性
- 定期更新最低版本要求

### 3. 报告配置建议
- 启用HTML报告便于查看结果
- 配置代码覆盖率检查
- 使用Allure生成详细报告
- 设置合理的重试次数

## 🔧 故障排除

### 常见问题

1. **未知标记警告**
   ```
   PytestUnknownMarkWarning: Unknown pytest.mark.xxx
   ```
   **解决方案**: 在 `markers` 配置中定义自定义标记

2. **配置文件不生效**
   - 确保文件名为 `pytest.ini`
   - 确保配置段为 `[pytest]` 而不是 `[tool:pytest]`
   - 检查文件编码是否正确

3. **日志不显示**
   - 检查 `log_cli` 是否设置为 `true`
   - 确认日志级别设置正确
   - 验证日志格式配置

4. **测试收集失败**
   - 检查 `testpaths` 配置是否正确
   - 确认文件命名规则匹配
   - 验证目录结构

## 📚 参考资源

- [Pytest 官方文档](https://docs.pytest.org/)
- [Pytest 配置参考](https://docs.pytest.org/en/stable/reference/reference.html#configuration-options)
- [Pytest 标记文档](https://docs.pytest.org/en/stable/how-to/mark.html)
- [Pytest 日志文档](https://docs.pytest.org/en/stable/how-to/logging.html)
