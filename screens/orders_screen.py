from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import (MDList, OneLineListItem, OneLineIconListItem, ThreeLineListItem,
                             ThreeLineAvatarIconListItem, IconLeftWidget, IconRightWidget)
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.chip import MDChip
from kivymd.uix.snackbar import MDSnackbar
from kivy.metrics import dp, sp
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.utils import platform
from plyer import filechooser
from kivy.clock import Clock

import json
import os
from kivymd.app import MDApp
from kivy.utils import platform
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.textfield import MDTextField
from kivymd.toast import toast

import csv
from datetime import datetime
from io import StringIO

from .assets.config_chinese import CHINESE_FONT_NAME


class OrdersScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "orders"
        self._build_ui()

    def _build_ui(self):
        # 主布局
        main_layout = MDBoxLayout(orientation='vertical')

        # 顶部工具栏
        toolbar = MDTopAppBar(
            title="订单/库存 详情",
            elevation=dp(4),
            md_bg_color=(0.2, 0.6, 0.86, 1),
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[["refresh", lambda x: self.refresh_orders()]]
        )

        # 功能列表
        scroll_view = MDScrollView()
        self.menu_list = MDList()

        # 订单管理区
        order_section = OneLineListItem(
            text="订单管理",
            theme_text_color="Primary",
            font_style="Headline6"
        )

        # 我的订单
        my_orders_item = OneLineIconListItem(
            text="我的订单",
            on_release=self.show_my_orders
        )
        my_orders_item.add_widget(IconLeftWidget(icon="cart"))

        # 历史订单
        history_orders_item = OneLineIconListItem(
            text="历史订单",
            on_release=self.show_history_orders
        )
        history_orders_item.add_widget(IconLeftWidget(icon="history"))

        # 库存管理区
        inventory_section = OneLineListItem(
            text="库存管理",
            theme_text_color="Primary",
            font_style="Headline6"
        )

        # 我的库存
        my_inventory_item = OneLineIconListItem(
            text="我的库存",
            on_release=self.show_my_inventory
        )
        my_inventory_item.add_widget(IconLeftWidget(icon="storefront"))

        self.menu_list.add_widget(order_section)
        self.menu_list.add_widget(my_orders_item)
        self.menu_list.add_widget(history_orders_item)
        self.menu_list.add_widget(inventory_section)
        self.menu_list.add_widget(my_inventory_item)

        scroll_view.add_widget(self.menu_list)

        main_layout.add_widget(toolbar)
        main_layout.add_widget(scroll_view)

        self.add_widget(main_layout)

    def on_enter(self):
        """进入页面时更新用户信息"""
        from kivy.app import App
        app = App.get_running_app()

    def show_my_orders(self, *args):
        """显示我的订单"""
        from kivy.app import App
        app = App.get_running_app()

        if not app.current_user:
            MDSnackbar(MDLabel(text="请先登录", text_color=(0.9, 0.2, 0.2, 1))).open()
            return

        # 获取当前用户的订单
        orders = app.order_manager.get_orders_by_user(app.current_user['phone'])

        if not orders:
            dialog = MDDialog(
                title="我的订单",
                text="暂无订单记录",
                buttons=[
                    MDFlatButton(
                        text="关闭",
                        on_release=lambda x: dialog.dismiss()
                    )
                ]
            )
            dialog.ids.title.font_name = CHINESE_FONT_NAME
            dialog.open()
            return

        # 创建订单列表对话框
        scroll_view = MDScrollView()
        order_list = MDList()

        for order in orders[:10][::-1]:  # 只显示最近10个订单
            time_str = datetime.fromisoformat(order.created_at).strftime("%Y-%m-%d %H:%M")
            item = ThreeLineAvatarIconListItem(
                text=f"订单号：{order.order_id[:20]}",
                secondary_text=f"收件人信息：{order.address}",  # | 状态：{self.get_status_text(order.status)}",
                tertiary_text=f"金额：¥{order.total:.1f} | 时间：{time_str}",
                _txt_left_pad=dp(10),  # 删除icon空白
                font_style='Subtitle2',
                secondary_font_style='Overline',
                tertiary_font_style='Overline'
            )
            item.bind(on_release=lambda x, o=order: self.show_order_detail(o))

            # # 添加操作按钮
            # extra_layout = MDBoxLayout(
            #     orientation='horizontal',
            #     adaptive_height=True,
            #     size_hint=(None, None),
            #     size=(sp(120), sp(40)),
            #     spacing=0
            # )
            #
            # delete_btn = MDIconButton(
            #     icon="delete",
            #     size_hint=(None, None),
            #     size=(sp(40), sp(40)),
            #     theme_text_color="Error",
            #     pos_hint={'center_x': 0.0}
            # )
            # delete_btn.bind(on_release=lambda x, o=order: self.delete_my_order(o))
            #
            # extra_layout.add_widget(delete_btn)
            # right_ = IconRightWidget(icon="", )
            # right_.add_widget(extra_layout)
            # item.add_widget(right_)

            order_list.add_widget(item)

        scroll_view.add_widget(order_list)

        self.my_order_dialog = MDDialog(
            title="我的订单",
            type="custom",
            size_hint_x=None,
            width=dp(360),
            content_cls=MDBoxLayout(
                orientation='vertical',
                spacing=dp(10),
                size_hint_y=None,
                height=dp(600)
            ),
            buttons=[
                MDFlatButton(
                    text="关闭",
                    on_release=lambda x: self.my_order_dialog.dismiss()
                )
            ]
        )
        self.my_order_dialog.ids.title.font_name = CHINESE_FONT_NAME

        # 添加筛选选项
        filter_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(50),
            spacing=dp(10)
        )

        statuses = ["全部", "待付款", "待发货", "待收货", "已完成"]
        for status in statuses:
            chip = MDChip(
                text=status,
                size_hint=(None, None),
                size=(sp(80), sp(30))
            )
            filter_layout.add_widget(chip)

        # dialog.content_cls.add_widget(filter_layout)
        self.my_order_dialog.content_cls.add_widget(scroll_view)
        self.my_order_dialog.open()

    def show_history_orders(self, *args):
        """显示历史订单"""
        from kivy.app import App
        app = App.get_running_app()

        if not app.current_user:
            MDSnackbar(MDLabel(text="请先登录", text_color=(0.9, 0.2, 0.2, 1))).open()
            return

        # 获取所有订单
        all_orders = app.order_manager.get_all_orders()

        if not all_orders:
            dialog = MDDialog(
                title="历史订单",
                text="暂无历史订单记录",
                buttons=[
                    MDFlatButton(
                        text="关闭",
                        on_release=lambda x: dialog.dismiss()
                    )
                ]
            )
            dialog.ids.title.font_name = CHINESE_FONT_NAME
            dialog.open()
            return

        # 创建订单统计
        total_orders = len(all_orders)
        total_amount = sum(order.total for order in all_orders)
        completed_orders = len([o for o in all_orders if o.status == "delivered"])

        # 创建对话框
        self.history_orders_dialog = MDDialog(
            title="历史订单统计",
            type="custom",
            size_hint_x=None,
            width=dp(360),
            content_cls=MDBoxLayout(
                orientation='vertical',
                spacing=dp(10),
                size_hint_y=None,
                height=dp(500)
            ),
            buttons=[
                MDFlatButton(
                    text="关闭",
                    on_release=lambda x: self.history_orders_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="查看详情",
                    on_release=lambda x: self.show_all_orders_detail()
                )
            ]
        )
        self.history_orders_dialog.ids.title.font_name = CHINESE_FONT_NAME

        # 统计信息
        stats_card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(150),
            padding=dp(20),
            spacing=dp(10),
            elevation=dp(2),
            radius=[dp(10)]
        )

        stats_card.add_widget(MDLabel(
            text="订单统计",
            theme_text_color="Primary",
            font_style="Headline6"
        ))

        stats_card.add_widget(MDLabel(
            text=f"总订单数：{total_orders}",
            theme_text_color="Secondary"
        ))

        stats_card.add_widget(MDLabel(
            text=f"总金额：¥{total_amount:.1f}",
            theme_text_color="Secondary"
        ))

        stats_card.add_widget(MDLabel(
            text=f"已完成订单：{completed_orders}",
            theme_text_color="Secondary"
        ))

        # 最近订单
        recent_label = MDLabel(
            text="最近订单",
            theme_text_color="Primary",
            font_style="Headline6",
            size_hint_y=None,
            height=30
        )

        scroll_view = MDScrollView()
        recent_list = MDList()

        # 按时间排序，取最近5个
        sorted_orders = sorted(all_orders, key=lambda x: x.created_at, reverse=True)[:5]

        for order in sorted_orders:
            time_str = datetime.fromisoformat(order.created_at).strftime("%m-%d %H:%M")
            item = ThreeLineListItem(
                text=f"订单号：{order.order_id[:20]}",
                secondary_text=f"收件人信息：{order.address}",  # | {self.get_status_text(order.status)}"
                tertiary_text=f"金额：¥{order.total:.1f} | 时间：{time_str}",
                font_style='Subtitle2',
                secondary_font_style='Overline',
                tertiary_font_style='Overline'
            )
            item.bind(on_release=lambda x, o=order: self.show_order_detail(o, has_delete=False))
            recent_list.add_widget(item)

        scroll_view.add_widget(recent_list)

        self.history_orders_dialog.content_cls.add_widget(stats_card)
        self.history_orders_dialog.content_cls.add_widget(recent_label)
        self.history_orders_dialog.content_cls.add_widget(scroll_view)
        self.history_orders_dialog.open()

    def show_all_orders_detail(self):
        """显示所有订单详情"""
        self.history_orders_dialog.dismiss()

        from kivy.app import App
        app = App.get_running_app()

        all_orders = app.order_manager.get_all_orders()

        scroll_view = MDScrollView()
        order_list = MDList()

        for order in all_orders[::-1]:
            time_str = datetime.fromisoformat(order.created_at).strftime("%Y-%m-%d %H:%M")
            item = ThreeLineListItem(
                text=f"订单号：{order.order_id[:20]}",
                secondary_text=f"收件人信息：{order.address}",  # | 状态：{self.get_status_text(order.status)}"
                tertiary_text=f"用户：{order.user_name} | 金额：¥{order.total:.1f} | 时间：{time_str}",
                font_style='Subtitle2',
                secondary_font_style='Overline',
                tertiary_font_style='Overline'
            )
            item.bind(on_release=lambda x, o=order: self.show_order_detail(o, prev_dialog='all'))
            order_list.add_widget(item)

        scroll_view.add_widget(order_list)

        self.all_orders_detail_dailog = MDDialog(
            title="所有订单详情",
            type="custom",
            size_hint_x=None,
            width=dp(360),
            content_cls=MDBoxLayout(
                orientation='vertical',
                spacing=dp(10),
                size_hint_y=None,
                height=dp(500)
            ),
            buttons=[
                MDFlatButton(
                    text="关闭",
                    on_release=lambda x: self.all_orders_detail_dailog.dismiss()
                ),
                MDRaisedButton(
                    text="导出数据",
                    on_release=lambda x, o=all_orders: self.export_orders_data(o)
                )
            ]
        )
        self.all_orders_detail_dailog.ids.title.font_name = CHINESE_FONT_NAME
        self.all_orders_detail_dailog.content_cls.add_widget(scroll_view)
        self.all_orders_detail_dailog.open()

    def show_order_detail(self, order, has_delete=True, prev_dialog="my"):
        """显示订单详情"""
        scroll_view = MDScrollView()
        recent_list = MDList()

        tmp = order.address.split('~')
        info_text = [
            f"收货人: {'~'.join(tmp[:-1])}",
            f"收货地址: {tmp[-1]}",  # 支付方式: {order.payment_method}
            f"下单账号: {order.user_name}",
            f"下单时间: {datetime.fromisoformat(order.created_at).strftime('%Y-%m-%d %H:%M:%S')}",
            f"订单号: {order.order_id[:20]}",
            f"订单状态: {self.get_status_text(order.status)}",
            ""
        ]
        for item in info_text:
            item_label = MDLabel(
                text=item,
                theme_text_color="Secondary",
                size_hint_y=None,
                font_style="Subtitle2",
                height=dp(20)
            )
            recent_list.add_widget(item_label)

        # 商品列表
        items_label = MDLabel(
            text="商品列表:",
            theme_text_color="Primary",
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(20)
        )
        recent_list.add_widget(items_label)

        # 添加商品项
        counts = 0
        for item in order.items:
            counts += item['quantity']
            item_text = f"• {item['product_name']} × {item['quantity']} = ¥{float(item['price']) * item['quantity']:.1f}"
            item_label = MDLabel(
                text=item_text,
                theme_text_color="Secondary",
                size_hint_y=None,
                font_style="Subtitle2",
                height=dp(20)
            )
            recent_list.add_widget(item_label)

        # 金额汇总
        summary_text = f"""\n\n\n
        商品总数: {int(counts)}
        商品小计: ¥{order.subtotal:.1f}
        优惠金额: ¥{order.discount:.1f}
        应付总额: ¥{order.total:.1f}
        """

        summary_label = MDLabel(
            text=summary_text,
            theme_text_color="Error",
            font_style="Headline5",
            size_hint_y=None,
            height=dp(60)
        )
        recent_list.add_widget(summary_label)
        # dialog.content_cls.add_widget(summary_label)
        scroll_view.add_widget(recent_list)

        # 调整内容高度
        # dialog.content_cls.height = dp(120 + len(order.items) * 20 + 60 + 10)

        if has_delete:
            self.order_detail_dialog = MDDialog(
                title=f"订单详情",
                type="custom",
                size_hint_x=None,
                width=dp(360),
                content_cls=MDBoxLayout(
                    orientation='vertical',
                    spacing=dp(10),
                    size_hint_y=None,
                    height=dp(500)
                ),
                buttons=[
                    MDRaisedButton(
                        text="删除订单",
                        on_release=lambda x, o=order: self.delete_my_order(o, prev=prev_dialog)
                    ),
                    MDFlatButton(
                        text="关闭",
                        on_release=lambda x: self.order_detail_dialog.dismiss()
                    )
                ]
            )
        else:
            self.order_detail_dialog = MDDialog(
                title=f"订单详情",
                type="custom",
                size_hint_x=None,
                width=dp(360),
                content_cls=MDBoxLayout(
                    orientation='vertical',
                    spacing=dp(10),
                    size_hint_y=None,
                    height=dp(500)
                ),
                buttons=[
                    MDFlatButton(
                        text="关闭",
                        on_release=lambda x: self.order_detail_dialog.dismiss()
                    )
                ]
            )
        self.order_detail_dialog.content_cls.add_widget(scroll_view)
        self.order_detail_dialog.open()

    def delete_my_order(self, order, prev="my"):

        # 确认删除 对话框
        self.confirm_delete_order_dialog = MDDialog(
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
                             on_release=lambda x: self.confirm_delete_order_dialog.dismiss()),
                MDRaisedButton(text="确认",
                               on_release=lambda x, o=order: self.comfirm_delete_my_order(o, flag=prev))
            ]
        )
        self.confirm_delete_order_dialog.ids.title.font_name = CHINESE_FONT_NAME

        time_str = datetime.fromisoformat(order.created_at).strftime("%Y-%m-%d %H:%M")
        self.confirm_delete_order_dialog.content_cls.add_widget(
            ThreeLineAvatarIconListItem(
                text=f"订单号：{order.order_id[:20]}",
                secondary_text=f"收件人信息：{order.address}",
                tertiary_text=f"金额：¥{order.total:.1f} | 时间：{time_str}",
                _txt_left_pad=dp(10)  # 删除icon空白
            ))

        self.confirm_delete_order_dialog.open()

    def comfirm_delete_my_order(self, order, flag="my"):

        from kivy.app import App
        app = App.get_running_app()

        app.order_manager.delete_order(order)

        self.confirm_delete_order_dialog.dismiss()

        if hasattr(self, 'all_orders_detail_dailog') and self.all_orders_detail_dailog:
            self.all_orders_detail_dailog.dismiss()
        if hasattr(self, 'order_detail_dialog') and self.order_detail_dialog:
            self.order_detail_dialog.dismiss()

        if hasattr(self, 'my_order_dialog') and self.my_order_dialog:
            self.my_order_dialog.dismiss()
            if flag == "my":
                self.show_my_orders()  # 重新载入
        if hasattr(self, 'history_orders_dialog') and self.history_orders_dialog:
            self.history_orders_dialog.dismiss()
            if flag == "all":
                self.show_history_orders()

    def get_status_text(self, status):
        """获取状态文本"""
        status_map = {
            "pending": "待付款",
            "paid": "待发货",
            "shipped": "待收货",
            "delivered": "已完成",
            "cancelled": "已取消"
        }
        # return status_map.get(status, status)
        return "已完成"

    def export_orders_data(self, orders):
        """导出订单数据"""
        # self.all_orders_detail_dailog.dismiss()

        JSONToCSVApp().export_json_to_csv(orders)

        MDSnackbar(MDLabel(text="订单数据导出功能开发中", text_color=(0.2, 0.6, 0.86, 1))).open()

    def refresh_orders(self):
        """刷新订单"""
        # self.load_orders()

        MDSnackbar(MDLabel(text="订单已刷新", text_color=(0.2, 0.8, 0.2, 1))).open()

    def show_my_inventory(self, *args):
        """显示我的订单"""
        from kivy.app import App
        app = App.get_running_app()
        app.show_inventory()

    def go_back(self):
        """返回主页"""
        from kivy.app import App
        app = App.get_running_app()
        app.show_home()


# Android平台特定导入
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path
    from android import mActivity


class JSONToCSVApp(MDApp):

    def export_json_to_csv(self, json_data):
        """导出JSON到CSV文件"""
        # 获取JSON数据
        # json_data = self.get_json_data()

        if not json_data:
            self.show_message("JSON数据为空！")
            return

        # 转换JSON到CSV
        csv_data = self.convert_json_to_csv(json_data)

        if csv_data:
            # 弹出保存对话框
            self.show_save_dialog(csv_data)

    def convert_json_to_csv(self, json_data):
        """将JSON转换为CSV格式"""
        try:
            if isinstance(json_data, list) and len(json_data) > 0:
                # 获取所有键作为CSV的标题
                dict_data = [order.to_dict() for order in json_data]
                fieldnames = list(dict_data[0].keys())

                # 创建CSV字符串
                output = StringIO()
                writer = csv.DictWriter(output, fieldnames=fieldnames)

                writer.writeheader()
                writer.writerows(dict_data)

                return output.getvalue()
            else:
                self.show_message("JSON数据格式不正确")
                return None
        except Exception as e:
            self.show_message(f"转换失败: {str(e)}")
            return None

    def show_save_dialog(self, csv_data):
        """显示保存对话框"""
        self.csv_data = csv_data

        self.dialog = MDDialog(
            title="保存CSV文件",
            text="请选择保存位置和文件名",
            buttons=[
                MDFlatButton(
                    text="取消",
                    font_name=CHINESE_FONT_NAME,
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDFlatButton(
                    text="保存",
                    font_name=CHINESE_FONT_NAME,
                    on_release=lambda x: self.save_file()
                ),
            ],
        )
        self.dialog.ids.title.font_name = CHINESE_FONT_NAME
        self.dialog.ids.text.font_name = CHINESE_FONT_NAME
        self.dialog.open()

    def save_file(self):
        """保存文件"""
        self.save_on_android()

        Clock.schedule_once(self.dismiss_dialog, 3)  # 延迟关闭

    def dismiss_dialog(self, dt):
        if hasattr(self, 'dialog') and self.dialog:
            self.dialog.dismiss()

    def save_on_android(self):
        """在Android上保存文件"""
        try:

            try:
                # 获取Download目录
                from android.storage import primary_external_storage_path
                storage = primary_external_storage_path()
                download_dir = os.path.join(storage, "Download")

                # 确保目录存在
                if not os.path.exists(download_dir):
                    os.makedirs(download_dir)

                # 保存文件
                filename = f"orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                filepath = os.path.join(download_dir, filename)

                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    f.write(self.csv_data)

            except Exception as e:
                from kivymd.toast import toast
                self.show_message(f"保存download目录失败: {str(e)}")

            # 使用plyer的文件选择器
            filechooser.save_file(
                title="保存CSV文件",
                filters=[("CSV files", "*.csv")],
                on_selection=self.handle_android_save
            )

        except Exception as e:
            self.show_message(f"保存失败: {str(e)}")

    def handle_android_save(self, selection):
        """处理Android保存选择"""
        if selection:
            file_path = selection[0]
            if not file_path.endswith('.csv'):
                file_path += '.csv'

            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    f.write(self.csv_data)
                self.show_message(message=f"文件已保存到: {file_path}")
            except Exception as e:
                self.show_message(message=f"保存失败: {str(e)}")
        else:
            self.show_message(message="保存已取消")

    def show_message(self, message, color=(0.2, 0.8, 0.2, 1)):
        """显示成功消息"""
        MDSnackbar(
            MDLabel(text=message, font_style="H6", theme_text_color="Custom", text_color=color),
            duration=3,
        ).open()
