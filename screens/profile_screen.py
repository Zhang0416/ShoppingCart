from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.chip import MDChip
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.list import (MDList, OneLineListItem, OneLineIconListItem, TwoLineListItem, ThreeLineListItem,
                             IconLeftWidget, IconRightWidget, ThreeLineAvatarIconListItem)
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
from kivy.logger import Logger
from kivy.metrics import dp, sp
from datetime import datetime
from pathlib import Path
import json
import os
import glob
import re

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
        change_pwd_item.add_widget(IconLeftWidget(icon="lock"))

        # 修改信息
        change_info_item = OneLineIconListItem(
            text="修改个人信息",
            on_release=self.change_user_info
        )
        change_info_item.add_widget(IconLeftWidget(icon="account-edit"))

        # 收货地址
        address_item = OneLineIconListItem(
            text="收货地址管理",
            on_release=self.show_addresses
        )
        address_item.add_widget(IconLeftWidget(icon="map-marker"))

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
        data_management_item.add_widget(IconLeftWidget(icon="database"))

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
        self.menu_list.add_widget(settings_section)
        self.menu_list.add_widget(notification_item)
        self.menu_list.add_widget(theme_item)
        self.menu_list.add_widget(data_management_item)
        self.menu_list.add_widget(about_section)
        self.menu_list.add_widget(about_item)
        self.menu_list.add_widget(help_item)
        self.menu_list.add_widget(feedback_item)
        self.menu_list.add_widget(logout_item)

        scroll_view.add_widget(self.menu_list)

        main_layout.add_widget(toolbar)
        main_layout.add_widget(self.user_card)
        main_layout.add_widget(scroll_view)

        self.add_widget(main_layout)

    def on_enter(self):
        """进入页面时更新用户信息"""
        from kivy.app import App
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
        from kivy.app import App
        app = App.get_running_app()

        if not app.current_user:
            return

        dialog = MDDialog(
            title="用户信息",
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
            type="custom",
            content_cls=MDBoxLayout(orientation='vertical',
                                    spacing=10,
                                    size_hint_y=None,
                                    height=200),
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
            MDSnackbar(MDLabel(text="用户不存在", text_color=(0.6, 0.2, 0.2, 1))).open()
            return

        old_pwd = self.password_input['old'].text
        new_pwd = self.password_input['new'].text
        confirm_pwd = self.password_input['confirm'].text

        if not old_pwd or not new_pwd or not confirm_pwd:
            MDSnackbar(MDLabel(text="请填写所有字段", text_color=(0.9, 0.2, 0.2, 1))).open()
            return

        if old_pwd != user['password']:
            MDSnackbar(MDLabel(text="旧密码输入错误", text_color=(0.6, 0.2, 0.5, 1))).open()
            return

        if new_pwd != confirm_pwd:
            MDSnackbar(MDLabel(text="两次输入的新密码不一致", text_color=(0.9, 0.2, 0.2, 1))).open()
            return

        if len(new_pwd) < 6:
            MDSnackbar(MDLabel(text="密码长度至少6位", text_color=(0.9, 0.2, 0.2, 1))).open()
            return

        dialog.dismiss()

        # 保存新密码
        user['password'] = new_pwd

        from kivy.app import App
        app = App.get_running_app()
        app.user_manager.save_users()

        MDSnackbar(MDLabel(text="密码修改成功", theme_text_color='Custom', text_color=(0.2, 0.8, 0.2, 1)),
                   md_bg_color=(0.8, 0.8, 0.8, 1)).open()
        return

    def change_user_info(self, *args):
        """修改用户信息"""
        from kivy.app import App
        app = App.get_running_app()

        if not app.current_user:
            MDSnackbar(MDLabel(text="请先登录", text_color=(0.9, 0.2, 0.2, 1))).open()
            return

        dialog = MDDialog(
            title="修改个人信息",
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
            MDSnackbar(MDLabel(text="用户名不能为空", text_color=(0.9, 0.2, 0.2, 1))).open()
            return

        if not phone or len(phone) != 11 or not re.match(r'^1[3-9]\d{9}$', phone):
            MDSnackbar(MDLabel(text="手机号格式不正确", text_color=(0.9, 0.2, 0.2, 1))).open()
            return

        if "@" not in email:
            MDSnackbar(MDLabel(text="请正确填写邮箱名称与后缀", text_color=(0.9, 0.2, 0.2, 1))).open()
            return

        from kivy.app import App
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
            left_ = IconLeftWidget(icon=f"numeric-{i + 1}-circle", theme_text_color="Custom")  # 图标
            item = ThreeLineAvatarIconListItem(
                text=f"收货人：{addr['name']}",
                secondary_text=f"电话：{addr['phone']}",
                tertiary_text=f"地址：{addr['address']}",
                _txt_left_pad=dp(20)  # 删除icon空白
            )

            # 添加操作按钮
            item_layout = MDBoxLayout(
                orientation='horizontal',
                adaptive_height=True,
                size_hint=(None, None),
                size=(sp(120), sp(40)),
                spacing=0
            )

            edit_btn = MDIconButton(
                icon="pencil",
                size_hint=(None, None),
                size=(sp(40), sp(40)),
                theme_text_color="Hint",
                # md_bg_color=(0.1, 0.6, 0.3, 0.6)
            )
            edit_btn.bind(on_release=lambda x, idx=i: self.edit_address(idx))

            delete_btn = MDIconButton(
                icon="delete",
                size_hint=(None, None),
                size=(sp(40), sp(40)),
                theme_text_color="Error",
                pos_hint={'center_x': 0.0}
            )
            delete_btn.bind(on_release=lambda x, idx=i: self.delete_address(idx))

            item_layout.add_widget(edit_btn)
            item_layout.add_widget(delete_btn)
            right_ = IconRightWidget(icon="", )
            right_.add_widget(item_layout)

            # item.add_widget(left_)
            # item.add_widget(item_layout)
            item.add_widget(right_)
            address_list.add_widget(item)

        scroll_view.add_widget(address_list)

        """显示收货地址"""
        self.show_addr_dialog = MDDialog(
            title="收货地址管理",
            type="custom",
            content_cls=MDBoxLayout(
                orientation='vertical',
                spacing=dp(10),
                size_hint_y=None,
                height=dp(300)
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
                                     height=dp(300))
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
                                             height=dp(80))
        self.edit_cont['addr'].font_name_hint_text = CHINESE_FONT_NAME
        self.edit_cont['addr'].font_name = CHINESE_FONT_NAME
        content_layout.add_widget(self.edit_cont['name'])
        content_layout.add_widget(self.edit_cont['phone'])
        content_layout.add_widget(self.edit_cont['addr'])

        # 编辑对话框
        self.edit_dialog = MDDialog(
            title="编辑",
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

        from kivy.app import App
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

        from kivy.app import App
        app = App.get_running_app()
        app.user_manager.save_users()  # 保存
        self.show_addresses()
        return

    def show_new_address_dialog(self, *args):
        """显示新增地址对话框"""
        self.dialog = MDDialog(
            title="新增地址",
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
            MDSnackbar(MDLabel(text="地址中不能包含特殊字符'~'", text_color=(0.2, 0.8, 0.5, 1))).open()
            return
        MDSnackbar(MDLabel(text="新增地址成功", text_color=(0.2, 0.6, 0.86, 1))).open()

        # 检查用户是否存在
        user = self.search_current_user()
        if not user:
            return

        if len(user['usual_address']) >= 100:
            user['usual_address'].pop(0)
        user['usual_address'].append('~'.join([self.new_name.text, self.new_phone.text, self.new_address.text]))

        from kivy.app import App
        app = App.get_running_app()
        app.user_manager.save_users()  # 保存
        self.show_addresses()
        # app.show_profile()  # 返回
        return

    def search_current_user(self):
        from kivy.app import App
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
        from kivy.app import App
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

            MDSnackbar(MDLabel(text="缓存已清除", text_color=(0.2, 0.8, 0.2, 1))).open()
        except Exception as e:
            MDSnackbar(MDLabel(text=f"清除缓存失败: {str(e)}", text_color=(0.9, 0.2, 0.2, 1))).open()

    def show_about(self, *args):
        """显示关于信息"""
        dialog = MDDialog(
            title="关于购物商城",
            text="购物商城 v1.0\n\n"
                 "一个功能完整的移动购物应用\n"
                 "支持用户管理、商品浏览、购物车、订单管理等功能\n\n"
                 "开发者: ShoppingCart Team\n"
                 "联系方式: support@shoppingcart.com\n"
                 "官方网站: https://www.shoppingcart.com",
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
            """
                1. 如何添加商品到购物车？
                   - 在商品浏览页面点击"加入购物车"按钮
            """,
            """
                2. 如何查看历史订单？
                   - 在主页面点击"订单管理
            """,
            """
                3. 如何管理用户账号？
                   - 在主页点击"个人中心"，可以添加/编辑/删除用户信息
            """,
            """
                4. 如何修改个人信息？
                   - 在个人中心点击"修改个人信息"
            """,
            """
                5. 如何退出登录？
                   - 在主页或个人中心都有退出登录选项
            """
        ]

        for i, ss in enumerate(help_text):
            item = MDBoxLayout(orientation='vertical',
                               spacing=dp(10),
                               size_hint_y=None,
                               height=dp(100))
            item.add_widget(MDLabel(text=ss, theme_text_color="Primary"))
            display_list.add_widget(item)
        scroll_view.add_widget(display_list)
        dialog.content_cls.add_widget(scroll_view)

        dialog.open()

    def show_feedback(self, *args):
        """显示反馈建议"""
        dialog = MDDialog(
            title="反馈建议",
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
            MDSnackbar(MDLabel(text="请输入反馈内容", text_color=(0.9, 0.2, 0.2, 1))).open()
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

        MDSnackbar(MDLabel(text="感谢您的反馈！", text_color=(0.2, 0.8, 0.2, 1))).open()

    def open_settings(self, *args):
        """打开设置"""
        # 直接跳转到设置部分
        MDSnackbar(MDLabel(text="请使用下方的设置选项", text_color=(0.2, 0.6, 0.86, 1))).open()

    def logout(self, *args):
        """退出登录"""
        from kivy.app import App
        app = App.get_running_app()

        if not app.current_user:
            MDSnackbar(MDLabel(text="您还没有登录", text_color=(0.9, 0.2, 0.2, 1))).open()
            return

        dialog = MDDialog(
            title="退出登录",
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

        from kivy.app import App
        app = App.get_running_app()
        app.current_user = None
        app.cart.clear()
        app.show_home()  # 返回主页

    def go_back(self):
        """返回主页"""
        from kivy.app import App
        app = App.get_running_app()
        app.show_home()
