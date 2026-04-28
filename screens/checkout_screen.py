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


class CheckoutScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "checkout"
        self.selected_payment = "cash"
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

        # 1. 收货人信息卡片
        self.receiver_card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(130),
            padding=dp(15),
            spacing=dp(5),
            elevation=dp(4),
            radius=[dp(10)]
        )
        receiver_title = MDLabel(
            text="收货人信息",
            theme_text_color="Primary",
            font_style="Subtitle1",
            size_hint=(1, None),
            height=dp(30)
        )
        self.receiver_name_label = MDLabel(
            text="收货人：--",
            theme_text_color="Secondary",
            font_style="Caption",
            size_hint=(1, None),
            height=dp(22)
        )
        self.receiver_phone_label = MDLabel(
            text="电话：--",
            theme_text_color="Secondary",
            font_style="Caption",
            size_hint=(1, None),
            height=dp(22)
        )
        self.receiver_address_label = MDLabel(
            text="地址：--",
            theme_text_color="Secondary",
            font_style="Caption",
            size_hint_y=None,
            height=dp(22)
        )
        # 地址自适应高度，并同步更新卡片高度
        self.receiver_address_label.bind(
            width=lambda inst, w: setattr(inst, 'text_size', (w, None)),
            texture_size=lambda inst, ts: (
                setattr(inst, 'height', max(ts[1], dp(22))),
                setattr(self.receiver_card, 'height', dp(110) + max(ts[1], dp(22)))
            )
        )
        self.receiver_card.add_widget(receiver_title)
        self.receiver_card.add_widget(self.receiver_name_label)
        self.receiver_card.add_widget(self.receiver_phone_label)
        self.receiver_card.add_widget(self.receiver_address_label)

        # 2. 商品详情卡片
        self.items_card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(80),
            padding=dp(10),
            spacing=dp(5),
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
            orientation='vertical',
            size_hint=(1, None),
            height=dp(0),
            padding=dp(5),
            spacing=dp(2)
        )
        self.items_table_layout.bind(
            minimum_height=self.items_table_layout.setter('height')
        )
        self.items_table_layout.bind(
            height=lambda inst, h: setattr(self.items_card, 'height', h + dp(55))
        )
        self.items_card.add_widget(self.items_table_layout)

        # 3. 订单金额卡片
        order_card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(120),
            padding=dp(15),
            spacing=dp(10),
            elevation=dp(4),
            radius=[dp(10)]
        )

        # 商品总价
        self.subtotal_label = MDLabel(
            text="商品总价: ¥0.00",
            theme_text_color="Primary",
            font_style="Subtitle1"
        )

        # 优惠
        discount_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(22),
            spacing=dp(10)
        )
        self.discount_label = MDLabel(
            text="优惠金额: ¥0.00",
            theme_text_color="Secondary",
            font_style="Subtitle1",
        )
        discount_layout.add_widget(self.discount_label)

        # 总计
        self.total_label = MDLabel(
            text="应付总额: ¥0.00",
            theme_text_color="Error",
            font_style="Subtitle1"
        )

        order_card.add_widget(self.subtotal_label)
        order_card.add_widget(discount_layout)
        order_card.add_widget(self.total_label)

        # 提交订单按钮
        submit_btn = MDRaisedButton(
            text="提交订单",
            size_hint=(1, None),
            height=dp(50),
            md_bg_color=(0.2, 0.8, 0.4, 1),
            pos_hint={'center_x': 0.5}
        )
        submit_btn.bind(on_release=self.submit_order)

        empty_label = MDLabel(
            text="",
            halign="center",
        )

        main_layout.add_widget(toolbar)
        main_layout.add_widget(self.receiver_card)
        main_layout.add_widget(self.items_card)
        main_layout.add_widget(order_card)
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

        # 更新收货人信息
        cart_screen = app.screen_manager.get_screen("cart")
        address_text = cart_screen.address_label.text
        if address_text and '~' in address_text and address_text != "选择收件人信息":
            parts = address_text.split('~')
            if len(parts) >= 3:
                self.receiver_name_label.text = f"收货人：{parts[0]}"
                self.receiver_phone_label.text = f"电话：{parts[1]}"
                self.receiver_address_label.text = f"地址：{'~'.join(parts[2:])}"
            else:
                self.receiver_name_label.text = f"收货人：{parts[0] if parts else '--'}"
                self.receiver_phone_label.text = f"电话：{parts[1] if len(parts) > 1 else '--'}"
                self.receiver_address_label.text = f"地址：{address_text}"
        else:
            self.receiver_name_label.text = "收货人：--"
            self.receiver_phone_label.text = "电话：--"
            self.receiver_address_label.text = "地址：--"

        original_subtotal = sum(item.price * item.quantity for item in app.cart.items.values())
        item_discount = app.cart.item_discount
        final_total = original_subtotal - item_discount

        self.subtotal_label.text = f"商品总价：¥{original_subtotal:.1f}"
        self.discount_label.text = f"优惠金额：¥{item_discount:.1f}"
        self.total_label.text = f"应付总额：¥{final_total:.1f}"

        self._update_items_table(app)

    def _update_items_table(self, app):
        """更新商品详情表格——逐行独立布局，名称自适应高度"""
        self.items_table_layout.clear_widgets()

        if not app.cart.items:
            empty_label = MDLabel(
                text="暂无商品",
                theme_text_color="Hint",
                font_style="Caption",
                halign="center"
            )
            self.items_table_layout.add_widget(empty_label)
            return

        # 表头
        header = MDBoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(20),
            spacing=dp(2)
        )
        headers = [("名称", 0.4), ("数量", 0.15), ("原价", 0.225), ("折扣价", 0.225)]
        for text, ratio in headers:
            lbl = MDLabel(
                text=text,
                theme_text_color="Secondary",
                font_style="Caption",
                size_hint=(ratio, 1),
                halign="center",
                bold=True
            )
            header.add_widget(lbl)
        self.items_table_layout.add_widget(header)

        # 数据行
        for item in app.cart.items.values():
            original_ss = float(item.price) * item.quantity
            discount_price = item.discount_price if item.discount_price is not None else item.price
            discount_ss = float(discount_price) * item.quantity

            row = MDBoxLayout(
                orientation='horizontal',
                size_hint=(1, None),
                height=dp(20),
                spacing=dp(2)
            )

            name_lbl = MDLabel(
                text=f"• {item.product_name}",
                theme_text_color="Secondary",
                font_style="Caption",
                size_hint=(0.4, None),
                valign="center",
                height=dp(20)
            )
            name_lbl.bind(
                width=lambda inst, w: setattr(inst, 'text_size', (w, None)),
                texture_size=lambda inst, ts, r=row: [
                    setattr(inst, 'height', max(ts[1], dp(20))),
                    setattr(r, 'height', max(ts[1], dp(20)))
                ]
            )

            qty_lbl = MDLabel(
                text=f"×{item.quantity}",
                theme_text_color="Secondary",
                font_style="Caption",
                size_hint=(0.15, 1),
                halign="center",
                valign="center"
            )
            orig_lbl = MDLabel(
                text=f"¥{original_ss:.1f}",
                theme_text_color="Secondary",
                font_style="Caption",
                size_hint=(0.225, 1),
                halign="right",
                valign="center"
            )
            disc_lbl = MDLabel(
                text=f"¥{discount_ss:.1f}",
                theme_text_color="Secondary",
                font_style="Caption",
                size_hint=(0.225, 1),
                halign="right",
                valign="center"
            )

            row.add_widget(name_lbl)
            row.add_widget(qty_lbl)
            row.add_widget(orig_lbl)
            row.add_widget(disc_lbl)
            self.items_table_layout.add_widget(row)

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
            size_hint_x=0.9,
            background_color=(0, 0, 0, 0),
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
        from kivy.app import App
        app = App.get_running_app()
        orders_screen = app.screen_manager.get_screen("orders")
        orders_screen.show_order_detail(order, has_delete=False)  # 仅供查看，不包含删除按钮

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
