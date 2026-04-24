from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import MDList, ThreeLineListItem
from kivymd.uix.scrollview import MDScrollView
from kivy.metrics import dp

from .assets.config_chinese import CHINESE_FONT_NAME
from .orders_screen import OrdersScreen


class CheckoutScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "checkout"
        self._build_ui()

    def _build_ui(self):
        # 主布局
        main_layout = MDBoxLayout(orientation='vertical')

        # 顶部栏
        toolbar = MDBoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(60),
            padding=dp(10),
            spacing=dp(10),
            md_bg_color=(0.2, 0.6, 0.86, 1)
        )

        # 返回按钮
        back_btn = MDIconButton(
            icon="arrow-left",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)
        )
        back_btn.bind(on_release=self.go_back)

        # 标题
        title = MDLabel(
            text="结算",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_style="Subtitle1",
            halign="center",
            size_hint=(0.6, 1)
        )

        toolbar.add_widget(back_btn)
        toolbar.add_widget(title)

        # 订单信息卡片
        order_card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(120),
            padding=dp(10),
            spacing=dp(10),
            elevation=dp(4),
            radius=[dp(10)]
        )

        # 商品详情卡片
        self.items_card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(80),
            padding=dp(20),
            spacing=dp(10),
            elevation=dp(4),
            radius=[dp(10)]
        )

        items_title = MDLabel(
            text="商品详情",
            theme_text_color="Primary",
            font_style="Subtitle1",
            size_hint=(1, None),
            height=dp(30)
        )
        self.items_card.add_widget(items_title)

        self.items_table_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(0),
            padding=dp(10),
            spacing=dp(0)
        )
        self.items_card.add_widget(self.items_table_layout)

        # 商品总价
        self.subtotal_label = MDLabel(
            text="商品总价: ¥0.00",
            theme_text_color="Primary",
            font_style="Subtitle1"
        )

        # 运费
        shipping_label = MDLabel(
            text="运费: ¥0.00",
            theme_text_color="Primary",
            font_style="Subtitle1"
        )

        # 优惠
        discount_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(20),
            spacing=dp(10)
        )
        self.discount_label = MDLabel(
            text="优惠金额: ¥0.00",
            theme_text_color="Secondary",
            font_style="Subtitle1",
            # size_hint=(0.4, 1)
        )
        # self.discount_value_label = MDLabel(
        #     text="¥0.00",
        #     theme_text_color="Primary",
        #     font_style="Subtitle2",
        #     size_hint=(0.6, 1)
        # )
        discount_layout.add_widget(self.discount_label)
        # discount_layout.add_widget(self.discount_value_label)

        # 总计
        self.total_label = MDLabel(
            text="应付总额: ¥0.00",
            theme_text_color="Error",
            font_style="Subtitle1"
        )

        order_card.add_widget(self.subtotal_label)
        # order_card.add_widget(shipping_label)
        order_card.add_widget(discount_layout)
        order_card.add_widget(self.total_label)

        # 支付方式卡片
        payment_card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(200),
            padding=dp(20),
            spacing=dp(10),
            elevation=dp(4),
            radius=[dp(10)]
        )

        payment_title = MDLabel(
            text="支付方式",
            theme_text_color="Primary",
            font_style="Subtitle1"
        )

        # 支付方式选择
        payment_layout = MDBoxLayout(orientation='vertical', spacing=10)

        self.payment_methods = [
            ("wechat", "微信支付", "wechat"),
            ("alipay", "支付宝", "alipay"),
            ("card", "银行卡支付", "credit-card"),
            ("cash", "货到付款", "cash")
        ]

        self.selected_payment = "cash"

        for method_id, method_name, icon in self.payment_methods:
            method_btn = MDRaisedButton(
                text=method_name,
                icon=icon,
                size_hint=(1, None),
                height=dp(40)
            )
            method_btn.bind(
                on_release=lambda x, m=method_id: self.select_payment(m)
            )
            payment_layout.add_widget(method_btn)

        payment_card.add_widget(payment_title)
        payment_card.add_widget(payment_layout)

        # 提交订单按钮
        submit_btn = MDRaisedButton(
            text="提交订单",
            size_hint=(1, None),
            height=dp(150),
            md_bg_color=(0.2, 0.8, 0.4, 1),
            pos_hint={'center_x': 0.5}
        )
        submit_btn.bind(on_release=self.submit_order)

        empty_label = MDLabel(
            text="",
            halign="center",
        )

        main_layout.add_widget(toolbar)
        main_layout.add_widget(order_card)
        main_layout.add_widget(self.items_card)
        # main_layout.add_widget(address_card)
        # main_layout.add_widget(payment_card)
        main_layout.add_widget(empty_label)
        main_layout.add_widget(submit_btn)

        self.add_widget(main_layout)

    def on_enter(self):
        """进入屏幕时更新数据"""
        self.update_order_info()

    def update_order_info(self):
        """更新订单信息"""
        from kivy.app import App
        app = App.get_running_app()

        original_subtotal = sum(item.price * item.quantity for item in app.cart.items.values())
        item_discount = app.cart.item_discount
        final_total = original_subtotal - item_discount

        self.subtotal_label.text = f"商品总价：¥{original_subtotal:.1f}"
        self.discount_label.text = f"优惠金额：¥{item_discount:.1f}"
        self.total_label.text = f"应付总额：¥{final_total:.1f}"

        self._update_items_table(app)

    def _update_items_table(self, app):
        """更新商品详情表格"""
        self.items_table_layout.clear_widgets()

        if not app.cart.items:
            self.items_card.height = dp(80)
            empty_label = MDLabel(
                text="暂无商品",
                theme_text_color="Hint",
                font_style="Caption",
                halign="center"
            )
            self.items_table_layout.add_widget(empty_label)
            self.items_table_layout.height = dp(30)
            return

        table_items = [["\n      名称", "\n 数量", "\n    原价", "\n   折扣价"]]
        for item in app.cart.items.values():
            original_ss = float(item.price) * item.quantity
            discount_price = item.discount_price if item.discount_price is not None else item.price
            discount_ss = float(discount_price) * item.quantity
            table_items.append([
                f"• {item.product_name}",
                f" × {item.quantity}",
                f" ¥{original_ss:.1f}",
                f" ¥{discount_ss:.1f}"
            ])

        size_x_arr = [0.4, 0.15, 0.225, 0.225]
        for i, cols in enumerate(list(zip(*table_items))):
            item_text = MDLabel(
                text="\n".join(cols),
                theme_text_color="Secondary",
                size_hint=(size_x_arr[i], 1),
                font_style="Caption",
            )
            self.items_table_layout.add_widget(item_text)

        table_height = dp(20 * (len(app.cart.items) + 1))
        self.items_table_layout.height = table_height
        self.items_card.height = table_height + dp(80)

    def select_payment(self, method_id):
        """选择支付方式"""
        self.selected_payment = method_id

    def submit_order(self, *args):
        """提交订单"""
        from kivy.app import App
        app = App.get_running_app()

        # 检查库存
        for item in app.cart.items.values():
            product = app.db.get_product(item.product_id)
            if not product or product.stock < item.quantity:
                MDSnackbar(
                    MDLabel(text=f"商品 {item.product_name} 库存不足", theme_text_color="Custom",
                            text_color=(0.9, 0.2, 0.2, 1))
                ).open()
                return

        # 创建订单数据
        from datetime import datetime
        original_subtotal = sum(item.price * item.quantity for item in app.cart.items.values())
        item_discount = app.cart.item_discount
        final_total = original_subtotal - item_discount

        order_data = {
            'items': [],
            'subtotal': original_subtotal,
            'discount': item_discount,
            'total': final_total,
            'address': app.screen_manager.get_screen("cart").address_label.text,
            'payment_method': self.selected_payment,
            'order_id': self.generate_order_id(),
            'order_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # 转换购物车项
        for item in app.cart.items.values():
            item_dict = {
                'product_id': item.product_id,
                'product_name': item.product_name,
                'price': float(item.price),
                'discount_price': float(item.discount_price) if item.discount_price is not None else float(item.price),
                'quantity': item.quantity,
                'image': item.image,
                'specifications': item.specifications
            }
            order_data['items'].append(item_dict)

        # 完成订单
        order = app.complete_order(order_data)

        # 显示订单确认
        self.confirm_order_dialog = MDDialog(
            title="订单创建成功",
            type="custom",
            size_hint_x=None,
            width=dp(320),
            content_cls=MDBoxLayout(
                orientation='vertical',
                spacing=dp(10),
                size_hint_y=None,
                height=dp(120)
            ),
            buttons=[
                MDRaisedButton(
                    text="查看订单",
                    on_release=lambda x: self.view_order(order)
                ),
                MDFlatButton(
                    text="返回购物车",
                    on_release=lambda x: self.go_back(self.confirm_order_dialog)
                )
            ]
        )
        order_info = MDLabel(
            text=f"订单号：{order.order_id[:20]}\n"
                 f"支付金额：¥{order.total:.1f}\n"
                 f"收货地址：{order.address}\n"
                 f"支付方式：{order.payment_method}\n"
                 f"订单状态：已完成",
            font_style='Caption',
        )
        self.confirm_order_dialog.content_cls.add_widget(order_info)
        self.confirm_order_dialog.open()

    def view_order(self, order):
        """ 调用 订单管理界面 的显示详情函数 """
        OrdersScreen().show_order_detail(order, has_delete=False)  # 仅供查看，不包含删除按钮

    def generate_order_id(self, length: int = 40) -> str:
        """
        生成类似Git Commit ID的订单ID
        :param length: 长度（SHA-1默认40位，SHA-256默认64位，建议≤40）
        :return: 十六进制随机字符串
        """
        import hashlib
        import os
        # 1. 生成高熵随机字节（20字节=160位，对应SHA-1的40位哈希）
        random_bytes = os.urandom(20)  # os.urandom是系统级高熵随机数，比random模块更安全

        # 2. SHA-1哈希（模拟Git Commit ID的哈希算法）
        sha1_hash = hashlib.sha1(random_bytes).hexdigest()  # 输出40位十六进制字符串

        # 3. 截取指定长度（保证长度可控）
        if length > 40:
            raise ValueError("长度不能超过40位（SHA-1哈希最大40位）")
        return sha1_hash[:length]

    def go_back(self, *args):
        if hasattr(self, 'confirm_order_dialog') and self.confirm_order_dialog:
            self.confirm_order_dialog.dismiss()

        """返回购物车"""
        from kivy.app import App
        app = App.get_running_app()
        app.show_cart()
