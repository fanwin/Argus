# 页面对象包初始化文件

from .base_page import BasePage
from .login_page import LoginPage
from .home_page import HomePage
from .user_management_page import UserManagementPage
from .search_page import SearchPage
from .form_page import FormPage

__all__ = [
    "BasePage",
    "LoginPage",
    "HomePage",
    "UserManagementPage",
    "SearchPage",
    "FormPage"
]
