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
from kivymd.uix.list import MDList, IconLeftWidget, IconRightWidget, ThreeLineAvatarIconListItem
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
            height=dp(200),
            padding=dp(20),
            spacing=dp(10),
            elevation=dp(4),
            radius=[dp(10)]
        )

        # 商品总价
        self.subtotal_label = MDLabel(
            text="商品总价: ¥0.00",
            theme_text_color="Primary",
            font_style="Subtitle2"
        )

        # 运费
        shipping_label = MDLabel(
            text="运费: ¥0.00",
            theme_text_color="Primary",
            font_style="Subtitle2"
        )

        # 优惠
        discount_label = MDLabel(
            text="优惠: -¥0.00",
            theme_text_color="Secondary",
            font_style="Subtitle2"
        )

        # 总计
        self.total_label = MDLabel(
            text="应付总额: ¥0.00",
            theme_text_color="Error",
            font_style="Subtitle2"
        )

        order_card.add_widget(self.subtotal_label)
        # order_card.add_widget(shipping_label)
        order_card.add_widget(discount_label)
        order_card.add_widget(self.total_label)

        # 收货地址卡片
        address_card = MDCard(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(120),
            padding=dp(20),
            spacing=dp(10),
            elevation=dp(4),
            radius=[dp(10)]
        )

        # address_title = MDLabel(
        #     text="收货地址",
        #     theme_text_color="Primary",
        #     font_style="Subtitle1"
        # )

        self.address_label = MDLabel(
            text="选择收件人信息",
            theme_text_color="Hint",
            font_style="Subtitle1"
        )

        self.change_address_btn = MDRaisedButton(
            text="点击选择",
            size_hint=(None, None),
            size=("200sp", "40sp"),
            on_release=self.open_address_menu
        )

        # address_card.add_widget(address_title)
        address_card.add_widget(self.address_label)
        address_card.add_widget(self.change_address_btn)

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
            height=dp(100),
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
        main_layout.add_widget(address_card)
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

        self.subtotal_label.text = f"商品总价: ¥{app.cart.subtotal:.1f}"
        self.total_label.text = f"应付总额: ¥{app.cart.total:.1f}"

    def open_address_menu(self, *args):
        from kivy.app import App
        app = App.get_running_app()

        # 查找用户
        user = None
        for u in app.user_manager.users:
            if u["phone"] == app.current_user['phone']:
                user = u
                break

        if not user:
            return

        # 创建下拉菜单
        self.menu = MDDropdownMenu(
            caller=self.change_address_btn,
            items=[
                {
                    "text": address,
                    "viewclass": "OneLineListItem",
                    "height": dp(50),
                    "on_release": lambda x=address: self.select_address(x),
                } for address in user['usual_address']
            ],
            width_mult=1,
            # max_height=300,
            # position="center",
            hor_growth="right",  # 水平向右扩展（避免左侧裁剪）
        )
        self.menu.width = dp(500)
        # 打开菜单
        self.menu.open()
        # print("Menu width:", self.menu.width)  # 查看实际像素值

    def select_address(self, address):
        """选择地址"""
        # self.selected_address = address
        # self.root.ids.selected_address_label.text = address
        # self.root.ids.address_btn.text = "已选择地址"
        self.address_label.text = address
        self.address_label.theme_text_color = "Primary"

        # 关闭菜单
        if self.menu:
            self.menu.dismiss()

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
                    MDLabel(text=f"商品 {item.product_name} 库存不足", text_color=(0.9, 0.2, 0.2, 1))
                ).open()
                return

        # 创建订单数据
        from datetime import datetime
        order_data = {
            'items': [],
            'subtotal': app.cart.subtotal,
            'discount': app.cart.discount,
            'total': app.cart.total,
            'address': self.address_label.text,
            'payment_method': self.selected_payment,
            'order_id': self.generate_order_id(),  # 由 complete_order 方法生成
            'order_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 由 complete_order 方法生成
        }

        # 转换购物车项
        for item in app.cart.items.values():
            item_dict = {
                'product_id': item.product_id,
                'product_name': item.product_name,
                'price': float(item.price),
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
            text=f"订单号：{order.order_id}\n"
                 f"支付金额：¥{order.total:.1f}\n"
                 f"收货地址：{order.address}\n"
                 f"支付方式：{order.payment_method}\n"
                 f"订单状态：已完成",
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
        if hasattr(self, 'menu') and self.menu:
            self.menu.dismiss()

        """返回购物车"""
        from kivy.app import App
        app = App.get_running_app()
        app.show_cart()
