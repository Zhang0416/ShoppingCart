from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import (MDList, OneLineListItem, OneLineIconListItem, ThreeLineListItem,
                             ThreeLineAvatarIconListItem, IconLeftWidget, IconRightWidget)
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.chip import MDChip
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.textfield import MDTextField
from kivy.metrics import dp, sp
from kivymd.app import MDApp
from kivy.logger import Logger
from kivy.utils import platform
from kivy.clock import Clock
from kivy.resources import resource_find
from kivy.app import App

from PIL import Image, ImageDraw, ImageFont

import json
import os
import csv
import traceback
from datetime import datetime
from io import StringIO

from .components.bluetooth_printer import get_printer_manager

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
            title="订单管理",
            md_bg_color=(0.2, 0.6, 0.86, 1),
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[["refresh", lambda x: self.refresh_orders()]]
        )

        # 功能列表
        scroll_view = MDScrollView()
        self.menu_list = MDList(size_hint_y=None)
        self.menu_list.bind(minimum_height=self.menu_list.setter('height'))

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
        my_orders_item.add_widget(
            IconLeftWidget(icon="cart", theme_text_color="Custom", text_color=(0.2, 0.2, 0.8, 1))
        )

        # 历史订单
        history_orders_item = OneLineIconListItem(
            text="历史订单",
            on_release=self.show_history_orders
        )
        history_orders_item.add_widget(
            IconLeftWidget(icon="history", theme_text_color="Custom", text_color=(1, 0.5, 0, 1))
        )

        # 利润统计，按照年份统计
        statis_orders_item = OneLineIconListItem(
            text="利润统计",
            on_release=self.show_statis_select_year
        )
        statis_orders_item.add_widget(
            IconLeftWidget(icon="camcorder", theme_text_color="Custom", text_color=(0.2, 0.8, 0.2, 1))
        )

        # # 库存管理区
        # inventory_section = OneLineListItem(
        #     text="库存管理",
        #     theme_text_color="Primary",
        #     font_style="Headline6"
        # )
        #
        # # 我的库存
        # my_inventory_item = OneLineIconListItem(
        #     text="我的库存",
        #     on_release=self.show_my_inventory
        # )
        # my_inventory_item.add_widget(IconLeftWidget(icon="storefront"))

        # self.menu_list.add_widget(order_section)
        self.menu_list.add_widget(my_orders_item)
        self.menu_list.add_widget(history_orders_item)
        self.menu_list.add_widget(statis_orders_item)
        # self.menu_list.add_widget(inventory_section)
        # self.menu_list.add_widget(my_inventory_item)

        scroll_view.add_widget(self.menu_list)

        main_layout.add_widget(toolbar)
        main_layout.add_widget(scroll_view)

        self.add_widget(main_layout)

    def on_enter(self):
        """进入页面时更新用户信息"""
        app = App.get_running_app()

    def show_my_orders(self, *args):
        """显示我的订单"""
        app = App.get_running_app()

        if not app.current_user:
            MDSnackbar(MDLabel(text="请先登录", theme_text_color="Custom", text_color=(0.9, 0.2, 0.2, 1))).open()
            return

        # 获取当前用户的订单
        orders = app.order_manager.get_orders_by_user(app.current_user['phone'])

        if not orders:
            dialog = MDDialog(
                title="我的订单",
                size_hint_x=0.9,
                background_color=(0, 0, 0, 0),
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

        # 最上方显示搜索订单框
        search_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(70),
            padding=dp(10),
            spacing=dp(10)
        )

        self.search_input = MDTextField(
            hint_text="搜索订单...",
            mode="rectangle",
            size_hint=(0.8, 1)
        )
        self.search_input.font_name_hint_text = CHINESE_FONT_NAME
        self.search_input.font_name = CHINESE_FONT_NAME

        search_btn = MDRaisedButton(
            text="搜索",
            size_hint=(0.2, 1),
            md_bg_color=(0.1, 0.5, 0.2, 0.8)
        )
        search_btn.bind(on_release=lambda x, o=orders: self.search_orders(o))

        search_layout.add_widget(self.search_input)
        search_layout.add_widget(search_btn)

        # 创建订单列表对话框
        scroll_view = MDScrollView()
        self.my_orders_list = MDList()

        for order in orders[::-1]:  # 最新的下单 显示在最前
            time_str = datetime.fromisoformat(order.created_at).strftime("%Y-%m-%d %H:%M")
            item = ThreeLineAvatarIconListItem(
                text=f"订单号：{order.order_id[:20]}",
                secondary_text=f"收货人：{order.address}",  # | 状态：{self.get_status_text(order.status)}",
                tertiary_text=f"金额：¥{order.total:.1f} | 时间：{time_str}",
                _txt_left_pad=dp(10),  # 删除icon空白
                font_style='Caption',
                secondary_font_style='Overline',
                tertiary_font_style='Overline'
            )
            item.bind(on_release=lambda x, o=order: self.show_order_detail(o))
            self.my_orders_list.add_widget(item)
        scroll_view.add_widget(self.my_orders_list)

        self.my_order_dialog = MDDialog(
            title="我的订单",
            type="custom",
            size_hint_x=0.9,
            background_color=(0, 0, 0, 0),
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

        # self.my_order_dialog.content_cls.add_widget(filter_layout)
        self.my_order_dialog.content_cls.add_widget(search_layout)
        self.my_order_dialog.content_cls.add_widget(scroll_view)
        self.my_order_dialog.open()

    def search_orders(self, orders):
        self.my_orders_list.clear_widgets()
        search_text = self.search_input.text.strip().lower()

        filtered_orders = [
            p for p in orders
            if search_text in str(p.address).lower() or search_text in str(p.order_id[:20]).lower()
        ]

        for order in filtered_orders[::-1]:  # 最新的下单 显示在最前
            time_str = datetime.fromisoformat(order.created_at).strftime("%Y-%m-%d %H:%M")
            item = ThreeLineAvatarIconListItem(
                text=f"订单号：{order.order_id[:20]}",
                secondary_text=f"收货人：{order.address}",  # | 状态：{self.get_status_text(order.status)}",
                tertiary_text=f"金额：¥{order.total:.1f} | 时间：{time_str}",
                _txt_left_pad=dp(10),  # 删除icon空白
                font_style='Caption',
                secondary_font_style='Overline',
                tertiary_font_style='Overline'
            )
            item.bind(on_release=lambda x, o=order: self.show_order_detail(o))
            self.my_orders_list.add_widget(item)  # 重新填充列表

    def show_history_orders(self, *args):
        """显示历史订单"""
        app = App.get_running_app()

        if not app.current_user:
            MDSnackbar(MDLabel(text="请先登录", theme_text_color="Custom", text_color=(0.9, 0.2, 0.2, 1))).open()
            return

        # 获取所有订单
        all_orders = app.order_manager.get_all_orders()

        if not all_orders:
            dialog = MDDialog(
                title="历史订单",
                size_hint_x=0.9,
                background_color=(0, 0, 0, 0),
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
            size_hint_x=0.9,
            background_color=(0, 0, 0, 0),
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
                    text="全部订单",
                    on_release=lambda x: self.show_all_orders()
                )
            ]
        )
        self.history_orders_dialog.ids.title.font_name = CHINESE_FONT_NAME

        # 统计信息
        stats_card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(120),
            padding=dp(20),
            spacing=dp(10),
            elevation=dp(2),
            radius=[dp(10)]
        )

        stats_card.add_widget(MDLabel(
            text="订单统计",
            theme_text_color="Primary",
            font_style="Subtitle2"
        ))

        stats_card.add_widget(MDLabel(
            text=f"总订单数：{total_orders}",
            theme_text_color="Secondary",
            font_style="Subtitle2"
        ))

        stats_card.add_widget(MDLabel(
            text=f"总金额：¥{total_amount:.1f}",
            theme_text_color="Secondary",
            font_style="Subtitle2"
        ))

        stats_card.add_widget(MDLabel(
            text=f"已完成订单：{completed_orders}",
            theme_text_color="Secondary",
            font_style="Subtitle2"
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
                secondary_text=f"收货人：{order.address}",  # | {self.get_status_text(order.status)}"
                tertiary_text=f"金额：¥{order.total:.1f} | 时间：{time_str}",
                font_style='Caption',
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

    def show_statis_select_year(self, *args):

        # 创建对话框
        self.statis_select_year_dialog = MDDialog(
            title="利润统计",
            type="custom",
            size_hint_x=0.9,
            background_color=(0, 0, 0, 0),
            content_cls=MDBoxLayout(
                orientation='vertical',
                spacing=dp(10),
                size_hint_y=None,
                height=dp(200)
            ),
            buttons=[
                MDFlatButton(
                    text="关闭",
                    on_release=lambda x: self.statis_select_year_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="查看详情",
                    on_release=lambda x: self.show_statis_orders()
                )
            ]
        )
        self.statis_select_year_dialog.ids.title.font_name = CHINESE_FONT_NAME

        # 选择年份
        select_year_layout = MDCard(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(60),
            padding=dp(10),
            spacing=dp(20),
            elevation=dp(2),
            radius=[dp(10)]
        )
        self.select_year_label = MDLabel(
            text="2026",
            theme_text_color="Hint",
            font_style="Subtitle2",
            height=dp(40),
        )
        self.select_year_btn = MDRaisedButton(
            text="选择年份",
            size_hint=(None, None),
            size=(sp(100), sp(10)),
            md_bg_color=(0.6, 0.4, 0.6, 1),
            on_release=self.open_year_menu
        )
        select_year_layout.add_widget(self.select_year_label)
        select_year_layout.add_widget(self.select_year_btn)

        self.statis_select_year_dialog.add_widget(select_year_layout)
        self.statis_select_year_dialog.open()

    def open_year_menu(self, *args):
        # 年份选择按钮
        self.year_menu_for_statis = MDDropdownMenu(
            caller=self.select_year_btn,
            items=[
                {
                    "text": str(cat),
                    "viewclass": "OneLineListItem",
                    "height": dp(50),
                    "on_release": lambda x=cat: self.select_year_for_statis(x),
                } for cat in range(2026, 2050)
            ],
            width_mult=1,
            # max_height=300,
            # position="center",
            hor_growth="left",  # 水平向右扩展（避免左侧裁剪）
            md_bg_color=(0.2, 0.8, 0.2, 1)
        )
        self.year_menu_for_statis.width = dp(100)
        self.year_menu_for_statis.open()

    def select_year_for_statis(self, year):
        """为商品选择分类"""
        self.select_year_label.text = str(year)
        if self.year_menu_for_statis:
            self.year_menu_for_statis.dismiss()

    def _calc_order_profit(self, order):
        """计算订单利润：订单金额 - 成本金额"""
        app = App.get_running_app()
        cost = 0.0
        for item in order.items:
            qty = int(item.get('quantity', 0))
            if 'suggest' in item:
                # 有 suggest 的订单：price 是成本价，suggest 是零售价
                unit_cost = float(item.get('price', 0))
            else:
                # 未转换的旧订单：尝试从产品库查找当前成本价
                product = app.db.get_product(item.get('product_id', ''))
                if product:
                    unit_cost = product.price
                else:
                    unit_cost = float(item.get('price', 0))
            cost += unit_cost * qty
        return order.total - cost

    def show_statis_orders(self, *args):

        """获取所有订单"""
        app = App.get_running_app()

        if not app.current_user:
            MDSnackbar(MDLabel(text="请先登录", theme_text_color="Custom", text_color=(0.9, 0.2, 0.2, 1))).open()
            return

        all_orders = app.order_manager.get_all_orders()
        sorted_orders = sorted(all_orders, key=lambda x: x.created_at, reverse=True)
        monthly_stats = {month: {"count": 0, "amount": 0.0, "profit": 0.0, "id_list": []} for month in range(1, 13)}
        for order in sorted_orders:
            time_format = datetime.fromisoformat(order.created_at)

            # 检查年份
            if str(time_format.year) == self.select_year_label.text:
                # 更新统计
                monthly_stats[time_format.month]["count"] += 1
                monthly_stats[time_format.month]["amount"] += order.total
                monthly_stats[time_format.month]["profit"] += self._calc_order_profit(order)
                monthly_stats[time_format.month]["id_list"].append(order.order_id)

        year_profit = sum(m["profit"] for m in monthly_stats.values())
        year_amount = sum(m["amount"] for m in monthly_stats.values())
        year_count = sum(m["count"] for m in monthly_stats.values())

        # 创建对话框
        self.statis_orders_dialog = MDDialog(
            title=f"{self.select_year_label.text}年利润统计",
            type="custom",
            size_hint_x=0.9,
            background_color=(0, 0, 0, 0),
            content_cls=MDBoxLayout(
                orientation='vertical',
                spacing=dp(10),
                size_hint_y=None,
                height=dp(500)
            ),
            buttons=[
                MDFlatButton(
                    text="关闭",
                    on_release=lambda x: self.statis_orders_dialog.dismiss()
                ),
            ]
        )
        self.statis_orders_dialog.ids.title.font_name = CHINESE_FONT_NAME

        # 年度汇总信息（三行居中：订单数、销售额、利润）
        summary_card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(95),
            padding=dp(8),
            spacing=dp(2),
            elevation=dp(2),
            radius=[dp(10)]
        )
        summary_card.add_widget(MDLabel(
            text=f"年度订单数: {year_count}",
            theme_text_color="Primary",
            font_style="Subtitle2",
            halign="center"
        ))
        summary_card.add_widget(MDLabel(
            text=f"年度销售额: ¥{year_amount:.1f}",
            theme_text_color="Primary",
            font_style="Subtitle2",
            halign="center"
        ))
        summary_card.add_widget(MDLabel(
            text=f"年度总利润: ¥{year_profit:.1f}",
            theme_text_color="Error",
            font_style="Subtitle2",
            halign="center"
        ))
        self.statis_orders_dialog.content_cls.add_widget(summary_card)

        scroll_view = MDScrollView()
        month_list = MDList()
        for month in range(1, 13):
            if monthly_stats[month]['count'] <= 0:
                continue
            item = ThreeLineListItem(
                text=f"{month}月",
                secondary_text=f"订单数：{monthly_stats[month]['count']:>4}   销售额：¥{monthly_stats[month]['amount']:.1f}",
                tertiary_text=f"利润：¥{monthly_stats[month]['profit']:.1f}",
                font_style='Subtitle2',
                secondary_font_style='Subtitle2',
                tertiary_font_style='Subtitle2'
            )
            item.bind(
                on_release=lambda x, m=month, id=monthly_stats[month]['id_list']: self.show_month_order_detail(m, id))
            month_list.add_widget(item)
        scroll_view.add_widget(month_list)

        self.statis_orders_dialog.content_cls.add_widget(scroll_view)
        self.statis_orders_dialog.open()

    def show_month_order_detail(self, month, id_list):
        app = App.get_running_app()

        all_orders = app.order_manager.get_all_orders()
        month_orders = [o for o in all_orders if o.order_id in id_list]

        month_profit = sum(self._calc_order_profit(o) for o in month_orders)
        month_amount = sum(o.total for o in month_orders)

        # 创建对话框
        month_orders_dialog = MDDialog(
            title=f"{month}月订单明细(利润¥{month_profit:.1f})",
            type="custom",
            size_hint_x=0.9,
            background_color=(0, 0, 0, 0),
            content_cls=MDBoxLayout(
                orientation='vertical',
                spacing=dp(10),
                size_hint_y=None,
                height=dp(500)
            ),
            buttons=[
                MDFlatButton(
                    text="关闭",
                    on_release=lambda x: month_orders_dialog.dismiss()
                ),
            ]
        )
        month_orders_dialog.ids.title.font_name = CHINESE_FONT_NAME

        scroll_view = MDScrollView()
        recent_list = MDList()
        for order in month_orders[::-1]:  # 倒序，日期较大的排在前面
            time_str = datetime.fromisoformat(order.created_at).strftime("%m-%d %H:%M")
            profit = self._calc_order_profit(order)
            item = ThreeLineListItem(
                text=f"订单号：{order.order_id[:20]}",
                secondary_text=f"收货人：{order.address}",
                tertiary_text=f"金额：¥{order.total:.1f} | 利润：¥{profit:.1f} | 时间：{time_str}",
                font_style='Caption',
                secondary_font_style='Overline',
                tertiary_font_style='Overline'
            )
            item.bind(on_release=lambda x, o=order: self.show_order_detail(o, has_delete=False, show_cost=True))
            recent_list.add_widget(item)

        scroll_view.add_widget(recent_list)
        month_orders_dialog.content_cls.add_widget(scroll_view)
        month_orders_dialog.open()

    def show_all_orders(self):
        """显示所有订单详情"""
        self.history_orders_dialog.dismiss()

        app = App.get_running_app()

        all_orders = app.order_manager.get_all_orders()

        scroll_view = MDScrollView()
        order_list = MDList()

        for order in all_orders[::-1]:
            time_str = datetime.fromisoformat(order.created_at).strftime("%Y-%m-%d %H:%M")
            item = ThreeLineListItem(
                text=f"订单号：{order.order_id[:20]}",
                secondary_text=f"收货人：{order.address}",  # | 状态：{self.get_status_text(order.status)}"
                tertiary_text=f"用户：{order.user_name} | 金额：¥{order.total:.1f} | 时间：{time_str}",
                font_style='Caption',
                secondary_font_style='Overline',
                tertiary_font_style='Overline'
            )
            item.bind(on_release=lambda x, o=order: self.show_order_detail(o, prev_dialog='all'))
            order_list.add_widget(item)

        scroll_view.add_widget(order_list)

        self.all_orders_detail_dailog = MDDialog(
            title="所有订单详情",
            type="custom",
            size_hint_x=0.9,
            background_color=(0, 0, 0, 0),
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

    def show_order_detail(self, order, has_delete=True, prev_dialog="my", show_cost=False):
        """显示订单详情（自适应宽度 Dialog）
        
        Args:
            show_cost: 为 True 时显示成本价列，且只保留打印/关闭按钮（用于利润统计入口）
        """

        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None,
            height=dp(520)
        )

        scroll_view = MDScrollView(size_hint=(1, None), height=dp(465))
        recent_list = MDList(size_hint_y=None)
        recent_list.bind(minimum_height=recent_list.setter('height'))

        # 顶部留白
        recent_list.add_widget(MDLabel(size_hint_y=None, height=dp(10)))

        # 订单信息
        infor_label = MDLabel(
            text="----------- 订单信息 -----------",
            theme_text_color="Primary",
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(24),
            halign='center'
        )
        infor_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        recent_list.add_widget(infor_label)

        tmp = order.address.split('~')
        info_text = [
            f"收货人: {'~'.join(tmp[:-1])}",
            f"收货地址: {tmp[-1]}",
            f"下单时间: {order.user_name}~{datetime.fromisoformat(order.created_at).strftime('%Y-%m-%d %H:%M:%S')}",
            f"订单号: {order.order_id[:20]}~{self.get_status_text(order.status)}",
        ]
        for item in info_text:
            item_label = MDLabel(
                text=item,
                theme_text_color="Secondary",
                size_hint_y=None,
                font_style="Caption",
                height=dp(20),
            )
            item_label.bind(
                width=lambda instance, value: setattr(instance, 'text_size', (value, None)),
                texture_size=lambda instance, value: setattr(instance, 'height', value[1])
            )
            recent_list.add_widget(item_label)

        # 商品列表
        recent_list.add_widget(MDLabel(size_hint_y=None, height=dp(15)))
        items_label = MDLabel(
            text="----------- 商品列表 -----------",
            theme_text_color="Primary",
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(24),
            halign='center'
        )
        items_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        recent_list.add_widget(items_label)

        counts = 0
        if show_cost:
            # 利润统计入口：4列，成本/零售列尽可能宽，折扣价一组数值0.25够用
            size_x_arr = [0.30, 0.15, 0.4, 0.25]
            col_headers = ["名称", "数量", "成本/零售", "折扣价"]
            col_haligns = ["left", "center", "right", "right"]
            name_col_w = 0.30
            qty_col_w = 0.12
            price_col_w = 0.4
            disc_col_w = 0.18
            row_min_h = dp(20)
        else:
            size_x_arr = [0.35, 0.15, 0.25, 0.25]
            col_headers = ["名称", "数量", "零售价", "折扣价"]
            col_haligns = ["left", "center", "right", "right"]
            name_col_w = 0.35
            qty_col_w = 0.15
            price_col_w = 0.25
            disc_col_w = 0.25
            row_min_h = dp(20)

        # 表头
        header_row = MDBoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(22),
            padding=(dp(5), 0)
        )
        for i, h in enumerate(col_headers):
            if show_cost and i == 2:
                # "成本/零售" 列拆分为三部分，让 "/" 与数据行对齐
                price_header_box = MDBoxLayout(
                    orientation='horizontal',
                    size_hint=(size_x_arr[i], 1),
                )
                price_header_box.add_widget(MDLabel(
                    text="成本", theme_text_color="Secondary",
                    size_hint=(0.46, 1), font_style="Caption",
                    halign="right", bold=True,
                ))
                price_header_box.add_widget(MDLabel(
                    text="/", theme_text_color="Secondary",
                    size_hint=(0.08, 1), font_style="Caption",
                    halign="center", bold=True,
                ))
                price_header_box.add_widget(MDLabel(
                    text="零售", theme_text_color="Secondary",
                    size_hint=(0.46, 1), font_style="Caption",
                    halign="left", bold=True,
                ))
                header_row.add_widget(price_header_box)
            else:
                header_row.add_widget(MDLabel(
                    text=h,
                    theme_text_color="Secondary",
                    size_hint=(size_x_arr[i], 1),
                    font_style="Caption",
                    halign=col_haligns[i],
                    bold=True,
                ))
        recent_list.add_widget(header_row)

        # 商品行
        for item in order.items:
            counts += item['quantity']
            retail_price = float(item.get('suggest', item['price']))
            cost_price = float(item.get('price', 0)) if 'suggest' in item else retail_price
            original_ss = retail_price * item['quantity']
            cost_ss = cost_price * item['quantity']
            discount_price = item.get('discount_price', retail_price)
            discount_ss = float(discount_price) * item['quantity']

            row = MDBoxLayout(
                orientation='horizontal',
                size_hint=(1, None),
                height=row_min_h,
                padding=(dp(5), 0)
            )

            name_lbl = MDLabel(
                text=f"• {item['product_name']}",
                theme_text_color="Secondary",
                size_hint=(name_col_w, None),
                font_style="Overline",
                valign="center",
            )
            name_lbl.bind(
                width=lambda inst, w: setattr(inst, 'text_size', (w, None)),
                texture_size=lambda inst, ts: setattr(inst, 'height', ts[1])
            )

            qty_lbl = MDLabel(
                text=f"× {item['quantity']}",
                theme_text_color="Secondary",
                size_hint=(qty_col_w, 1),
                font_style="Overline",
                halign="center",
                valign="center",
            )

            if show_cost:
                # 成本/零售拆分为三部分，让 "/" 上下对齐，内部比例紧凑
                price_box = MDBoxLayout(
                    orientation='horizontal',
                    size_hint=(price_col_w, 1),
                )
                price_box.add_widget(MDLabel(
                    text=f"¥{cost_ss:.1f}",
                    theme_text_color="Secondary",
                    size_hint=(0.46, 1), font_style="Overline",
                    halign="right", valign="center",
                ))
                price_box.add_widget(MDLabel(
                    text="/",
                    theme_text_color="Secondary",
                    size_hint=(0.08, 1), font_style="Overline",
                    halign="center", valign="center",
                ))
                price_box.add_widget(MDLabel(
                    text=f"¥{original_ss:.1f}",
                    theme_text_color="Secondary",
                    size_hint=(0.46, 1), font_style="Overline",
                    halign="left", valign="center",
                ))
                price_lbl = price_box
            else:
                price_lbl = MDLabel(
                    text=f"¥{original_ss:.1f}",
                    theme_text_color="Secondary",
                    size_hint=(price_col_w, 1),
                    font_style="Overline",
                    halign="right",
                    valign="center",
                )

            disc_lbl = MDLabel(
                text=f"¥{discount_ss:.1f}",
                theme_text_color="Secondary",
                size_hint=(disc_col_w, 1),
                font_style="Overline",
                halign="right",
                valign="center",
            )

            def on_name_height(inst, ts, row=row):
                row.height = max(ts[1], row_min_h)

            name_lbl.bind(texture_size=on_name_height)

            row.add_widget(name_lbl)
            row.add_widget(qty_lbl)
            row.add_widget(price_lbl)
            row.add_widget(disc_lbl)
            recent_list.add_widget(row)

        # 金额汇总
        recent_list.add_widget(MDLabel(size_hint_y=None, height=dp(15)))
        summary_label = MDLabel(
            text="----------- 金额汇总 -----------",
            theme_text_color="Primary",
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(24),
            halign='center'
        )
        summary_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        recent_list.add_widget(summary_label)

        summary_text = (
            f"商品总数: {int(counts)}\n"
            f"商品小计: ¥{order.subtotal:.1f}\n"
            f"优惠金额: ¥{order.discount:.1f}\n"
            f"应付总额: ¥{order.total:.1f}"
        )

        summary_value = MDLabel(
            text=summary_text,
            theme_text_color="Error",
            font_style="Subtitle2",
            size_hint_y=None,
            text_size=(None, None),
            padding=(dp(20), 0)
        )
        summary_value.bind(
            width=lambda instance, value: setattr(instance, 'text_size', (value, None)),
            texture_size=lambda instance, value: setattr(instance, 'height', value[1])
        )
        recent_list.add_widget(summary_value)
        scroll_view.add_widget(recent_list)
        content.add_widget(scroll_view)

        # 按钮容器：平均分布（减小字号和高度以适配窄屏）
        button_box = MDBoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(36),
            spacing=dp(2)
        )

        if show_cost:
            # 利润统计入口：只显示打印和关闭
            btn_ratio = 0.5
            print_btn = MDRaisedButton(
                text="打印",
                size_hint=(btn_ratio, 1),
                md_bg_color=(0.2, 0.6, 0.86, 1),
                on_release=lambda x, o=order: self._print_order(o)
            )
            close_btn = MDRaisedButton(
                text="关闭",
                size_hint=(btn_ratio, 1),
                md_bg_color=(0.5, 0.5, 0.5, 1),
                on_release=lambda x: self.order_detail_dialog.dismiss()
            )
            button_box.add_widget(print_btn)
            button_box.add_widget(close_btn)
        else:
            btn_ratio = 0.25 if has_delete else 0.333

            if has_delete:
                delete_btn = MDRaisedButton(
                    text="删除",
                    size_hint=(btn_ratio, 1),
                    md_bg_color=(0.9, 0.3, 0.3, 1),
                    on_release=lambda x, o=order: self.delete_my_order(o, prev=prev_dialog)
                )
                button_box.add_widget(delete_btn)

            print_btn = MDRaisedButton(
                text="打印",
                size_hint=(btn_ratio, 1),
                md_bg_color=(0.2, 0.6, 0.86, 1),
                on_release=lambda x, o=order: self._print_order(o)
            )
            save_img_btn = MDRaisedButton(
                text="保存",
                size_hint=(btn_ratio, 1),
                md_bg_color=(0.2, 0.7, 0.5, 1),
                on_release=lambda x, o=order: self.save_order_image(o)
            )
            close_btn = MDRaisedButton(
                text="关闭",
                size_hint=(btn_ratio, 1),
                md_bg_color=(0.5, 0.5, 0.5, 1),
                on_release=lambda x: self.order_detail_dialog.dismiss()
            )

            button_box.add_widget(print_btn)
            button_box.add_widget(save_img_btn)
            button_box.add_widget(close_btn)

        content.add_widget(button_box)

        self.order_detail_dialog = MDDialog(
            title=f"订单详情",
            type="custom",
            size_hint_x=0.9,
            background_color=(0, 0, 0, 0),
            content_cls=content,
            buttons=[]
        )
        self.order_detail_dialog.ids.title.font_name = CHINESE_FONT_NAME
        self.order_detail_dialog.open()

    def delete_my_order(self, order, prev="my"):

        # 确认删除 对话框
        self.confirm_delete_order_dialog = MDDialog(
            title="确认删除",
            type="custom",
            size_hint_x=0.9,
            background_color=(0, 0, 0, 0),
            content_cls=MDBoxLayout(
                orientation='vertical',
                spacing=dp(10),
                size_hint_y=None,
                height=dp(60)
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
                secondary_text=f"收货人信息：{order.address}",
                tertiary_text=f"金额：¥{order.total:.1f} | 时间：{time_str}",
                _txt_left_pad=dp(10),  # 删除icon空白
                font_style='Caption',
                secondary_font_style='Overline',
                tertiary_font_style='Overline'
            ))

        self.confirm_delete_order_dialog.open()

    def comfirm_delete_my_order(self, order, flag="my"):

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

        # JSONToCSVApp().export_json_to_csv(orders)

        MDSnackbar(
            MDLabel(text="订单数据导出功能开发中", theme_text_color="Custom", text_color=(0.2, 0.6, 0.86, 1))).open()

    def refresh_orders(self):
        """刷新订单"""
        # self.load_orders()

        MDSnackbar(MDLabel(text="订单已刷新", theme_text_color="Custom", text_color=(0.2, 0.8, 0.2, 1))).open()

    def _print_order(self, order):
        """打印订单到蓝牙打印机"""
        Logger.info("OrdersScreen: _print_order 开始")
        mgr = get_printer_manager()
        Logger.info(f"OrdersScreen: mgr={mgr}")
        if not mgr:
            MDSnackbar(
                MDLabel(text="蓝牙打印机模块未初始化", theme_text_color="Custom", text_color=(0.9, 0.2, 0.2, 1))
            ).open()
            return

        connected = mgr.is_connected()
        Logger.info(f"OrdersScreen: is_connected={connected}")
        if not connected:
            MDSnackbar(
                MDLabel(text="没有可用的蓝牙打印机，请先在个人中心连接打印机", theme_text_color="Custom",
                        text_color=(0.9, 0.2, 0.2, 1))
            ).open()
            return

        try:
            Logger.info("OrdersScreen: 调用 mgr.print_order")
            success, error = mgr.print_order(order)
            Logger.info(f"OrdersScreen: print_order 返回 success={success}, error={error}")
        except Exception as e:
            Logger.error(f"OrdersScreen: print_order 调用异常: {e}")
            Logger.error(traceback.format_exc())
            success = False
            error = str(e)

        if success:
            MDSnackbar(
                MDLabel(text="订单已发送到打印机", theme_text_color="Custom", text_color=(0.2, 0.8, 0.2, 1)),
                duration=2,
            ).open()
        else:
            MDSnackbar(
                MDLabel(text=f"打印失败: {error}", theme_text_color="Custom", text_color=(0.9, 0.2, 0.2, 1))
            ).open()

    def go_back(self):
        """返回主页"""
        app = App.get_running_app()
        app.show_home()

    def _generate_order_image(self, order, output_path):
        """使用 Pillow 生成订单长图，格式与订单详情页面一致"""
        WIDTH = 384
        MARGIN = 16
        INNER_WIDTH = WIDTH - 2 * MARGIN
        BG_COLOR = (255, 255, 255)
        TEXT_COLOR = (0, 0, 0)
        HEADER_COLOR = (80, 80, 80)
        SEP_COLOR = (200, 200, 200)
        RED_COLOR = (220, 50, 50)

        # 加载中文字体
        font_path = None
        try:
            font_path = resource_find('screens/assets/fonts/msyhbd.ttc')
        except Exception:
            pass

        if not font_path or not os.path.exists(font_path):
            for fp in ['/system/fonts/DroidSansFallback.ttf',
                       '/system/fonts/NotoSansCJK-Regular.ttc',
                       '/system/fonts/NotoSansSC-Regular.otf']:
                if os.path.exists(fp):
                    font_path = fp
                    break

        try:
            font_title = ImageFont.truetype(font_path, 28)
            font_section = ImageFont.truetype(font_path, 20)
            font_body = ImageFont.truetype(font_path, 18)
            font_bold = ImageFont.truetype(font_path, 20)
        except Exception:
            font_title = font_section = font_body = font_bold = ImageFont.load_default()

        def get_text_size(draw, text, font):
            try:
                bbox = draw.textbbox((0, 0), text, font=font)
                return bbox[2] - bbox[0], bbox[3] - bbox[1]
            except Exception:
                try:
                    return draw.textsize(text, font=font)
                except Exception:
                    return font.getsize(text)

        def wrap_text(draw, text, font, max_width):
            """按最大宽度对文本进行换行（逐字符）"""
            if not text:
                return [""]
            lines = []
            current = ""
            for ch in text:
                test = current + ch
                w, _ = get_text_size(draw, test, font)
                if w <= max_width:
                    current = test
                else:
                    lines.append(current)
                    current = ch
            if current:
                lines.append(current)
            return lines if lines else [text]

        # 列宽定义（四列：名称 0.35, 数量 0.15, 零售价 0.25, 折扣价 0.25）
        name_col_w = int(INNER_WIDTH * 0.35)
        qty_col_w = int(INNER_WIDTH * 0.15)
        orig_col_w = int(INNER_WIDTH * 0.25)
        disc_col_w = INNER_WIDTH - name_col_w - qty_col_w - orig_col_w

        col_x = [
            MARGIN,
            MARGIN + name_col_w,
            MARGIN + name_col_w + qty_col_w,
            MARGIN + name_col_w + qty_col_w + orig_col_w,
        ]
        col_w = [name_col_w, qty_col_w, orig_col_w, disc_col_w]

        # 先创建临时 draw 用于测量
        tmp_img = Image.new('RGB', (1, 1))
        tmp_draw = ImageDraw.Draw(tmp_img)

        # 构建绘制项并计算高度
        draw_items = []
        y = MARGIN

        # 大标题
        draw_items.append(("title", "订单详情", y))
        y += 45

        # 分隔线
        draw_items.append(("sep", None, y))
        y += 18

        # 订单信息
        section_text = "-------------- 订单信息 --------------"
        draw_items.append(("section_title", section_text, y))
        y += 32

        tmp = order.address.split('~')
        info_lines = [
            f"收货人: {'~'.join(tmp[:-1])}",
            f"收货地址: {tmp[-1]}",
            f"下单时间: {order.user_name}~{datetime.fromisoformat(order.created_at).strftime('%Y-%m-%d %H:%M:%S')}",
            f"订单号: {order.order_id[:20]}~{self.get_status_text(order.status)}",
        ]
        for line in info_lines:
            draw_items.append(("body", line, y))
            y += 28

        # 商品列表
        y += 8
        section_text = "-------------- 商品列表 --------------"
        draw_items.append(("section_title", section_text, y))
        y += 32

        # 表头（四列：名称、数量、零售价、折扣价）
        draw_items.append(("table_header", ["名称", "数量", "零售价", "折扣价"], y))
        y += 28

        counts = 0
        for item in order.items:
            counts += item['quantity']
            retail_price = float(item.get('suggest', item['price']))
            original_ss = retail_price * item['quantity']
            discount_price = item.get('discount_price', retail_price)
            discount_ss = float(discount_price) * item['quantity']

            name_text = f"• {item['product_name']}"
            name_lines = wrap_text(tmp_draw, name_text, font_body, name_col_w - 6)
            row_h = max(len(name_lines) * 24, 28)

            draw_items.append(("table_row", {
                "name_lines": name_lines,
                "qty": f"× {item['quantity']}",
                "orig": f"¥{original_ss:.1f}",
                "disc": f"¥{discount_ss:.1f}",
                "row_h": row_h,
            }, y))
            y += row_h

        # 金额汇总
        y += 8
        section_text = "-------------- 金额汇总 --------------"
        draw_items.append(("section_title", section_text, y))
        y += 32

        summary_lines = [
            f"商品总数: {int(counts)}",
            f"商品小计: ¥{order.subtotal:.1f}",
            f"优惠金额: ¥{order.discount:.1f}",
            f"应付总额: ¥{order.total:.1f}",
        ]
        for line in summary_lines:
            draw_items.append(("body_bold", line, y))
            y += 28

        y += MARGIN  # 底部边距
        total_height = y

        # 创建最终图片
        img = Image.new('RGB', (WIDTH, total_height), BG_COLOR)
        draw = ImageDraw.Draw(img)

        # 绘制
        for typ, data, y in draw_items:
            if typ == "title":
                tw, th = get_text_size(draw, data, font_title)
                x = (WIDTH - tw) // 2
                draw.text((x, y), data, font=font_title, fill=TEXT_COLOR)
            elif typ == "section_title":
                tw, th = get_text_size(draw, data, font_section)
                x = (WIDTH - tw) // 2
                draw.text((x, y), data, font=font_section, fill=HEADER_COLOR)
            elif typ == "sep":
                draw.line([(MARGIN, y + 9), (WIDTH - MARGIN, y + 9)], fill=SEP_COLOR, width=2)
            elif typ == "body":
                draw.text((MARGIN, y), data, font=font_body, fill=TEXT_COLOR)
            elif typ == "body_bold":
                draw.text((MARGIN, y), data, font=font_bold, fill=RED_COLOR)
            elif typ == "table_header":
                headers = data
                haligns = ["left", "center", "right", "right"]
                for i, h in enumerate(headers):
                    if haligns[i] == "center":
                        tw, _ = get_text_size(draw, h, font_body)
                        tx = col_x[i] + (col_w[i] - tw) // 2
                    elif haligns[i] == "right":
                        tw, _ = get_text_size(draw, h, font_body)
                        tx = col_x[i] + col_w[i] - tw
                    else:
                        tx = col_x[i]
                    draw.text((tx, y), h, font=font_body, fill=HEADER_COLOR)
            elif typ == "table_row":
                row_data = data
                row_h = row_data["row_h"]
                # 名称（可能多行）
                for j, nl in enumerate(row_data["name_lines"]):
                    draw.text((col_x[0], y + j * 24), nl, font=font_body, fill=TEXT_COLOR)
                # 数量（垂直居中）
                tw, _ = get_text_size(draw, row_data["qty"], font_body)
                tx = col_x[1] + (col_w[1] - tw) // 2
                draw.text((tx, y + (row_h - 24) // 2), row_data["qty"], font=font_body, fill=TEXT_COLOR)
                # 原价（垂直居中+右对齐）
                tw, _ = get_text_size(draw, row_data["orig"], font_body)
                tx = col_x[2] + col_w[2] - tw
                draw.text((tx, y + (row_h - 24) // 2), row_data["orig"], font=font_body, fill=TEXT_COLOR)
                # 折扣价（垂直居中+右对齐）
                tw, _ = get_text_size(draw, row_data["disc"], font_body)
                tx = col_x[3] + col_w[3] - tw
                draw.text((tx, y + (row_h - 24) // 2), row_data["disc"], font=font_body, fill=TEXT_COLOR)

        img.save(output_path, 'PNG')
        return output_path

    def save_order_image(self, order):
        """保存订单长图：PC端弹出目录选择，Android端保存到相册并触发扫描"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"order_{order.order_id[:8]}_{timestamp}.png"

            if platform == 'android':
                # Android: 保存到外部存储 Pictures/ShopCart/
                try:
                    from android.storage import primary_external_storage_path
                    storage = primary_external_storage_path()
                except Exception:
                    storage = os.environ.get('EXTERNAL_STORAGE', '/sdcard')

                save_dir = os.path.join(storage, "Pictures", "ShopCart")
                os.makedirs(save_dir, exist_ok=True)
                filepath = os.path.join(save_dir, filename)

                self._generate_order_image(order, filepath)
                Logger.info(f"OrdersScreen: 订单长图已保存: {filepath}")

                # 通知媒体扫描，让相册可见
                try:
                    from jnius import autoclass
                    from android import mActivity
                    MediaScannerConnection = autoclass('android.media.MediaScannerConnection')
                    MediaScannerConnection.scanFile(mActivity, [filepath], ['image/png'], None)
                except Exception as scan_err:
                    Logger.warning(f"OrdersScreen: 媒体扫描通知失败: {scan_err}")

                MDSnackbar(
                    MDLabel(text=f"已保存到相册/ShopCart/{filename}"),
                    duration=3,
                ).open()
            else:
                # PC端：弹出保存文件对话框
                default_path = os.path.join(os.path.expanduser('~'), 'Pictures', filename)

                def on_selection(selection):
                    if selection:
                        path = selection[0]
                        if not path.lower().endswith('.png'):
                            path += '.png'
                        try:
                            self._generate_order_image(order, path)
                            Logger.info(f"OrdersScreen: 订单长图已保存: {path}")
                            MDSnackbar(
                                MDLabel(text=f"已保存: {path}"),
                                duration=3,
                            ).open()
                        except Exception as save_err:
                            Logger.error(f"OrdersScreen: 保存长图失败: {save_err}")
                            MDSnackbar(
                                MDLabel(text=f"保存失败: {save_err}"),
                                duration=3,
                            ).open()

                try:
                    from plyer import filechooser
                    filechooser.save_file(
                        title="保存订单长图",
                        filters=[["PNG图片", "*.png"]],
                        path=default_path,
                        on_selection=on_selection
                    )
                except Exception as chooser_err:
                    Logger.warning(f"OrdersScreen: 文件选择器失败，使用默认路径: {chooser_err}")
                    # 备选：直接保存到默认路径
                    self._generate_order_image(order, default_path)
                    MDSnackbar(
                        MDLabel(text=f"已保存到: {default_path}"),
                        duration=3,
                    ).open()
        except Exception as e:
            Logger.error(f"OrdersScreen: 保存订单长图失败: {e}")
            Logger.error(traceback.format_exc())
            MDSnackbar(
                MDLabel(text=f"保存失败: {e}"),
                duration=3,
            ).open()


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
            size_hint_x=0.9,
            background_color=(0, 0, 0, 0),
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
                self.show_message(f"保存download目录失败: {str(e)}")

            # 使用plyer的文件选择器
            from plyer import filechooser
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
