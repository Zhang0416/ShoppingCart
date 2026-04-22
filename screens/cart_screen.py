from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, ThreeLineListItem
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp, sp
from datetime import datetime

from .assets.config_chinese import CHINESE_FONT_NAME


class CartScreen(Screen):
    total_price = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "cart"
        self._build_ui()

    def _build_ui(self):
        # 主布局
        main_layout = MDBoxLayout(orientation='vertical')

        # 顶部工具栏
        toolbar = MDTopAppBar(
            title="购物车",
            elevation=dp(4),
            md_bg_color=(0.2, 0.6, 0.86, 1),
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[["refresh", lambda x: self.refresh()]]
        )

        # 购物车内容区域
        from kivy.uix.scrollview import ScrollView
        self.scroll_view = ScrollView()
        self.cart_layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(10),
            size_hint_y=None
        )
        self.cart_layout.bind(minimum_height=self.cart_layout.setter('height'))
        self.scroll_view.add_widget(self.cart_layout)

        # 收货地址卡片（从 CheckoutScreen 迁移）
        self.address_card = MDCard(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(80),
            padding=dp(20),
            spacing=dp(10),
            elevation=dp(4),
            radius=[dp(10)]
        )

        self.address_label = MDLabel(
            text="选择收件人信息",
            theme_text_color="Hint",
            font_style="Subtitle2"
        )

        self.change_address_btn = MDRaisedButton(
            text="点击选择",
            size_hint=(None, 1),
            md_bg_color=(0.6, 0.4, 0.6, 1),
            on_release=self.open_address_menu
        )

        self.address_card.add_widget(self.address_label)
        self.address_card.add_widget(self.change_address_btn)

        # 底部结算栏
        bottom_layout = MDCard(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(80),
            padding=dp(20),
            spacing=dp(20),
            elevation=dp(8),
            radius=[dp(10), dp(10), 0, 0]
        )

        # 总计
        self.total_label = MDLabel(
            text=f"总计: ¥0.00",
            theme_text_color="Error",
            font_style="Headline6",
            size_hint=(0.35, 1)
        )

        # 导入历史订单按钮
        self.import_btn = MDRaisedButton(
            text="导入历史订单",
            size_hint=(0.3, 1),
            md_bg_color=(0.9, 0.5, 0.1, 1)
        )
        # self.import_btn._lbl.max_lines = 2
        # self.import_btn._lbl.shorten = False
        # self.import_btn._lbl.halign = 'center'
        self.import_btn.bind(on_release=self.show_import_orders)

        # 结算按钮
        self.checkout_btn = MDRaisedButton(
            text="去结算",
            size_hint=(0.3, 1),
            md_bg_color=(0.2, 0.8, 0.4, 1)
        )
        self.checkout_btn.bind(on_release=self.checkout)

        bottom_layout.add_widget(self.total_label)
        bottom_layout.add_widget(self.import_btn)
        bottom_layout.add_widget(self.checkout_btn)

        # 空购物车提示
        self.empty_label = MDLabel(
            text="购物车是空的",
            halign="center",
            theme_text_color="Hint",
            font_style="Headline5"
        )
        self.empty_label.opacity = 0

        main_layout.add_widget(toolbar)
        main_layout.add_widget(self.scroll_view)
        main_layout.add_widget(self.address_card)
        main_layout.add_widget(bottom_layout)

        self.add_widget(main_layout)

    def on_enter(self):
        """进入屏幕时更新购物车"""
        self.update_cart()

    def update_cart(self):
        """更新购物车显示"""
        from kivy.app import App
        app = App.get_running_app()

        # 清空现有内容
        self.cart_layout.clear_widgets()

        # 检查购物车是否为空
        if app.cart.item_count == 0:
            self.empty_label.opacity = 1
            self.total_label.text = " 购物车为空 "
            self.checkout_btn.text = "去选购"
            self.checkout_btn.unbind(on_release=self.checkout)
            self.checkout_btn.bind(on_release=self.go_back)
            self.import_btn.disabled = True
            self.address_card.opacity = 0
            self.address_card.height = 0
            self.address_card.disabled = True
            return
        else:
            self.checkout_btn.text = "去结算"
            self.checkout_btn.bind(on_release=self.checkout)
            self.checkout_btn.unbind(on_release=self.go_back)
            self.import_btn.disabled = False
            self.address_card.opacity = 1
            self.address_card.height = dp(80)
            self.address_card.disabled = False

        self.empty_label.opacity = 0

        # 添加购物车项
        for item in app.cart.items.values():
            from .components.cart_item import CartItemWidget
            cart_item = CartItemWidget(
                product_id=item.product_id,
                name=item.product_name,
                price=item.price,
                quantity=item.quantity,
                image_url=item.image,
                discount_price=item.discount_price
            )
            self.cart_layout.add_widget(cart_item)

        # 更新总价
        item_discount = app.cart.item_discount
        coupon_discount = app.cart.discount
        total = app.cart.total
        if item_discount > 0 or coupon_discount > 0:
            total_discount = item_discount + coupon_discount
            self.total_label.text = f"数量：{app.cart.item_count}  优惠：¥{total_discount:.1f}\n总价: ¥{total:.1f}"
        else:
            self.total_label.text = f"数量：{app.cart.item_count}\n总价: ¥{total:.1f}"

    # ========== 地址相关（从 CheckoutScreen 迁移） ==========

    def open_address_menu(self, *args):
        from kivy.app import App
        app = App.get_running_app()

        user = None
        for u in app.user_manager.users:
            if u["phone"] == app.current_user['phone']:
                user = u
                break

        if not user:
            return

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
            hor_growth="right",
        )
        self.menu.width = dp(500)
        self.menu.open()

    def select_address(self, address):
        self.address_label.text = address
        self.address_label.theme_text_color = "Primary"
        if self.menu:
            self.menu.dismiss()

    # ========== 导入历史订单 ==========

    def show_import_orders(self, *args):
        """显示可导入的历史订单列表"""
        from kivy.app import App
        app = App.get_running_app()

        if not app.current_user:
            MDSnackbar(MDLabel(text="请先登录", text_color=(0.9, 0.2, 0.2, 1))).open()
            return

        orders = app.order_manager.get_orders_by_user(app.current_user['phone'])

        # 如果已选择地址，按收件人和地址筛选
        current_address = self.address_label.text
        if current_address != "选择收件人信息":
            filtered_orders = []
            for order in orders:
                # 地址格式: 姓名~电话~地址
                current_parts = current_address.split('~')
                order_parts = order.address.split('~')
                # 比较收件人(姓名~电话)和地址
                if len(current_parts) >= 3 and len(order_parts) >= 3:
                    current_recipient = '~'.join(current_parts[:-1])
                    order_recipient = '~'.join(order_parts[:-1])
                    if current_recipient == order_recipient and current_parts[-1] == order_parts[-1]:
                        filtered_orders.append(order)
            orders = filtered_orders

        if not orders:
            dialog = MDDialog(
                title="导入历史订单",
                text="暂无历史订单",
                buttons=[
                    MDFlatButton(text="关闭", on_release=lambda x: dialog.dismiss())
                ]
            )
            dialog.ids.title.font_name = CHINESE_FONT_NAME
            dialog.open()
            return

        scroll_view = MDScrollView()
        orders_list = MDList()

        for order in orders[::-1]:
            time_str = datetime.fromisoformat(order.created_at).strftime("%Y-%m-%d %H:%M")
            item = ThreeLineListItem(
                text=f"订单号：{order.order_id[:20]}",
                secondary_text=f"收货人：{order.address}",
                tertiary_text=f"金额：¥{order.total:.1f} | 时间：{time_str}",
                font_style='Caption',
                secondary_font_style='Overline',
                tertiary_font_style='Overline'
            )
            item.bind(on_release=lambda x, o=order: self.show_import_order_detail(o))
            orders_list.add_widget(item)

        scroll_view.add_widget(orders_list)

        self.import_orders_dialog = MDDialog(
            title="选择要导入的订单",
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
                    on_release=lambda x: self.import_orders_dialog.dismiss()
                )
            ]
        )
        self.import_orders_dialog.ids.title.font_name = CHINESE_FONT_NAME
        self.import_orders_dialog.content_cls.add_widget(scroll_view)
        self.import_orders_dialog.open()

    def show_import_order_detail(self, order):
        """显示订单详情，提供导入按钮"""
        if hasattr(self, 'import_orders_dialog') and self.import_orders_dialog:
            self.import_orders_dialog.dismiss()

        scroll_view = MDScrollView()
        detail_list = MDList()

        # 订单信息
        detail_list.add_widget(MDLabel(
            text="----------- 订单信息 -----------",
            theme_text_color="Primary",
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(20)
        ))

        tmp = order.address.split('~')
        info_texts = [
            f"收货人: {'~'.join(tmp[:-1])}",
            f"收货地址: {tmp[-1]}",
            f"下单时间: {order.user_name}~{datetime.fromisoformat(order.created_at).strftime('%Y-%m-%d %H:%M:%S')}",
            f"订单号: {order.order_id[:20]}",
        ]
        for text in info_texts:
            detail_list.add_widget(MDLabel(
                text=text,
                theme_text_color="Secondary",
                size_hint_y=None,
                font_style="Caption",
                height=dp(20)
            ))

        # 商品列表标题
        detail_list.add_widget(MDLabel(
            text="----------- 商品列表 -----------",
            theme_text_color="Primary",
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(20)
        ))

        # 商品表格（4列：名称、数量、原价、折扣价）
        table_items = [["\n      名称", "\n 数量", "\n    原价", "\n   折扣价"]]
        for item in order.items:
            original_ss = float(item['price']) * item['quantity']
            discount_price = item.get('discount_price', item['price'])
            discount_ss = float(discount_price) * item['quantity']
            table_items.append([
                f"• {item['product_name']}",
                f" × {item['quantity']}",
                f" ¥{original_ss:.1f}",
                f" ¥{discount_ss:.1f}"
            ])

        table_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(18 * (len(order.items) + 1)),
            padding=dp(10),
            spacing=dp(0)
        )
        size_x_arr = [0.4, 0.15, 0.225, 0.225]
        for i, cols in enumerate(list(zip(*table_items))):
            table_layout.add_widget(MDLabel(
                text="\n".join(cols),
                theme_text_color="Secondary",
                size_hint=(size_x_arr[i], 1),
                font_style="Caption",
            ))
        detail_list.add_widget(table_layout)

        # 金额汇总
        detail_list.add_widget(MDLabel(
            text="\n\n----------- 金额汇总 -----------",
            theme_text_color="Primary",
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(20)
        ))

        summary_text = f"""\n\n\n\n\n
        商品总数: {sum(item['quantity'] for item in order.items)}
        商品小计: ¥{order.subtotal:.1f}
        优惠金额: ¥{order.discount:.1f}
        应付总额: ¥{order.total:.1f}
        """
        detail_list.add_widget(MDLabel(
            text=summary_text,
            theme_text_color="Error",
            font_style="Subtitle2",
            size_hint_y=None,
            height=dp(40)
        ))

        scroll_view.add_widget(detail_list)

        self.import_detail_dialog = MDDialog(
            title="订单详情",
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
                MDRaisedButton(
                    text="导入",
                    md_bg_color=(0.2, 0.8, 0.4, 1),
                    on_release=lambda x, o=order: self.do_import_order(o)
                ),
                MDFlatButton(
                    text="关闭",
                    on_release=lambda x: self.import_detail_dialog.dismiss()
                )
            ]
        )
        self.import_detail_dialog.ids.title.font_name = CHINESE_FONT_NAME
        self.import_detail_dialog.content_cls.add_widget(scroll_view)
        self.import_detail_dialog.open()

    def do_import_order(self, order):
        """执行导入：将订单中折扣价应用到购物车"""
        from kivy.app import App
        app = App.get_running_app()

        imported_count = 0
        for item in order.items:
            product_id = item['product_id']
            discount_price = item.get('discount_price')
            # 只导入有折扣价且低于原价的商品，并且购物车中存在该商品
            if discount_price is not None and discount_price < item['price']:
                if product_id in app.cart.items:
                    app.cart.update_discount_price(product_id, float(discount_price))
                    imported_count += 1

        self.import_detail_dialog.dismiss()

        # 刷新购物车显示
        self.update_cart()

        MDSnackbar(
            MDLabel(
                text=f"成功导入 {imported_count} 个商品的折扣价",
                theme_text_color="Custom",
                text_color=(0.2, 0.8, 0.2, 1)
            )
        ).open()

    def refresh(self):
        """刷新"""
        MDSnackbar(
            MDLabel(text="购物车已刷新", theme_text_color="Custom", text_color=(0.2, 0.8, 0.2, 1))
        ).open()

    def go_back(self, *args):
        """返回商品页"""
        from kivy.app import App
        app = App.get_running_app()
        app.show_products()

    def checkout(self, *args):
        """结算"""
        from kivy.app import App
        app = App.get_running_app()

        if app.cart.item_count == 0:
            MDSnackbar(
                MDLabel(text="购物车为空", theme_text_color="Custom", text_color=(0.9, 0.2, 0.2, 1))
            ).open()
            return

        app.show_checkout()
