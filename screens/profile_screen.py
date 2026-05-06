from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.chip import MDChip
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.list import (MDList, OneLineListItem, OneLineIconListItem, TwoLineListItem, ThreeLineListItem,
                             IconLeftWidget, IconRightWidget, ThreeLineAvatarIconListItem, TwoLineIconListItem)
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.selectioncontrol import MDSwitch, MDCheckbox
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
from kivy.logger import Logger
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.app import App
from kivy.utils import platform
from datetime import datetime
from pathlib import Path
import json
import os
import glob
import re
import shutil
import tempfile
import zipfile
import traceback

from .assets.config_chinese import CHINESE_FONT_NAME


class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "profile"
        self._build_ui()

    def _build_ui(self):
        # 主布局
        main_layout = MDBoxLayout(orientation='vertical')

        # 顶部栏
        toolbar = MDTopAppBar(
            title="个人中心",
            elevation=dp(4),
            md_bg_color=(0.2, 0.6, 0.86, 1),
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[["cog", lambda x: self.open_settings()]]
        )
        toolbar.ids.label_title.font_name = CHINESE_FONT_NAME

        # 用户信息卡片
        self.user_card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(150),
            padding=dp(20),
            spacing=dp(10),
            md_bg_color=(0.95, 0.95, 0.95, 1),
            ripple_behavior=True
        )

        self.user_name = MDLabel(
            text="用户",
            theme_text_color="Primary",
            font_style="Headline5"
        )

        self.user_phone = MDLabel(
            text="手机号：",
            theme_text_color="Secondary"
        )

        self.user_email = MDLabel(
            text="邮箱：未设置",
            theme_text_color="Secondary"
        )

        self.user_card.add_widget(self.user_name)
        self.user_card.add_widget(self.user_phone)
        self.user_card.add_widget(self.user_email)

        # 功能列表
        scroll_view = MDScrollView()
        self.menu_list = MDList()

        # 个人信息区
        personal_section = OneLineListItem(
            text="个人信息",
            theme_text_color="Primary",
            font_style="Headline6"
        )

        # 修改密码
        change_pwd_item = OneLineIconListItem(
            text="修改密码",
            on_release=self.change_password
        )
        change_pwd_item.add_widget(
            IconLeftWidget(icon="lock", theme_text_color="Custom", text_color=(0.2, 0.2, 0.8, 1))
        )

        # 修改信息
        change_info_item = OneLineIconListItem(
            text="修改个人信息",
            on_release=self.change_user_info
        )
        change_info_item.add_widget(
            IconLeftWidget(icon="account-edit", theme_text_color="Custom", text_color=(1, 0.5, 0, 1))
        )

        # 收货地址
        address_item = OneLineIconListItem(
            text="收货地址管理",
            on_release=self.show_addresses
        )
        address_item.add_widget(
            IconLeftWidget(icon="map-marker", theme_text_color="Custom", text_color=(0.2, 0.8, 0.2, 1))
        )

        # 应用设置区
        settings_section = OneLineListItem(
            text="应用设置",
            theme_text_color="Primary",
            font_style="Headline6"
        )

        # 通知设置
        notification_item = OneLineIconListItem(
            text="通知设置"
        )
        self.notification_switch = MDSwitch(
            pos_hint={"center_y": 0.3},
            # active=True
        )
        notification_item.add_widget(self.notification_switch)

        # 主题设置
        theme_item = OneLineIconListItem(
            text="深色模式",
            on_release=self.toggle_theme
        )
        self.theme_switch = MDSwitch(
            pos_hint={"center_y": 0.3}
        )
        theme_item.add_widget(self.theme_switch)

        # 数据管理
        data_management_item = OneLineIconListItem(
            text="数据管理",
            on_release=self.show_data_management
        )
        data_management_item.add_widget(
            IconLeftWidget(icon="database", theme_text_color="Custom", text_color=(0.3, 0.2, 0.6, 1))
        )

        # 数据迁移
        data_migration_item = OneLineIconListItem(
            text="数据迁移",
            on_release=self.show_data_migration_dialog
        )
        data_migration_item.add_widget(
            IconLeftWidget(icon="swap-horizontal", theme_text_color="Custom", text_color=(0.8, 0.5, 0.1, 1))
        )

        # 连接蓝牙打印机
        self.bluetooth_printer_item = OneLineIconListItem(
            text="连接打印机",
            on_release=self.show_bluetooth_printer_dialog
        )
        self.bluetooth_printer_item.add_widget(
            IconLeftWidget(icon="printer", theme_text_color="Custom", text_color=(0.2, 0.6, 0.1, 1))
        )

        # 关于与帮助区
        about_section = OneLineListItem(
            text="关于与帮助",
            theme_text_color="Primary",
            font_style="Headline6"
        )

        # 关于我们
        about_item = OneLineIconListItem(
            text="关于我们",
            on_release=self.show_about
        )
        about_item.add_widget(IconLeftWidget(icon="information"))

        # 帮助中心
        help_item = OneLineIconListItem(
            text="帮助中心",
            on_release=self.show_help
        )
        help_item.add_widget(IconLeftWidget(icon="help-circle"))

        # 反馈建议
        feedback_item = OneLineIconListItem(
            text="反馈建议",
            on_release=self.show_feedback
        )
        feedback_item.add_widget(IconLeftWidget(icon="message-text"))

        # 退出登录
        logout_item = OneLineIconListItem(
            text="退出登录",
            on_release=self.logout
        )
        logout_item.add_widget(IconLeftWidget(icon="logout", theme_text_color="Error"))

        # 添加到列表
        self.menu_list.add_widget(personal_section)
        self.menu_list.add_widget(change_pwd_item)
        self.menu_list.add_widget(change_info_item)
        self.menu_list.add_widget(address_item)
        self.menu_list.add_widget(logout_item)
        self.menu_list.add_widget(settings_section)
        self.menu_list.add_widget(data_management_item)
        self.menu_list.add_widget(data_migration_item)
        self.menu_list.add_widget(self.bluetooth_printer_item)
        self.menu_list.add_widget(notification_item)
        self.menu_list.add_widget(theme_item)
        self.menu_list.add_widget(about_section)
        self.menu_list.add_widget(about_item)
        self.menu_list.add_widget(help_item)
        self.menu_list.add_widget(feedback_item)

        scroll_view.add_widget(self.menu_list)

        main_layout.add_widget(toolbar)
        main_layout.add_widget(self.user_card)
        main_layout.add_widget(scroll_view)

        self.add_widget(main_layout)

    def on_enter(self):
        """进入页面时更新用户信息"""
        app = App.get_running_app()

        if app.current_user:
            self.user_name.text = app.current_user.get('name', '用户')
            self.user_phone.text = f"手机号：{app.current_user.get('phone', '未设置')}"
            self.user_email.text = f"邮箱：{app.current_user.get('email', '未设置')}"

            # 更新用户卡片点击事件
            self.user_card.bind(on_release=self.show_user_info)
        else:
            self.user_name.text = "请先登录"
            self.user_phone.text = "手机号：未登录"
            self.user_email.text = "邮箱：未登录"
            # self.user_card.unbind(on_release)

    def show_user_info(self, *args):
        """显示用户信息"""
        app = App.get_running_app()

        if not app.current_user:
            return

        dialog = MDDialog(
            title="用户信息",
            size_hint_x=0.9,
            background_color=(0, 0, 0, 0),
            text=f"用户名：{app.current_user.get('name', '')}\n"
                 f"手机号：{app.current_user.get('phone', '')}\n"
                 f"邮箱：{app.current_user.get('email', '未设置')}\n"
                 f"用户ID：{app.current_user.get('id', '')}\n"
                 f"注册时间：{app.current_user.get('register_time', '')}",
            buttons=[
                MDFlatButton(
                    text="关闭",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.ids.title.font_name = CHINESE_FONT_NAME
        dialog.open()

    def change_password(self, *args):
        """修改密码"""
        dialog = MDDialog(
            title="修改密码",
            size_hint_x=0.9,
            background_color=(0, 0, 0, 0),
            type="custom",
            content_cls=MDBoxLayout(orientation='vertical',
                                    spacing=dp(10),
                                    size_hint_y=None,
                                    height=dp(200)),
            buttons=[
                MDFlatButton(text="取消",
                             on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text="确认修改",
                               on_release=lambda x: self.save_password(dialog))
            ]
        )
        dialog.ids.title.font_name = CHINESE_FONT_NAME

        self.password_input = dict()
        self.password_input['old'] = MDTextField(hint_text="旧密码", password=True)
        self.password_input['old'].font_name_hint_text = CHINESE_FONT_NAME
        self.password_input['new'] = MDTextField(hint_text="新密码", password=True)
        self.password_input['new'].font_name_hint_text = CHINESE_FONT_NAME
        self.password_input['confirm'] = MDTextField(hint_text="确认新密码", password=True)
        self.password_input['confirm'].font_name_hint_text = CHINESE_FONT_NAME

        dialog.content_cls.add_widget(self.password_input['old'])
        dialog.content_cls.add_widget(self.password_input['new'])
        dialog.content_cls.add_widget(self.password_input['confirm'])

        dialog.open()

    def save_password(self, dialog):
        """保存密码"""
        # 查找用户
        user = self.search_current_user()
        if not user:
            MDSnackbar(MDLabel(text="用户不存在", theme_text_color="Custom", text_color=(0.6, 0.2, 0.2, 1))).open()
            return

        old_pwd = self.password_input['old'].text
        new_pwd = self.password_input['new'].text
        confirm_pwd = self.password_input['confirm'].text

        if not old_pwd or not new_pwd or not confirm_pwd:
            MDSnackbar(MDLabel(text="请填写所有字段", theme_text_color="Custom", text_color=(0.9, 0.2, 0.2, 1))).open()
            return

        if old_pwd != user['password']:
            MDSnackbar(MDLabel(text="旧密码输入错误", theme_text_color="Custom", text_color=(0.6, 0.2, 0.5, 1))).open()
            return

        if new_pwd != confirm_pwd:
            MDSnackbar(
                MDLabel(text="两次输入的新密码不一致", ttheme_text_color="Custom", ext_color=(0.9, 0.2, 0.2, 1))).open()
            return

        if len(new_pwd) < 6:
            MDSnackbar(MDLabel(text="密码长度至少6位", theme_text_color="Custom", text_color=(0.9, 0.2, 0.2, 1))).open()
            return

        dialog.dismiss()

        # 保存新密码
        user['password'] = new_pwd

        app = App.get_running_app()
        app.user_manager.save_users()

        MDSnackbar(MDLabel(text="密码修改成功", theme_text_color='Custom', text_color=(0.2, 0.8, 0.2, 1)),
                   md_bg_color=(0.8, 0.8, 0.8, 1)).open()
        return

    def change_user_info(self, *args):
        """修改用户信息"""
        app = App.get_running_app()

        if not app.current_user:
            MDSnackbar(MDLabel(text="请先登录", theme_text_color="Custom", text_color=(0.9, 0.2, 0.2, 1))).open()
            return

        dialog = MDDialog(
            title="修改个人信息",
            size_hint_x=0.9,
            background_color=(0, 0, 0, 0),
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
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="保存",
                    on_release=lambda x: self.save_user_info(dialog)
                )
            ]
        )
        dialog.ids.title.font_name = CHINESE_FONT_NAME

        self.user_info_input = dict()
        self.user_info_input['name'] = MDTextField(hint_text="用户名", text=app.current_user.get('name', ''))
        self.user_info_input['name'].font_name_hint_text = CHINESE_FONT_NAME
        self.user_info_input['name'].font_name = CHINESE_FONT_NAME
        self.user_info_input['phone'] = MDTextField(hint_text="手机号", text=app.current_user.get('phone', ''))
        self.user_info_input['phone'].font_name_hint_text = CHINESE_FONT_NAME
        self.user_info_input['phone'].font_name = CHINESE_FONT_NAME
        self.user_info_input['email'] = MDTextField(hint_text="邮箱", text=app.current_user.get('email', ''))
        self.user_info_input['email'].font_name_hint_text = CHINESE_FONT_NAME
        self.user_info_input['email'].font_name = CHINESE_FONT_NAME

        dialog.content_cls.add_widget(self.user_info_input['name'])
        dialog.content_cls.add_widget(self.user_info_input['phone'])
        dialog.content_cls.add_widget(self.user_info_input['email'])

        dialog.open()

    def save_user_info(self, dialog):
        """保存用户信息"""
        name = self.user_info_input['name'].text.strip()
        phone = self.user_info_input['phone'].text.strip()
        email = self.user_info_input['email'].text.strip()

        if not name:
            MDSnackbar(MDLabel(text="用户名不能为空", theme_text_color="Custom", text_color=(0.9, 0.2, 0.2, 1))).open()
            return

        if not phone or len(phone) != 11 or not re.match(r'^1[3-9]\d{9}$', phone):
            MDSnackbar(
                MDLabel(text="手机号格式不正确", theme_text_color="Custom", text_color=(0.9, 0.2, 0.2, 1))).open()
            return

        if "@" not in email:
            MDSnackbar(MDLabel(text="请正确填写邮箱名称与后缀", theme_text_color="Custom",
                               text_color=(0.9, 0.2, 0.2, 1))).open()
            return

        app = App.get_running_app()

        # 更新用户信息
        app.current_user['id'] = '用户_' + name + f'{phone[-4:]}',
        app.current_user['name'] = name
        app.current_user['phone'] = phone
        app.current_user['email'] = email

        # 更新保存信息
        user = self.search_current_user()
        if not user:
            return
        user['name'] = name
        user['phone'] = phone
        user['email'] = email
        app.user_manager.save_users()

        # 更新显示
        self.user_name.text = name
        self.user_phone.text = phone
        self.user_email.text = f"邮箱：{email if email else '未设置'}"

        dialog.dismiss()

        MDSnackbar(MDLabel(text="个人信息更新成功", theme_text_color='Custom', text_color=(0.2, 0.8, 0.2, 1)),
                   md_bg_color=(0.8, 0.8, 0.8, 1)).open()

    def show_addresses(self, *args):
        # 查找用户
        user = self.search_current_user()
        if not user:
            return
        combined_addr = user['usual_address']

        if len(combined_addr) == 0:
            # 示例地址
            addresses = [
                {"name": "张三", "phone": "13800138000", "address": "北京市朝阳区建国门外大街1号"},
                {"name": "李四", "phone": "13900139000", "address": "上海市浦东新区张江高科技园区"}
            ]
        else:
            addresses = []
            for addr in combined_addr:
                tmp = addr.split('~')
                if len(tmp) > 3:
                    tmp[0] = "~".join(tmp[:-2])  # 用户名中含有特殊字符，重新组合
                addresses.append({"name": tmp[0], "phone": tmp[-2], "address": tmp[-1]})

        # 地址列表
        scroll_view = MDScrollView()
        address_list = MDList()

        for i, addr in enumerate(addresses):
            item = ThreeLineAvatarIconListItem(
                text=f"收货人：{addr['name']}",
                secondary_text=f"电话：{addr['phone']}",
                tertiary_text=f"地址：{addr['address']}",
                _txt_left_pad=dp(4),
                _txt_right_pad=dp(4),
            )

            # 配置右侧容器：用 MDBoxLayout 包裹两个 MDIconButton，避免被截断
            right_container = item.ids._right_container
            right_container.size_hint = (None, 1)
            right_container.width = dp(72)
            if hasattr(right_container, 'anchor_x'):
                right_container.anchor_x = 'right'

            btn_box = MDBoxLayout(
                orientation='horizontal',
                size_hint=(None, None),
                size=(dp(64), dp(32)),
                pos_hint={'center_y': 0.5},
                spacing=dp(4)
            )

            edit_btn = MDIconButton(
                icon="pencil",
                theme_text_color="Custom",
                text_color=(0.2, 0.8, 0.2, 1),
                size_hint=(None, None),
                size=(dp(28), dp(28)),
                pos_hint={'center_y': 0.5},
            )
            edit_btn.bind(on_release=lambda x, idx=i: self.edit_address(idx))

            delete_btn = MDIconButton(
                icon="delete",
                theme_text_color="Error",
                size_hint=(None, None),
                size=(dp(28), dp(28)),
                pos_hint={'center_y': 0.5},
            )
            delete_btn.bind(on_release=lambda x, idx=i: self.delete_address(idx))

            btn_box.add_widget(edit_btn)
            btn_box.add_widget(delete_btn)
            right_container.add_widget(btn_box)
            address_list.add_widget(item)

        scroll_view.add_widget(address_list)

        """显示收货地址"""
        self.show_addr_dialog = MDDialog(
            title="收货地址管理",
            type="custom",
            size_hint_x=0.9,
            background_color=(0, 0, 0, 0),
            content_cls=MDBoxLayout(
                orientation='vertical',
                spacing=dp(10),
                size_hint_y=None,
                height=dp(400)
            ),
            buttons=[
                MDFlatButton(
                    text="关闭",
                    on_release=lambda x: self.show_addr_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="新增地址",
                    on_release=lambda x: self.show_new_address_dialog()
                )
            ]
        )
        self.show_addr_dialog.ids.title.font_name = CHINESE_FONT_NAME
        self.show_addr_dialog.content_cls.add_widget(scroll_view)
        self.show_addr_dialog.open()

    def edit_address(self, idx: int):
        # 查找用户
        user = self.search_current_user()
        if not user:
            return

        tmp = user['usual_address'][idx].split('~')
        if len(tmp) > 3:
            tmp[0] = "~".join(tmp[:-2])
        # if name == tmp[0] and phone == tmp[-2] and addr == tmp[-1]:
        content_layout = MDBoxLayout(orientation='vertical',
                                     spacing=dp(10),
                                     size_hint_y=None,
                                     height=dp(230))
        self.edit_cont = dict()
        self.edit_cont['name'] = MDTextField(hint_text="请输入修改后的名称",
                                             text=tmp[0],
                                             size_hint_y=None,
                                             height=dp(80))
        self.edit_cont['name'].font_name_hint_text = CHINESE_FONT_NAME
        self.edit_cont['name'].font_name = CHINESE_FONT_NAME
        self.edit_cont['phone'] = MDTextField(hint_text="请输入修改后的电话",
                                              text=tmp[-2],
                                              size_hint_y=None,
                                              height=dp(80))
        self.edit_cont['phone'].font_name_hint_text = CHINESE_FONT_NAME
        self.edit_cont['phone'].font_name = CHINESE_FONT_NAME
        self.edit_cont['addr'] = MDTextField(hint_text="请输入修改后的地址",
                                             text=tmp[-1],
                                             size_hint_y=None,
                                             height=dp(80),
                                             font_size=sp(16))
        self.edit_cont['addr'].font_name_hint_text = CHINESE_FONT_NAME
        self.edit_cont['addr'].font_name = CHINESE_FONT_NAME
        content_layout.add_widget(self.edit_cont['name'])
        content_layout.add_widget(self.edit_cont['phone'])
        content_layout.add_widget(self.edit_cont['addr'])

        # 编辑对话框
        self.edit_dialog = MDDialog(
            title="编辑",
            size_hint_x=0.9,
            background_color=(0, 0, 0, 0),
            type="custom",
            content_cls=content_layout,
            buttons=[
                MDFlatButton(text="关闭",
                             on_release=lambda x: self.edit_dialog.dismiss()),
                MDRaisedButton(text="保存",
                               on_release=lambda x, i=idx, u=user: self.confirm_edit_and_save(i, u))
            ]
        )
        self.edit_dialog.ids.title.font_name = CHINESE_FONT_NAME
        self.edit_dialog.open()

    def confirm_edit_and_save(self, idx: int, user: dict):
        # 关闭对话框
        self.edit_dialog.dismiss()
        self.show_addr_dialog.dismiss()

        user["usual_address"][idx] = "~".join(
            [self.edit_cont['name'].text, self.edit_cont['phone'].text, self.edit_cont['addr'].text])

        app = App.get_running_app()
        app.user_manager.save_users()  # 保存
        self.show_addresses()
        return

    def delete_address(self, idx: int):
        # 查找用户
        user = self.search_current_user()
        if not user:
            return

        # 确认删除 对话框
        self.confirm_delete_dialog = MDDialog(
            title="确认删除",
            size_hint_x=0.9,
            background_color=(0, 0, 0, 0),
            type="custom",
            content_cls=MDBoxLayout(
                orientation='vertical',
                spacing=dp(10),
                size_hint_y=None,
                height=dp(200)
            ),
            buttons=[
                MDFlatButton(text="取消",
                             on_release=lambda x: self.confirm_delete_dialog.dismiss()),
                MDRaisedButton(text="确认",
                               on_release=lambda x, i=idx, u=user: self.confirm_delete(i, u))
            ]
        )
        self.confirm_delete_dialog.ids.title.font_name = CHINESE_FONT_NAME
        self.confirm_delete_dialog.open()

    def confirm_delete(self, idx: int, user: dict):
        # 关闭对话框
        self.confirm_delete_dialog.dismiss()
        self.show_addr_dialog.dismiss()

        del user["usual_address"][idx]

        app = App.get_running_app()
        app.user_manager.save_users()  # 保存
        self.show_addresses()
        return

    def show_new_address_dialog(self, *args):
        """显示新增地址对话框"""
        self.dialog = MDDialog(
            title="新增地址",
            size_hint_x=0.9,
            background_color=(0, 0, 0, 0),
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
                    text="新增",
                    on_release=self.new_register
                )
            ]
        )

        # 添加输入字段
        self.new_name = MDTextField(hint_text="收货人", font_size=12)
        self.new_name.font_name_hint_text = CHINESE_FONT_NAME
        self.new_name.font_name = CHINESE_FONT_NAME

        self.new_phone = MDTextField(hint_text="电话", font_size=12)
        self.new_phone.font_name_hint_text = CHINESE_FONT_NAME
        self.new_phone.font_name = CHINESE_FONT_NAME

        self.new_address = MDTextField(hint_text="地址")
        self.new_address.font_name_hint_text = CHINESE_FONT_NAME
        self.new_address.font_name = CHINESE_FONT_NAME

        self.dialog.content_cls.add_widget(self.new_name)
        self.dialog.content_cls.add_widget(self.new_phone)
        self.dialog.content_cls.add_widget(self.new_address)

        self.dialog.open()

    def new_register(self, *args):
        """注册"""
        self.show_addr_dialog.dismiss()
        self.dialog.dismiss()
        if "~" in self.new_address.text:
            MDSnackbar(MDLabel(text="地址中不能包含特殊字符'~'", theme_text_color="Custom",
                               text_color=(0.2, 0.8, 0.5, 1))).open()
            return
        MDSnackbar(MDLabel(text="新增地址成功", theme_text_color="Custom", text_color=(0.2, 0.6, 0.86, 1))).open()

        # 检查用户是否存在
        user = self.search_current_user()
        if not user:
            return

        if len(user['usual_address']) >= 100:
            user['usual_address'].pop(0)
        user['usual_address'].append('~'.join([self.new_name.text, self.new_phone.text, self.new_address.text]))

        app = App.get_running_app()
        app.user_manager.save_users()  # 保存
        self.show_addresses()
        # app.show_profile()  # 返回
        return

    def search_current_user(self):
        app = App.get_running_app()

        # 查找用户
        user = None
        for u in app.user_manager.users:
            if u["phone"] == app.current_user['phone']:
                user = u
                break
        return user

    def toggle_theme(self, *args):
        """切换主题"""
        app = App.get_running_app()

        if app.theme_cls.theme_style == "Light":
            app.theme_cls.theme_style = "Dark"
            self.theme_switch.active = True
        else:
            app.theme_cls.theme_style = "Light"
            self.theme_switch.active = False

    def show_data_management(self, *args):
        """显示数据管理"""
        dialog = MDDialog(
            title="数据管理",
            size_hint_x=0.9,
            background_color=(0, 0, 0, 0),
            type="custom",
            content_cls=MDBoxLayout(
                orientation='vertical',
                spacing=dp(10),
                size_hint_y=None,
                height=dp(250)
            ),
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="清除缓存",
                    md_bg_color=(0.9, 0.2, 0.2, 1),
                    on_release=lambda x: self.clear_cache(dialog)
                )
            ]
        )
        dialog.ids.title.font_name = CHINESE_FONT_NAME

        # 检查文件大小
        order_file_size = 0
        parent_dir = str(Path(__file__).parent.parent)
        Logger.info(f"parent directory: {parent_dir}")
        if os.path.exists(parent_dir + "/data/orders.json"):
            order_file_size = os.path.getsize(parent_dir + "/data/orders.json") / 1024  # KB

        user_file_size = 0
        if os.path.exists(parent_dir + "/data/users.json"):
            user_file_size = os.path.getsize(parent_dir + "/data/users.json") / 1024  # KB

        dialog.content_cls.add_widget(MDLabel(
            text="数据统计",
            theme_text_color="Primary",
            font_style="Headline6"
        ))

        dialog.content_cls.add_widget(MDLabel(
            text=f"订单数据文件：{order_file_size:.2f} KB",
            theme_text_color="Secondary"
        ))

        dialog.content_cls.add_widget(MDLabel(
            text=f"用户数据文件：{user_file_size:.2f} KB",
            theme_text_color="Secondary"
        ))

        cache_files = glob.glob("*.cache") + glob.glob("*.tmp")
        cache_file_size = 0
        for cache_file in cache_files:
            cache_file_size += os.path.getsize(cache_file) / 1024
        dialog.content_cls.add_widget(MDLabel(
            text=f"缓存数据：{cache_file_size:.2f} KB",
            theme_text_color="Secondary"
        ))

        dialog.content_cls.add_widget(MDLabel(
            text="清除缓存将删除所有临时数据，但不会删除订单记录。",
            theme_text_color="Hint",
            font_style="Caption"
        ))

        dialog.open()

    def clear_cache(self, dialog):
        """清除缓存"""
        try:
            # 清除缓存文件
            cache_files = glob.glob("*.cache") + glob.glob("*.tmp")
            for file in cache_files:
                try:
                    os.remove(file)
                except:
                    pass

            dialog.dismiss()

            MDSnackbar(MDLabel(text="缓存已清除", theme_text_color="Custom", text_color=(0.2, 0.8, 0.2, 1))).open()
        except Exception as e:
            MDSnackbar(
                MDLabel(text=f"清除缓存失败: {str(e)}", theme_text_color="Custom", text_color=(0.9, 0.2, 0.2, 1))
            ).open()

    def show_about(self, *args):
        """显示关于信息（版本号动态从 buildozer.spec 读取）"""
        app = App.get_running_app()
        version = getattr(app, 'app_version', '1.0.0')
        dialog = MDDialog(
            title="关于购物商城",
            text=f"购物商城 v{version}\n\n"
                 "一个功能完整的移动购物应用\n"
                 "支持用户管理、商品浏览、购物车、订单管理等功能\n\n"
                 "开发者: ShoppingCart Team\n"
                 "联系方式: support@shoppingcart.com\n"
                 "官方网站: https://www.shoppingcart.com",
            size_hint_x=0.9,
            background_color=(0, 0, 0, 0),
            buttons=[
                MDFlatButton(text="确定", on_release=lambda x: dialog.dismiss())
            ]
        )
        dialog.ids.title.font_name = CHINESE_FONT_NAME
        dialog.open()

    def show_help(self, *args):
        """显示帮助中心"""
        dialog = MDDialog(
            title="帮助中心",
            type="custom",
            size_hint_x=0.9,
            background_color=(0, 0, 0, 0),
            content_cls=MDBoxLayout(orientation='vertical',
                                    spacing=dp(10),
                                    size_hint_y=None,
                                    height=dp(300)),
            buttons=[
                MDFlatButton(text="关闭", on_release=lambda x: dialog.dismiss())
            ]
        )
        dialog.ids.title.font_name = CHINESE_FONT_NAME

        scroll_view = MDScrollView()
        display_list = MDList()

        help_text = [
            "1. 如何添加商品到购物车？\n   - 在商品浏览页面点击\"加入购物车\"按钮",
            "2. 如何查看历史订单？\n   - 在主页面点击\"订单管理\"",
            "3. 如何管理用户账号？\n   - 在主页点击\"个人中心\"，可以添加/编辑/删除用户信息",
            "4. 如何修改个人信息？\n   - 在个人中心点击\"修改个人信息\"",
            "5. 如何退出登录？\n   - 在主页或个人中心都有退出登录选项",
        ]

        for ss in help_text:
            lbl = MDLabel(
                text=ss,
                theme_text_color="Primary",
                halign="left",
                valign="top",
                size_hint_y=None,
                padding=(dp(8), dp(6))
            )
            lbl.bind(
                width=lambda inst, w: setattr(inst, 'text_size', (w, None)),
                texture_size=lambda inst, ts: setattr(inst, 'height', max(ts[1], dp(20)))
            )
            display_list.add_widget(lbl)
        scroll_view.add_widget(display_list)
        dialog.content_cls.add_widget(scroll_view)

        dialog.open()

    def show_feedback(self, *args):
        """显示反馈建议"""
        dialog = MDDialog(
            title="反馈建议",
            type="custom",
            size_hint_x=0.9,
            background_color=(0, 0, 0, 0),
            content_cls=MDBoxLayout(
                orientation='vertical',
                spacing=dp(10),
                size_hint_y=None,
                height=dp(250)
            ),
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="提交",
                    on_release=lambda x: self.submit_feedback(dialog)
                )
            ]
        )
        dialog.ids.title.font_name = CHINESE_FONT_NAME

        self.feedback_input = MDTextField(
            hint_text="请输入您的反馈建议",
            multiline=True
        )
        self.feedback_input.font_name_hint_text = CHINESE_FONT_NAME

        dialog.content_cls.add_widget(MDLabel(
            text="我们非常重视您的反馈，请告诉我们您的建议：",
            theme_text_color="Primary"
        ))

        dialog.content_cls.add_widget(self.feedback_input)

        dialog.open()

    def submit_feedback(self, dialog):
        """提交反馈"""
        feedback = self.feedback_input.text.strip()

        if not feedback:
            MDSnackbar(MDLabel(text="请输入反馈内容", theme_text_color="Custom", text_color=(0.9, 0.2, 0.2, 1))).open()
            return

        dialog.dismiss()

        # 保存到服务器或本地文件，示例：保存到本地文件
        try:
            data_file = str(Path(__file__).parent.parent) + "/data/feedback.txt"
            with open(data_file, "a", encoding="utf-8") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] {feedback}\n")
        except:
            pass

        MDSnackbar(MDLabel(text="感谢您的反馈！", theme_text_color="Custom", text_color=(0.2, 0.8, 0.2, 1))).open()

    def open_settings(self, *args):
        """打开设置"""
        # 直接跳转到设置部分
        MDSnackbar(
            MDLabel(text="请使用下方的设置选项", theme_text_color="Custom", text_color=(0.2, 0.6, 0.86, 1))).open()

    def logout(self, *args):
        """退出登录"""
        app = App.get_running_app()

        if not app.current_user:
            MDSnackbar(MDLabel(text="您还没有登录", theme_text_color="Custom", text_color=(0.9, 0.2, 0.2, 1))).open()
            return

        dialog = MDDialog(
            title="退出登录",
            size_hint_x=0.9,
            background_color=(0, 0, 0, 0),
            text=f"确定要退出登录吗？\n当前用户：{app.current_user['name']}",
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="确定",
                    md_bg_color=(0.9, 0.2, 0.2, 1),
                    on_release=lambda x: self.confirm_logout(dialog)
                )
            ]
        )
        dialog.ids.title.font_name = CHINESE_FONT_NAME
        dialog.open()

    def confirm_logout(self, dialog):
        """确认退出登录"""
        dialog.dismiss()

        app = App.get_running_app()
        app.current_user = None
        app.cart.clear()
        app.show_login()  # 返回登录页

    def go_back(self):
        """返回主页"""
        app = App.get_running_app()
        app.show_home()


    # ==================== 蓝牙打印机 ====================

    def show_bluetooth_printer_dialog(self, *args):
        """显示蓝牙打印机连接对话框"""
        app = App.get_running_app()
        mgr = app.bluetooth_printer_manager

        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(480)
        )

        # 状态卡片（动态高度，文字过长自动换行扩展）
        self._printer_status_card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            padding=dp(10),
            spacing=dp(5),
            elevation=dp(2),
            radius=[dp(10)]
        )
        self._printer_status_card.bind(minimum_height=self._printer_status_card.setter('height'))

        self._printer_status_label = MDLabel(
            text="状态: 未连接",
            theme_text_color="Secondary",
            font_style="Subtitle1",
            size_hint_y=None
        )
        self._printer_status_label.bind(
            width=lambda instance, value: setattr(instance, 'text_size', (value, None)),
            texture_size=lambda instance, value: setattr(instance, 'height', value[1])
        )

        self._printer_device_label = MDLabel(
            text="设备: 无",
            theme_text_color="Hint",
            font_style="Caption",
            size_hint_y=None
        )
        self._printer_device_label.bind(
            width=lambda instance, value: setattr(instance, 'text_size', (value, None)),
            texture_size=lambda instance, value: setattr(instance, 'height', value[1])
        )

        self._printer_status_card.add_widget(self._printer_status_label)
        self._printer_status_card.add_widget(self._printer_device_label)
        content.add_widget(self._printer_status_card)

        # 操作按钮行
        actions_row = MDBoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(50),
            spacing=dp(10)
        )
        self._scan_btn = MDRaisedButton(
            text="扫描设备",
            size_hint=(0.5, 1),
            md_bg_color=(0.2, 0.6, 0.86, 1)
        )
        self._scan_btn.bind(on_release=self._start_scan_printers)
        self._disconnect_btn = MDRaisedButton(
            text="断开连接",
            size_hint=(0.5, 1),
            md_bg_color=(0.9, 0.3, 0.3, 1)
        )
        self._disconnect_btn.bind(on_release=self._disconnect_printer)
        actions_row.add_widget(self._scan_btn)
        actions_row.add_widget(self._disconnect_btn)
        content.add_widget(actions_row)

        # 设备列表
        self._printer_scroll = MDScrollView(size_hint=(1, 1))
        self._printer_device_list = MDList(size_hint_y=None)
        self._printer_device_list.bind(minimum_height=self._printer_device_list.setter('height'))
        self._printer_scroll.add_widget(self._printer_device_list)
        content.add_widget(self._printer_scroll)

        self.bluetooth_printer_dialog = MDDialog(
            title="连接蓝牙打印机",
            type="custom",
            size_hint_x=0.9,
            background_color=(0, 0, 0, 0),
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="关闭",
                    on_release=lambda x: self.bluetooth_printer_dialog.dismiss()
                )
            ]
        )
        self.bluetooth_printer_dialog.ids.title.font_name = CHINESE_FONT_NAME

        # 注册状态回调
        mgr.set_state_callback(self._on_printer_state_changed)

        # 初始化显示当前状态
        self._update_printer_dialog_state(mgr.connection_state, mgr.connected_device, mgr.last_error)

        self.bluetooth_printer_dialog.open()

    def _on_printer_state_changed(self, state, device_info, error_msg):
        """蓝牙打印机状态变更回调（在主线程执行）"""
        def _update(dt):
            self._update_printer_dialog_state(state, device_info, error_msg)
        Clock.schedule_once(_update, 0)

    def _update_printer_dialog_state(self, state, device_info, error_msg):
        """更新对话框中的状态显示"""
        state_text_map = {
            "disconnected": "状态: 未连接",
            "scanning": "状态: 正在扫描...",
            "connecting": "状态: 正在连接...",
            "connected": "状态: 已连接",
            "error": f"状态: 错误 - {error_msg or '未知错误'}",
        }
        status_text = state_text_map.get(state, f"状态: {state}")
        self._printer_status_label.text = status_text

        if device_info and state == "connected":
            self._printer_device_label.text = f"设备: {device_info.get('name', 'Unknown')} ({device_info.get('address', '')})"
            self._printer_device_label.theme_text_color = "Custom"
            self._printer_device_label.text_color = (0.2, 0.8, 0.2, 1)
        elif state == "scanning":
            self._printer_device_label.text = "正在搜索附近的蓝牙设备..."
            self._printer_device_label.theme_text_color = "Hint"
        else:
            self._printer_device_label.text = "设备: 无"
            self._printer_device_label.theme_text_color = "Hint"

        # 按钮状态
        self._scan_btn.disabled = (state == "scanning" or state == "connecting")
        self._disconnect_btn.disabled = (state != "connected")

    def _start_scan_printers(self, *args):
        """开始扫描蓝牙打印机设备"""
        app = App.get_running_app()
        mgr = app.bluetooth_printer_manager

        self._printer_device_list.clear_widgets()
        self._printer_device_list.add_widget(
            OneLineListItem(text="正在准备扫描...", theme_text_color="Hint")
        )

        def _do_scan():
            """执行实际扫描"""
            # 检查蓝牙是否开启（仅 Android）
            if platform == 'android':
                bt_enabled = self._is_android_bluetooth_enabled()
                if not bt_enabled:
                    self._printer_device_list.clear_widgets()
                    self._printer_device_list.add_widget(
                        OneLineListItem(
                            text="请先开启手机蓝牙后再扫描",
                            theme_text_color="Error"
                        )
                    )
                    MDSnackbar(
                        MDLabel(text="请先开启手机蓝牙", theme_text_color="Custom",
                                text_color=(0.9, 0.2, 0.2, 1))
                    ).open()
                    return

            self._printer_device_list.clear_widgets()
            self._printer_device_list.add_widget(
                OneLineListItem(text="正在扫描...", theme_text_color="Hint")
            )

            def _on_found(devices):
                self._printer_device_list.clear_widgets()
                if not devices:
                    self._printer_device_list.add_widget(
                        OneLineListItem(
                            text="未发现已配对设备\n请先在系统设置中配对打印机",
                            theme_text_color="Hint"
                        )
                    )
                    return
                for dev in devices:
                    name = dev.get('name', 'Unknown')
                    addr = dev.get('address', '')
                    paired_str = " [已配对]" if dev.get('paired') else ""
                    item = TwoLineIconListItem(
                        text=f"{name}{paired_str}",
                        secondary_text=addr,
                        on_release=lambda x, d=dev: self._connect_printer(d)
                    )
                    item.add_widget(IconLeftWidget(icon="printer"))
                    self._printer_device_list.add_widget(item)

            mgr.scan_devices(on_devices_found=_on_found)

        # Android 需要先请求运行时权限
        if platform == 'android':
            self._request_bluetooth_permissions(on_granted=_do_scan)
        else:
            _do_scan()

    def _request_bluetooth_permissions(self, on_granted):
        """请求 Android 蓝牙相关运行时权限"""
        if platform != 'android':
            on_granted()
            return

        try:
            from android.permissions import request_permissions
            try:
                from android.permissions import check_permission
            except ImportError:
                check_permission = None
            from jnius import autoclass
            # Build.VERSION 是静态嵌套类，pyjnius 中需用 $ 访问
            Build_VERSION = autoclass('android.os.Build$VERSION')
            sdk_int = Build_VERSION.SDK_INT

            # Android 12+ (API 31) 需要 BLUETOOTH_SCAN / BLUETOOTH_CONNECT
            # Android 6-11 需要 ACCESS_FINE_LOCATION 才能扫描
            if sdk_int >= 31:
                perms = [
                    'android.permission.BLUETOOTH_SCAN',
                    'android.permission.BLUETOOTH_CONNECT',
                ]
            else:
                perms = [
                    'android.permission.ACCESS_FINE_LOCATION',
                ]

            # 检查是否已有权限
            all_granted = True
            if check_permission:
                for perm in perms:
                    if not check_permission(perm):
                        all_granted = False
                        break
            else:
                all_granted = False

            if all_granted:
                on_granted()
                return

            def _callback(*args):
                # 兼容不同版本 p4a 的回调格式: (permissions, grants) 或 (permissions_dict,)
                granted = False
                if len(args) == 2:
                    permissions, grants = args
                    granted = all(grants)
                elif len(args) == 1 and isinstance(args[0], dict):
                    granted = all(args[0].values())
                elif len(args) == 1 and isinstance(args[0], (list, tuple)):
                    granted = all(args[0])

                if granted:
                    on_granted()
                else:
                    self._printer_device_list.clear_widgets()
                    self._printer_device_list.add_widget(
                        OneLineListItem(
                            text="权限被拒绝，无法扫描蓝牙设备",
                            theme_text_color="Error"
                        )
                    )
                    MDSnackbar(
                        MDLabel(text="需要蓝牙权限才能扫描设备", theme_text_color="Custom",
                                text_color=(0.9, 0.2, 0.2, 1))
                    ).open()

            request_permissions(perms, _callback)
        except Exception as e:
            Logger.error(f"BluetoothPrinter: 请求权限失败: {e}")
            # 降级处理：直接尝试扫描
            on_granted()

    def _is_android_bluetooth_enabled(self):
        """检查 Android 蓝牙是否开启"""
        try:
            from jnius import autoclass
            BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
            adapter = BluetoothAdapter.getDefaultAdapter()
            return adapter is not None and adapter.isEnabled()
        except Exception as e:
            Logger.error(f"BluetoothPrinter: 检查蓝牙状态失败: {e}")
            return False

    def _connect_printer(self, device_info):
        """连接选中的蓝牙打印机"""
        app = App.get_running_app()
        mgr = app.bluetooth_printer_manager

        self._printer_device_list.clear_widgets()
        self._printer_device_list.add_widget(
            OneLineListItem(
                text=f"正在连接 {device_info.get('name', '')}...",
                theme_text_color="Hint"
            )
        )

        def _on_result(success, error_msg):
            if not success:
                self._printer_device_list.clear_widgets()
                self._printer_device_list.add_widget(
                    OneLineListItem(
                        text=f"连接失败: {error_msg or '未知错误'}",
                        theme_text_color="Error"
                    )
                )
            else:
                self._printer_device_list.clear_widgets()
                self._printer_device_list.add_widget(
                    OneLineListItem(
                        text=f"已连接: {device_info.get('name', '')}",
                        theme_text_color="Custom"
                    )
                )
                # 更新个人中心菜单项文字
                self.bluetooth_printer_item.text = f"蓝牙打印机: {device_info.get('name', '已连接')}"

        mgr.connect(device_info, on_result=_on_result)

    def _disconnect_printer(self, *args):
        """断开蓝牙打印机连接"""
        app = App.get_running_app()
        mgr = app.bluetooth_printer_manager
        mgr.disconnect()
        self.bluetooth_printer_item.text = "连接蓝牙打印机"
        self._printer_device_list.clear_widgets()
        self._printer_device_list.add_widget(
            OneLineListItem(text="已断开连接", theme_text_color="Hint")
        )


    # ==================== 数据迁移 ====================

    def show_data_migration_dialog(self, *args):
        """显示数据迁移对话框"""
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(200)
        )

        export_btn = MDRaisedButton(
            text="更新APP前，导出所有数据",
            size_hint=(1, None),
            height=dp(50),
            md_bg_color=(0.2, 0.6, 0.86, 1)
        )
        export_btn.bind(on_release=lambda x: self._show_export_dialog())
        export_btn.font_name = CHINESE_FONT_NAME

        import_btn = MDRaisedButton(
            text="更新APP后，导入历史数据",
            size_hint=(1, None),
            height=dp(50),
            md_bg_color=(0.2, 0.8, 0.4, 1)
        )
        import_btn.bind(on_release=lambda x: self._show_import_dialog())
        import_btn.font_name = CHINESE_FONT_NAME

        content.add_widget(export_btn)
        content.add_widget(import_btn)

        self.data_migration_dialog = MDDialog(
            title="数据迁移",
            type="custom",
            size_hint_x=0.9,
            background_color=(0, 0, 0, 0),
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="关闭",
                    on_release=lambda x: self.data_migration_dialog.dismiss()
                )
            ]
        )
        self.data_migration_dialog.ids.title.font_name = CHINESE_FONT_NAME
        self.data_migration_dialog.open()

    def _show_export_dialog(self):
        """显示导出数据对话框"""
        if hasattr(self, 'data_migration_dialog') and self.data_migration_dialog:
            self.data_migration_dialog.dismiss()

        self.export_checkboxes = {}

        scroll = MDScrollView(size_hint=(1, 1))
        export_list = MDList(size_hint_y=None)
        export_list.bind(minimum_height=export_list.setter('height'))

        export_items = [
            ("categories", "类别信息"),
            ("products", "商品信息"),
            ("orders", "订单信息"),
            ("users", "用户信息"),
            ("assets", "字体和图片"),
        ]

        for key, label in export_items:
            row = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(48),
                spacing=dp(5)
            )
            cb = MDCheckbox(
                size_hint=(None, None),
                size=(dp(48), dp(48)),
                active=False
            )
            lbl = MDLabel(
                text=label,
                valign='center',
                theme_text_color="Primary"
            )
            lbl.font_name = CHINESE_FONT_NAME
            row.add_widget(cb)
            row.add_widget(lbl)
            export_list.add_widget(row)
            self.export_checkboxes[key] = cb

        scroll.add_widget(export_list)

        content = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(360)
        )
        content.add_widget(scroll)

        self.export_dialog = MDDialog(
            title="导出数据",
            type="custom",
            size_hint_x=0.9,
            background_color=(0, 0, 0, 0),
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="全部勾选",
                    on_release=lambda x: self._export_select_all()
                ),
                MDRaisedButton(
                    text="一键导出",
                    md_bg_color=(0.2, 0.6, 0.86, 1),
                    on_release=lambda x: self._do_export()
                ),
                MDFlatButton(
                    text="关闭",
                    on_release=lambda x: self.export_dialog.dismiss()
                )
            ]
        )
        self.export_dialog.ids.title.font_name = CHINESE_FONT_NAME
        self.export_dialog.open()

    def _export_select_all(self):
        """全部勾选"""
        for cb in self.export_checkboxes.values():
            cb.active = True

    def _do_export(self):
        """执行导出"""
        try:
            project_root = str(Path(__file__).parent.parent)

            item_map = {
                'categories': ('data/categories.json', os.path.join(project_root, 'data', 'categories.json')),
                'products': ('data/products.json', os.path.join(project_root, 'data', 'products.json')),
                'orders': ('data/orders.json', os.path.join(project_root, 'data', 'orders.json')),
                'users': ('data/users.json', os.path.join(project_root, 'data', 'users.json')),
                'assets': ('screens/assets', os.path.join(project_root, 'screens', 'assets')),
            }

            selected_items = []
            for key, cb in self.export_checkboxes.items():
                if cb.active:
                    selected_items.append(item_map[key])

            if not selected_items:
                MDSnackbar(
                    MDLabel(text="请至少选择一项数据", theme_text_color="Custom", text_color=(0.9, 0.2, 0.2, 1))
                ).open()
                return

            # 创建临时 zip
            tmp_zip = tempfile.mktemp(suffix='.zip')
            Logger.info(f"Export: 创建临时zip: {tmp_zip}")
            try:
                with zipfile.ZipFile(tmp_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for arcname, src_path in selected_items:
                        if os.path.isdir(src_path):
                            for root, dirs, files in os.walk(src_path):
                                for file in files:
                                    if file.endswith('.pyc') or '__pycache__' in root:
                                        continue
                                    file_path = os.path.join(root, file)
                                    rel_path = os.path.relpath(file_path, project_root)
                                    zf.write(file_path, rel_path)
                        elif os.path.isfile(src_path):
                            rel_path = os.path.relpath(src_path, project_root)
                            zf.write(src_path, rel_path)
            except Exception as e:
                Logger.error(f"Export: 创建zip失败: {e}")
                MDSnackbar(
                    MDLabel(text=f"打包失败: {e}", theme_text_color="Custom", text_color=(0.9, 0.2, 0.2, 1))
                ).open()
                return

            self._pending_export_zip = tmp_zip

            def _start_save():
                default_name = f"shoppingcart_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                if platform == 'android':
                    # Android 上 plyer.filechooser.save_file 不可靠，直接保存到 Download 目录
                    self._android_direct_save(tmp_zip, default_name)
                else:
                    try:
                        from plyer import filechooser
                        filechooser.save_file(
                            title="保存数据备份",
                            filters=[["ZIP压缩包", "*.zip"]],
                            path=default_name,
                            on_selection=self._on_export_save
                        )
                        Logger.info("Export: filechooser.save_file 已调用")
                    except Exception as e:
                        Logger.error(f"Export: 文件选择器失败: {e}")
                        self._android_direct_save(tmp_zip)

            if platform == 'android':
                self._request_storage_permission(_start_save)
            else:
                _start_save()

        except Exception as e:
            Logger.error(f"Export: 导出异常: {e}")
            Logger.error(traceback.format_exc())
            MDSnackbar(
                MDLabel(text=f"导出失败: {e}", theme_text_color="Custom", text_color=(0.9, 0.2, 0.2, 1))
            ).open()

    def _request_storage_permission(self, on_granted):
        """请求 Android 存储权限"""
        if platform != 'android':
            on_granted()
            return
        try:
            from android.permissions import request_permissions, Permission, check_permission
            perm = Permission.WRITE_EXTERNAL_STORAGE
            if check_permission(perm):
                on_granted()
                return

            def callback(permissions, grants):
                if grants and all(grants):
                    on_granted()
                else:
                    MDSnackbar(
                        MDLabel(text="需要存储权限才能导出数据", text_color=(0.9, 0.2, 0.2, 1))
                    ).open()

            request_permissions([perm], callback)
        except Exception as e:
            Logger.error(f"Export: 请求权限失败: {e}")
            on_granted()

    def _android_direct_save(self, tmp_zip, filename=None):
        """Android 直接保存 / PC 降级保存（直接保存到默认路径）"""
        try:
            app = App.get_running_app()
            if platform == 'android':
                try:
                    from android.storage import primary_external_storage_path
                    download_dir = os.path.join(primary_external_storage_path(), 'Download')
                except Exception:
                    download_dir = app.user_data_dir
            else:
                download_dir = str(Path(__file__).parent.parent)

            os.makedirs(download_dir, exist_ok=True)
            if filename is None:
                filename = f"shoppingcart_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            default_path = os.path.join(download_dir, filename)
            shutil.copy(tmp_zip, default_path)
            MDSnackbar(
                MDLabel(text=f"已保存到: {default_path}", theme_text_color="Custom", text_color=(0.2, 0.8, 0.2, 1))
            ).open()
            if hasattr(self, 'export_dialog') and self.export_dialog:
                self.export_dialog.dismiss()
        except Exception as e:
            Logger.error(f"Export: 降级保存也失败: {e}")
            MDSnackbar(
                MDLabel(text=f"保存失败: {e}", theme_text_color="Custom", text_color=(0.9, 0.2, 0.2, 1))
            ).open()
        finally:
            try:
                os.remove(tmp_zip)
            except:
                pass
            self._pending_export_zip = None

    def _on_export_save(self, selection):
        """导出保存回调"""
        tmp_zip = getattr(self, '_pending_export_zip', None)
        if not tmp_zip or not os.path.exists(tmp_zip):
            Logger.warning("Export: 临时zip不存在，跳过保存")
            return

        if not selection:
            Logger.info("Export: 用户取消保存")
            try:
                os.remove(tmp_zip)
            except:
                pass
            self._pending_export_zip = None
            return

        target_path = selection[0]
        if not target_path.endswith('.zip'):
            target_path += '.zip'

        try:
            shutil.copy(tmp_zip, target_path)
            MDSnackbar(
                MDLabel(text=f"导出成功: {target_path}", theme_text_color="Custom", text_color=(0.2, 0.8, 0.2, 1))
            ).open()
            if hasattr(self, 'export_dialog') and self.export_dialog:
                self.export_dialog.dismiss()
        except Exception as e:
            Logger.error(f"Export: 保存失败: {e}")
            MDSnackbar(
                MDLabel(text=f"保存失败: {e}", theme_text_color="Custom", text_color=(0.9, 0.2, 0.2, 1))
            ).open()
        finally:
            try:
                os.remove(tmp_zip)
            except:
                pass
            self._pending_export_zip = None

    def _show_import_dialog(self):
        """显示导入对话框"""
        if hasattr(self, 'data_migration_dialog') and self.data_migration_dialog:
            self.data_migration_dialog.dismiss()

        if platform == 'android':
            # Android 上 plyer.filechooser.open_file 回调不可靠，改用目录扫描
            self._request_storage_permission(self._show_android_import_picker)
        else:
            try:
                from plyer import filechooser
                filechooser.open_file(
                    title="选择数据备份",
                    filters=[["ZIP压缩包", "*.zip"]],
                    on_selection=self._on_import_selection
                )
            except Exception as e:
                Logger.error(f"Import: 文件选择器失败: {e}")
                MDSnackbar(
                    MDLabel(text="无法打开文件选择器", theme_text_color="Custom", text_color=(0.9, 0.2, 0.2, 1))
                ).open()

    def _show_android_import_picker(self):
        """Android 端扫描 Download 目录中的 zip 并显示列表供选择"""
        try:
            from android.storage import primary_external_storage_path
            download_dir = os.path.join(primary_external_storage_path(), 'Download')
        except Exception:
            download_dir = App.get_running_app().user_data_dir

        zip_files = []

        def _scan_single_level(path):
            if os.path.isdir(path):
                try:
                    for f in os.listdir(path):
                        if f.lower().endswith('.zip'):
                            full = os.path.join(path, f)
                            if os.path.isfile(full):
                                zip_files.append(full)
                except Exception as e:
                    Logger.warning(f"Import: 扫描目录失败 {path}: {e}")

        # 只扫描单层目录，避免 os.walk 递归导致卡顿
        _scan_single_level(download_dir)
        _scan_single_level(os.path.join(download_dir, 'ShoppingCart'))

        if not zip_files:
            MDSnackbar(
                MDLabel(text=f"未在 {download_dir} 中找到 ZIP 备份文件", 
                        theme_text_color="Custom", text_color=(0.9, 0.2, 0.2, 1))
            ).open()
            return

        content = MDBoxLayout(orientation='vertical', size_hint_y=None, height=dp(360))
        scroll = MDScrollView()
        file_list = MDList(size_hint_y=None)
        file_list.bind(minimum_height=file_list.setter('height'))

        for path in zip_files:
            filename = os.path.basename(path)
            # 解析文件名中的时间戳，副标题显示导出时间
            secondary = path
            if filename.startswith('shoppingcart_backup_') and filename.endswith('.zip'):
                time_part = filename[len('shoppingcart_backup_'):-4]
                try:
                    dt = datetime.strptime(time_part, '%Y%m%d_%H%M%S')
                    secondary = f"导出时间: {dt.strftime('%Y-%m-%d %H:%M:%S')}"
                except ValueError:
                    pass

            card = MDCard(
                orientation='vertical',
                size_hint_y=None,
                height=dp(80),
                padding=(dp(10), dp(8)),
                spacing=dp(4),
                ripple_behavior=True,
                md_bg_color=(0.95, 0.95, 0.95, 1)
            )
            card.bind(on_release=lambda x, p=path: self._on_android_import_selected(p))

            name_lbl = MDLabel(
                text=filename,
                font_size=sp(13),
                theme_text_color="Primary",
                size_hint_y=None
            )
            name_lbl.bind(
                width=lambda inst, val: setattr(inst, 'text_size', (val, None)),
                texture_size=lambda inst, val: setattr(inst, 'height', val[1])
            )
            time_lbl = MDLabel(
                text=secondary,
                font_size=sp(12),
                theme_text_color="Secondary",
                size_hint_y=None
            )
            time_lbl.bind(
                width=lambda inst, val: setattr(inst, 'text_size', (val, None)),
                texture_size=lambda inst, val: setattr(inst, 'height', val[1])
            )
            card.add_widget(name_lbl)
            card.add_widget(time_lbl)
            file_list.add_widget(card)

        scroll.add_widget(file_list)
        content.add_widget(scroll)

        self.import_picker_dialog = MDDialog(
            title="选择备份文件",
            type="custom",
            size_hint_x=0.95,
            background_color=(0, 0, 0, 0),
            content_cls=content,
            buttons=[
                MDFlatButton(text="关闭", on_release=lambda x: self.import_picker_dialog.dismiss())
            ]
        )
        self.import_picker_dialog.ids.title.font_name = CHINESE_FONT_NAME
        self.import_picker_dialog.open()

    def _on_android_import_selected(self, zip_path):
        if hasattr(self, 'import_picker_dialog') and self.import_picker_dialog:
            self.import_picker_dialog.dismiss()
        Logger.info(f"Import: Android 选择文件 {zip_path}")
        self._on_import_selection([zip_path])

    def _resolve_android_uri(self, uri):
        """将 Android content:// URI 复制到临时文件，返回真实路径"""
        if not uri.startswith('content://'):
            return uri
        try:
            from jnius import autoclass
            from android import mActivity
            uri_obj = autoclass('android.net.Uri').parse(uri)
            resolver = mActivity.getContentResolver()
            input_stream = resolver.openInputStream(uri_obj)
            tmp_file = tempfile.mktemp(suffix='.zip')
            with open(tmp_file, 'wb') as f:
                buffer = bytearray(4096)
                while True:
                    read = input_stream.read(buffer)
                    if read == -1:
                        break
                    f.write(buffer[:read])
            input_stream.close()
            Logger.info(f"Import: content URI 已复制到临时文件: {tmp_file}")
            return tmp_file
        except Exception as e:
            Logger.error(f"Import: 无法解析 URI {uri}: {e}")
            return uri

    def _show_import_result_dialog(self, success, message):
        """显示导入结果 Dialog（手动关闭，不会自动消失）"""
        content = MDBoxLayout(orientation='vertical', size_hint_y=None)
        lbl = MDLabel(
            text=message,
            theme_text_color="Primary",
            size_hint_y=None,
            valign="top"
        )
        lbl.bind(
            width=lambda inst, val: setattr(inst, 'text_size', (val, None)),
            texture_size=lambda inst, val: setattr(inst, 'height', val[1])
        )
        content.add_widget(lbl)
        content.bind(minimum_height=content.setter('height'))

        dialog = MDDialog(
            title="导入成功" if success else "导入失败",
            type="custom",
            size_hint_x=0.9,
            background_color=(0, 0, 0, 0),
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="关闭",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.ids.title.font_name = CHINESE_FONT_NAME
        dialog.open()

    def _robust_copy(self, src, dst):
        """健壮的文件复制：若目标被占用，先重命名为 .bak 再覆盖"""
        try:
            shutil.copy2(src, dst)
            return True
        except (PermissionError, OSError):
            try:
                bak = dst + '.bak'
                if os.path.exists(bak):
                    os.remove(bak)
                os.rename(dst, bak)
                shutil.copy2(src, dst)
                try:
                    os.remove(bak)
                except Exception:
                    pass
                return True
            except Exception as e:
                Logger.warning(f"Import: 无法复制 {os.path.basename(dst)}: {e}")
                return False

    def _on_import_selection(self, selection):
        """导入选择回调"""
        Logger.info(f"Import: _on_import_selection 被调用, selection={selection}")
        if not selection:
            MDSnackbar(
                MDLabel(text="未选择文件", theme_text_color="Custom", text_color=(0.9, 0.2, 0.2, 1))
            ).open()
            return

        zip_path = selection[0]
        Logger.info(f"Import: 选择的路径: {zip_path}")

        # Android content URI 处理
        if platform == 'android':
            zip_path = self._resolve_android_uri(zip_path)

        if not os.path.exists(zip_path):
            MDSnackbar(
                MDLabel(text=f"文件不存在或无法访问: {zip_path}", theme_text_color="Custom",
                        text_color=(0.9, 0.2, 0.2, 1))
            ).open()
            return

        project_root = str(Path(__file__).parent.parent)

        tmp_dir = tempfile.mkdtemp()
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(tmp_dir)

            # 查找 data 和 screens/assets 目录
            data_src = None
            assets_src = None

            root_data = os.path.join(tmp_dir, 'data')
            root_screens = os.path.join(tmp_dir, 'screens')
            if os.path.isdir(root_data) and os.path.isdir(root_screens):
                data_src = root_data
                assets_src = os.path.join(root_screens, 'assets')
            else:
                for entry in os.listdir(tmp_dir):
                    entry_path = os.path.join(tmp_dir, entry)
                    if os.path.isdir(entry_path):
                        candidate_data = os.path.join(entry_path, 'data')
                        candidate_screens = os.path.join(entry_path, 'screens')
                        if os.path.isdir(candidate_data) and os.path.isdir(candidate_screens):
                            data_src = candidate_data
                            assets_src = os.path.join(candidate_screens, 'assets')
                            break

            if not data_src or not os.path.isdir(data_src):
                MDSnackbar(
                    MDLabel(text="备份文件格式不正确：未找到 data 目录", theme_text_color="Custom",
                            text_color=(0.9, 0.2, 0.2, 1))
                ).open()
                return

            # 复制 data 文件（健壮复制：被占用时先重命名 .bak 再覆盖）
            data_dst = os.path.join(project_root, 'data')
            os.makedirs(data_dst, exist_ok=True)
            skipped_data = []
            for filename in os.listdir(data_src):
                src_file = os.path.join(data_src, filename)
                dst_file = os.path.join(data_dst, filename)
                if os.path.isfile(src_file):
                    if not self._robust_copy(src_file, dst_file):
                        skipped_data.append(filename)

            # 复制 assets（健壮复制：被占用时先重命名 .bak 再覆盖）
            skipped_assets = []
            if assets_src and os.path.isdir(assets_src):
                assets_dst = os.path.join(project_root, 'screens', 'assets')
                os.makedirs(assets_dst, exist_ok=True)

                def _safe_copy_tree(src, dst, skip_list):
                    for item in os.listdir(src):
                        if item == '__pycache__':
                            continue
                        s = os.path.join(src, item)
                        d = os.path.join(dst, item)
                        if os.path.isdir(s):
                            if not os.path.exists(d):
                                os.makedirs(d, exist_ok=True)
                            _safe_copy_tree(s, d, skip_list)
                        else:
                            if not self._robust_copy(s, d):
                                rel_path = os.path.relpath(s, src)
                                skip_list.append(rel_path)

                _safe_copy_tree(assets_src, assets_dst, skipped_assets)

            # 重新加载数据
            app = App.get_running_app()
            if hasattr(app, 'db') and app.db:
                app.db.products = app.db.load_product_info()
            if hasattr(app, 'order_manager') and app.order_manager:
                app.order_manager.orders = app.order_manager.load_orders()
            if hasattr(app, 'inventory_manager') and app.inventory_manager:
                app.inventory_manager.categories = app.inventory_manager.load_categories()
            if hasattr(app, 'user_manager') and app.user_manager:
                app.user_manager.users = app.user_manager._load_users()
                # 如果当前用户已登录，更新当前用户信息
                if app.current_user:
                    for u in app.user_manager.users:
                        if u.get('phone') == app.current_user.get('phone'):
                            app.current_user = u
                            break

            msg = "数据导入成功，应用已更新"
            if skipped_data or skipped_assets:
                details = []
                if skipped_data:
                    details.append(f"data: {', '.join(skipped_data)}")
                if skipped_assets:
                    details.append(f"assets: {', '.join(skipped_assets[:3])}{'...' if len(skipped_assets) > 3 else ''}")
                msg += f"\n(以下文件被跳过: {'; '.join(details)})"
            self._show_import_result_dialog(success=True, message=msg)

        except Exception as e:
            Logger.error(f"Import: 导入失败: {e}")
            Logger.error(traceback.format_exc())
            self._show_import_result_dialog(success=False, message=f"导入失败: {e}")
        finally:
            try:
                shutil.rmtree(tmp_dir)
            except:
                pass
