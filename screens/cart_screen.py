from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.toolbar import MDTopAppBar
from kivy.metrics import dp, sp


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
            size_hint=(0.6, 1)
        )

        # 结算按钮
        checkout_btn = MDRaisedButton(
            text="去结算",
            size_hint=(0.4, 1),
            md_bg_color=(0.2, 0.8, 0.4, 1)
        )
        checkout_btn.bind(on_release=self.checkout)

        bottom_layout.add_widget(self.total_label)
        bottom_layout.add_widget(checkout_btn)

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
        # main_layout.add_widget(self.empty_label)
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
            self.total_label.text = " 购物车为空\n 快去选购吧"
            return

        self.empty_label.opacity = 0

        # 添加购物车项
        for item in app.cart.items.values():
            from .components.cart_item import CartItemWidget
            cart_item = CartItemWidget(
                product_id=item.product_id,
                name=item.product_name,
                price=item.price,
                quantity=item.quantity,
                image_url=item.image
            )
            self.cart_layout.add_widget(cart_item)

        # 更新总价
        self.total_label.text = f"数量：{app.cart.item_count}， 总价: ¥{app.cart.total:.1f}"

    def refresh(self):
        """刷新"""
        MDSnackbar(MDLabel(text="购物车已刷新", text_color=(0.2, 0.8, 0.2, 1))).open()

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
            from kivymd.uix.snackbar import MDSnackbar
            MDSnackbar(
                MDLabel(text="购物车为空", text_color=(0.9, 0.2, 0.2, 1))
            ).open()
            return

        app.show_checkout()
