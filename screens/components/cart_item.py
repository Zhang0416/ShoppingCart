from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import NumericProperty, BooleanProperty, StringProperty
from kivy.animation import Animation
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.behaviors import HoverBehavior, TouchBehavior
from kivy.uix.widget import Widget
from kivy.metrics import dp, sp


class CartItemWidget(MDBoxLayout):
    """购物车项组件"""
    product_id = StringProperty()
    name = StringProperty()
    price = NumericProperty()
    quantity = NumericProperty()
    image_url = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = dp(10)
        self.padding = dp(10)
        self.size_hint_y = None
        self.height = dp(100)

        # 商品图片
        from kivy.uix.image import AsyncImage
        image = AsyncImage(
            source=self.image_url,
            size_hint=(None, 1),
            width=dp(35),
        )

        # 商品信息
        info_layout = MDBoxLayout(orientation='vertical', size_hint=(0.3, 1))

        name_label = MDLabel(
            text=self.name,
            theme_text_color="Primary",
            font_style="Caption",
            size_hint_y=None,
            height=dp(20)
        )

        price_label = MDLabel(
            text=f"¥{self.price:.1f}",
            theme_text_color="Error",
            font_style="Overline",
            size_hint_y=None,
            height=dp(20)
        )

        subtotal_label = MDLabel(
            text=f"小计: ¥{self.price * self.quantity:.1f}",
            theme_text_color="Secondary",
            font_style="Overline",
            size_hint_y=None,
            height=dp(20)
        )

        info_layout.add_widget(name_label)
        info_layout.add_widget(price_label)
        info_layout.add_widget(subtotal_label)

        # 数量控制
        quantity_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint=(0.4, 1),
            spacing=dp(2)
        )

        minus_btn = MDIconButton(
            icon="minus",
            theme_text_color="Primary",
            icon_size='16sp',
            valign='center'
        )
        minus_btn.bind(on_release=self.decrease_quantity)

        self.quantity_field = MDTextField(
            text=str(self.quantity),
            mode="rectangle",
            # size_hint=(0.5, 0.3),
            # width=dp(20),
            input_filter="int"
        )
        self.quantity_field.bind(text=self.on_quantity_changed)

        plus_btn = MDIconButton(
            icon="plus",
            theme_text_color="Primary",
            icon_size='16sp',
            valign='center'
        )
        plus_btn.bind(on_release=self.increase_quantity)

        quantity_layout.add_widget(minus_btn)
        quantity_layout.add_widget(self.quantity_field)
        quantity_layout.add_widget(plus_btn)

        # 删除按钮
        delete_btn = MDIconButton(
            icon="delete",
            theme_text_color="Error",
            size_hint=(None, None),
        )
        delete_btn.bind(on_release=self.remove_item)

        self.add_widget(image)
        self.add_widget(info_layout)
        self.add_widget(quantity_layout)
        self.add_widget(delete_btn)

    def decrease_quantity(self, *args):
        """减少数量"""
        if self.quantity > 1:
            self.quantity -= 1
            self.quantity_field.text = str(self.quantity)
            self.update_cart()

    def increase_quantity(self, *args):
        """增加数量"""
        self.quantity += 1
        self.quantity_field.text = str(self.quantity)
        self.update_cart()

    def on_quantity_changed(self, instance, value):
        """数量输入变化"""
        try:
            self.quantity = int(value) if value else 1
            self.update_cart()
        except ValueError:
            pass

    def update_cart(self):
        """更新购物车"""
        from kivy.app import App
        app = App.get_running_app()
        app.update_cart_item(self.product_id, self.quantity)

        # 更新商品界面 购物车徽章
        product_screen = app.screen_manager.get_screen("products")
        product_screen.update_badge_color_text(app.cart.item_count)

    def remove_item(self, *args):
        """移除商品"""
        from kivy.app import App
        app = App.get_running_app()
        app.remove_from_cart(self.product_id)
