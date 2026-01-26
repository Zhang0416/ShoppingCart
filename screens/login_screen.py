from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.snackbar import MDSnackbar
from kivy.metrics import dp, sp

import json
import re
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .assets.config_chinese import CHINESE_FONT_NAME


class UserManager:
    """用户管理类，处理用户注册、登录和数据的JSON存储"""

    def __init__(self, data_file: str = "/data/users.json"):
        """
        初始化用户管理器

        Args:
            data_file: 用户数据JSON文件路径
        """
        self.data_file = str(Path(__file__).parent.parent) + data_file
        self.users = self._load_users()

    def _ensure_data_dir(self):
        """确保数据目录存在"""
        data_dir = os.path.dirname(self.data_file)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def _load_users(self) -> List[Dict]:
        """从JSON文件加载用户数据"""
        self._ensure_data_dir()

        if not os.path.exists(self.data_file):
            return []

        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_users(self):
        """保存用户数据到JSON文件"""
        self._ensure_data_dir()
        print(f"data_file: {self.data_file}")
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)

    def _get_current_time(self) -> str:
        """获取当前时间的格式化字符串"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def register_user(self, username: str, phone: str, password: str) -> Tuple[bool, str]:
        """
        注册新用户

        Args:
            username: 用户名
            phone: 手机号
            password: 密码

        Returns:
            (是否成功, 提示信息)
        """
        # 验证输入
        if not username or not phone or not password:
            return False, "所有字段都必须填写"

        # 检查用户名是否已存在
        if any(user["username"] == username for user in self.users):
            return False, "用户名已存在"

        # 检查手机号是否已存在
        if any(user["phone"] == phone for user in self.users):
            return False, "手机号已注册"

        # 验证手机号格式（简单验证）
        if not phone.isdigit() or len(phone) != 11:
            return False, "手机号格式不正确（应为11位数字）"

        # 创建新用户
        new_user = {
            "username": username,
            "phone": phone,
            "password": password,
            "email": None,
            "usual_address": [],
            "register_time": self._get_current_time(),
            "last_login_time": None
        }

        # 添加到用户列表并保存
        self.users.append(new_user)
        self.save_users()

        return True, "注册成功！"

    def login_user(self, phone: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        用户登录

        Args:
            phone: 手机号
            password: 密码

        Returns:
            (是否成功, 提示信息, 用户信息)
        """
        # 查找用户
        user = None
        for u in self.users:
            if u["phone"] == phone:
                user = u
                break

        # 检查用户是否存在
        if not user:
            return False, "用户不存在", None

        # 验证密码
        if user["password"] != password:
            return False, "密码错误", None

        # 更新最后登录时间
        user["last_login_time"] = self._get_current_time()
        self.save_users()

        return True, f"欢迎回来，{user['username']}！", user

    def demo_login(self) -> Tuple[bool, str, Optional[Dict]]:
        """演示登录（使用默认账户）"""
        # 检查是否有演示账户
        demo_user = None
        for user in self.users:
            if user["username"] == "demo" or user["phone"] == "13800138000":
                demo_user = user
                break

        # 如果没有演示账户，创建一个
        if not demo_user:
            success, message = self.register_user(
                username="demo",
                phone="13800138000",
                password="123456"
            )
            if success:
                # 重新获取用户信息
                for user in self.users:
                    if user["phone"] == "13800138000":
                        demo_user = user
                        break

        if demo_user:
            # 更新最后登录时间
            demo_user["last_login_time"] = self._get_current_time()
            self.save_users()
            return True, f"演示登录成功！欢迎{demo_user['username']}", demo_user

        return False, "演示登录失败", None

    def get_all_users(self) -> List[Dict]:
        """获取所有用户信息（调试用）"""
        return self.users


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "login"
        self.password_visible = False  # 初始化为密码模式（隐藏）
        self._build_ui()

    def _build_ui(self):
        layout = MDBoxLayout(
            orientation='vertical',
            padding=dp(40),
            spacing=dp(30),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        # 标题
        title = MDLabel(
            text="购 物 商 城",
            halign="center",
            font_style="Headline1",
            font_size=sp(48),  # 字体用 sp（可随系统字体缩放）
            theme_text_color="Primary",
        )

        # 手机号输入（带眼睛图标，无切换功能）
        phone_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(50),  # 尺寸用 dp
            spacing=dp(20)
        )
        self.phone_input = MDTextField(
            hint_text="请输入手机号",
            # helper_text="仅限数字",
            mode="rectangle",
            icon_left="phone",
            input_filter="int",  # 可选：只允许输入数字
            max_text_length=11,  # 手机号最多11位
            size_hint=(1, None),
            height=dp(60)
        )
        self.phone_input.font_name_hint_text = CHINESE_FONT_NAME
        self.phone_input.font_name_helper_text = CHINESE_FONT_NAME
        # 眼睛图标按钮
        phone_eye_icon = MDIconButton(
            icon="eye",
            theme_text_color="Hint",
            size_hint=(None, None),
            size=(dp(45), dp(45)),
            pos_hint={'center_y': 0.5}
        )
        phone_layout.add_widget(self.phone_input)
        phone_layout.add_widget(phone_eye_icon)

        # 密码输入框（带眼睛图标，可切换隐藏/显示）
        password_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(50),
            spacing=dp(20)
        )

        # 密码输入
        self.password_input = MDTextField(
            hint_text="请输入密码",
            # helper_text="英文字母+数字+特殊字符",
            # font_name_helper_text="H6",
            mode="rectangle",
            icon_left="lock",
            password=True,
            max_text_length=8,
            size_hint=(1, None),
            height=dp(50),
        )
        self.password_input.font_name_hint_text = CHINESE_FONT_NAME
        # self.password_input.font_name_helper_text = CHINESE_FONT_NAME
        # self.password_input.ids.obj.font_name_helper_text = CHINESE_FONT_NAME

        # 眼睛图标按钮
        self.eye_icon = MDIconButton(
            icon="eye-off",
            theme_text_color="Hint",
            size_hint=(None, None),
            size=(sp(45), sp(45)),
            pos_hint={'center_y': 0.5}
        )
        self.eye_icon.bind(on_release=self.toggle_password_visibility)

        password_layout.add_widget(self.password_input)
        password_layout.add_widget(self.eye_icon)

        # 登录按钮
        login_btn = MDRaisedButton(
            text="登录",
            size_hint=(1, None),
            height=dp(50),
            md_bg_color=(0.2, 0.6, 0.86, 1)
        )
        login_btn.bind(on_release=self.login)

        # 注册按钮
        register_btn = MDFlatButton(
            text="注册账号",
            size_hint=(1, None),
            height=dp(40)
        )
        register_btn.bind(on_release=self.show_register_dialog)

        # 忘记密码
        # forgot_btn = MDFlatButton(
        #     text="忘记密码？",
        #     size_hint=(1, None),
        #     height=30
        # )
        # forgot_btn.bind(on_release=self.show_forgot_password_dialog)

        # 快速登录（演示用）
        demo_btn = MDFlatButton(
            text="演示登录",
            size_hint=(1, None),
            height=dp(40)
        )
        demo_btn.bind(on_release=self.demo_login)

        layout.add_widget(title)
        layout.add_widget(phone_layout)
        layout.add_widget(password_layout)
        layout.add_widget(login_btn)
        layout.add_widget(register_btn)
        # layout.add_widget(forgot_btn)
        layout.add_widget(demo_btn)

        self.add_widget(layout)

    def toggle_password_visibility(self, *args):
        """切换密码可见性"""
        self.password_visible = not self.password_visible

        if self.password_visible:
            # 显示密码
            self.password_input.password = False
            self.eye_icon.icon = "eye"
            self.eye_icon.theme_text_color = "Primary"
        else:
            # 隐藏密码
            self.password_input.password = True
            self.eye_icon.icon = "eye-off"
            self.eye_icon.theme_text_color = "Hint"

    def login(self, *args):
        """登录"""
        phone = self.phone_input.text
        password = self.password_input.text

        if not phone or not password:
            self.show_error("请输入手机号和密码")
            return

        if not re.match(r'^1[3-9]\d{9}$', phone):
            self.show_error("手机号格式不正确")
            return

        # 模拟登录成功
        from kivy.app import App
        app = App.get_running_app()

        # 使用UserManager验证登录
        success, message, user = app.user_manager.login_user(phone, password)
        if success:
            app.current_user = {
                'id': '用户_' + str(user['username']) + f'{phone[-4:]}',
                'phone': phone,
                'name': user['username'],
                'email': user['email'],
                'register_time': user['register_time']
            }
            self.show_success(message=message)
            app.show_home()
        else:
            self.show_error(message=message)

    def demo_login(self, *args):
        """演示登录"""
        from kivy.app import App
        app = App.get_running_app()

        success, message, user = app.user_manager.demo_login()
        if success:
            app.current_user = {
                'id': str(user['username']) + str(user['phone'][-4:]),
                'phone': user['phone'],
                'name': user['username'],
                'email': user['email'],
                'register_time': user['register_time']
            }
            self.show_success(message=message)
            app.show_home()
        else:
            self.show_error(message=message)

    def show_register_dialog(self, *args):
        """显示注册对话框"""
        self.dialog = MDDialog(
            title="注册账号",
            type="custom",
            content_cls=MDBoxLayout(
                orientation='vertical',
                spacing=dp(10),
                size_hint_y=None,
                height=dp(200)
            ),
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="注册",
                    on_release=self.register
                )
            ]
        )

        # 添加输入字段
        self.register_phone = MDTextField(hint_text="手机号")
        self.register_phone.font_name_hint_text = CHINESE_FONT_NAME
        self.register_password = MDTextField(hint_text="密码", password=True)
        self.register_password.font_name_hint_text = CHINESE_FONT_NAME
        self.register_name = MDTextField(hint_text="昵称")
        self.register_name.font_name_hint_text = CHINESE_FONT_NAME

        self.dialog.content_cls.add_widget(self.register_phone)
        self.dialog.content_cls.add_widget(self.register_password)
        self.dialog.content_cls.add_widget(self.register_name)

        self.dialog.open()

    def register(self, *args):
        """注册"""
        phone = self.register_phone.text
        password = self.register_password.text
        name = self.register_name.text

        if not all([phone, password, name]):
            self.show_error("请填写所有字段")
            return

        if not re.match(r'^1[3-9]\d{9}$', phone):
            self.show_error("手机号格式不正确")
            return

        if len(password) < 6:
            self.show_error("密码长度至少6位")
            return

        self.dialog.dismiss()
        self.show_success("注册成功！请登录")
        # 自动填充登录信息
        self.phone_input.text = phone
        self.password_input.text = password

    def show_error(self, message):
        """显示错误消息"""
        MDSnackbar(MDLabel(text=message, text_color=(0.9, 0.2, 0.2, 1))).open()

    def show_success(self, message):
        """显示成功消息"""
        MDSnackbar(MDLabel(text=message, theme_text_color="Custom", text_color=(0.2, 0.8, 0.2, 1))).open()
