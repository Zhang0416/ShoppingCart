from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.textfield import MDTextField
from kivy.metrics import dp
from kivy.app import App
from datetime import datetime, timedelta

from .assets.config_chinese import CHINESE_FONT_NAME


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "home"
        self._otp_verified_at = 0  # 动态口令上次验证通过的时间戳
        self._build_ui()

    def _build_ui(self):
        # 主布局
        main_layout = MDBoxLayout(orientation='vertical')

        # 顶部工具栏
        toolbar = MDTopAppBar(
            title="Shopping Home",
            elevation=4,
            md_bg_color=(0.2, 0.6, 0.86, 1),
            left_action_items=[["menu", lambda x: self.open_menu()]],
            right_action_items=[["cart", lambda x: self.show_cart()]]
        )

        # 欢迎标语
        welcome_card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(120),
            padding=dp(20),
            spacing=dp(10),
            elevation=2,
            radius=[dp(10)]
        )

        self.welcome_label = MDLabel(
            text="欢迎使用 购物商城",
            theme_text_color="Primary",
            font_style="Headline5",
            halign="center",
        )

        self.user_label = MDLabel(
            text="请先登录",
            theme_text_color="Secondary",
            font_style="Subtitle1",
            halign="center"
        )

        welcome_card.add_widget(self.welcome_label)
        welcome_card.add_widget(self.user_label)

        # 功能网格
        grid = MDGridLayout(
            cols=2,
            spacing=dp(20),
            padding=dp(20),
            size_hint=(1, 1)
        )

        # 功能卡片 -- 库存管理(package-variant)移到，服务端
        functions = [
            ("shopping", "浏览商品", "查看和购买商品", "#3498db"),
            ("file-document", "订单管理", "历史订单统计", "#2ecc71"),
            ("account", "个人中心", "个人信息和设置", "#9b59b6"),
            ("store-cog", "库存管理", "商品分类和库存", "#e74c3c")
        ]

        for icon, title, subtitle, color in functions:
            card = MDCard(
                orientation='vertical',
                size_hint=(None, None),
                size=(dp(160), dp(140)),
                padding=dp(15),
                spacing=dp(10),
                elevation=2,
                radius=[dp(15)],
                ripple_behavior=True
            )

            # 图标
            icon_btn = MDIconButton(
                icon=icon,
                icon_size=dp(40),
                theme_text_color="Custom",
                text_color=color,
                pos_hint={'center_x': 0.5}
            )

            # 标题
            title_label = MDLabel(
                text=title,
                theme_text_color="Primary",
                font_style="Headline6",
                halign="center"
            )

            # 副标题
            subtitle_label = MDLabel(
                text=subtitle,
                theme_text_color="Secondary",
                font_style="Caption",
                halign="center"
            )

            card.add_widget(icon_btn)
            card.add_widget(title_label)
            card.add_widget(subtitle_label)

            # 绑定点击事件
            if icon == "shopping":
                card.bind(on_release=self.show_products)
            elif icon == "file-document":
                card.bind(on_release=self.show_orders)
            elif icon == "account":
                card.bind(on_release=self.show_profile)
            elif icon == "store-cog":
                card.bind(on_release=self.show_inventory)

            grid.add_widget(card)

        # 添加所有部件
        main_layout.add_widget(toolbar)
        main_layout.add_widget(welcome_card)
        main_layout.add_widget(grid)

        self.add_widget(main_layout)

    def on_enter(self):
        """进入页面时更新用户信息"""
        app = App.get_running_app()

        if app.current_user:
            self.user_label.text = f"欢迎回来，{app.current_user['name']}"
        else:
            self.user_label.text = "请先登录"

    def open_menu(self):
        """打开菜单"""
        MDSnackbar(
            MDLabel(text="菜单功能开发中", theme_text_color="Custom", text_color=(0.2, 0.6, 0.86, 1)),
            duration=3).open()
        return

    def show_cart(self):
        """显示购物车"""
        app = App.get_running_app()
        app.show_cart()

    def show_products(self, *args):
        """浏览商品"""
        app = App.get_running_app()
        app.show_products()

    def show_orders(self, *args):
        """订单管理 - 动态口令验证（1分钟内免重复验证）"""
        now = datetime.now().timestamp()
        if now - self._otp_verified_at <= 60:
            app = App.get_running_app()
            app.show_orders()
            return
        self._show_otp_dialog("orders")

    def _show_otp_dialog(self, target):
        """显示动态口令验证对话框"""
        self._otp_target = target
        self.otp_input = MDTextField(
            hint_text="请输入动态口令",
            # helper_text="口令 = 当前小时 + 分钟",
            mode="rectangle",
            input_filter="int",
        )
        self.otp_input.font_name_hint_text = CHINESE_FONT_NAME
        self.otp_input.font_name = CHINESE_FONT_NAME

        self.otp_dialog = MDDialog(
            title="动态口令验证",
            type="custom",
            size_hint_x=0.8,
            content_cls=MDBoxLayout(
                self.otp_input,
                orientation="vertical",
                size_hint_y=None,
                height=dp(80),
            ),
            buttons=[
                MDFlatButton(
                    text="取消",
                    font_name=CHINESE_FONT_NAME,
                    on_release=lambda x: self.otp_dialog.dismiss(),
                ),
                MDRaisedButton(
                    text="验证",
                    font_name=CHINESE_FONT_NAME,
                    on_release=self._verify_otp,
                ),
            ],
        )
        self.otp_dialog.ids.title.font_name = CHINESE_FONT_NAME
        self.otp_dialog.open()

    def _verify_otp(self, *args):
        """验证动态口令"""
        bj_now = datetime.now() # 计算北京时间口令：小时 + 分钟
        # bj_now = utc_now + timedelta(hours=8)
        correct_code = bj_now.hour + bj_now.minute

        try:
            user_code = int(self.otp_input.text.strip())
        except (ValueError, AttributeError):
            user_code = -1

        self.otp_dialog.dismiss()

        if user_code == correct_code:
            self._otp_verified_at = datetime.now().timestamp()
            app = App.get_running_app()
            if self._otp_target == "orders":
                app.show_orders()
            else:
                app.show_inventory()
        else:
            # correct_str = f"{bj_now.hour:02d}:{bj_now.minute:02d} = {correct_code}"
            MDSnackbar(
                MDLabel(
                    text=f"口令错误，请检查口令是否正确",
                    theme_text_color="Custom",
                    text_color=(0.9, 0.2, 0.2, 1),
                ),
                duration=3,
            ).open()

    def show_profile(self, *args):
        """个人中心"""
        app = App.get_running_app()
        app.show_profile()

    def show_inventory(self, *args):
        """库存管理 - 动态口令验证（1分钟内免重复验证）"""
        now = datetime.now().timestamp()
        if now - self._otp_verified_at <= 60:
            app = App.get_running_app()
            app.show_inventory()
            return
        self._show_otp_dialog("inventory")

    # def show_logout_dialog(self, *args):
    #     """显示退出登录对话框"""
    #     from kivy.app import App
    #     app = App.get_running_app()
    #
    #     if not app.current_user:
    #         MDSnackbar(MDLabel(text="您还没有登录", text_color=(0.9, 0.2, 0.2, 1))).open()
    #         return
    #
    #     dialog = MDDialog(
    #         title="退出登录",
    #         text=f"确定要退出登录吗？\n当前用户：{app.current_user['name']}",
    #         buttons=[
    #             MDFlatButton(
    #                 text="取消",
    #                 on_release=lambda x: dialog.dismiss()
    #             ),
    #             MDRaisedButton(
    #                 text="确定",
    #                 md_bg_color=(0.9, 0.2, 0.2, 1),
    #                 on_release=lambda x: self.confirm_logout(dialog)
    #             )
    #         ]
    #     )
    #     dialog.ids.title.font_name = CHINESE_FONT_NAME
    #     dialog.open()

    # def confirm_logout(self, dialog):
    #     """确认退出登录"""
    #     dialog.dismiss()
    #
    #     from kivy.app import App
    #     app = App.get_running_app()
    #     app.current_user = None
    #     app.cart.clear()
    #     app.show_login()
