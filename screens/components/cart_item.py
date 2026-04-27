from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import NumericProperty, BooleanProperty, StringProperty
from kivy.animation import Animation
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.behaviors import HoverBehavior, TouchBehavior
from kivy.uix.widget import Widget
from kivy.metrics import dp, sp

from ..assets.config_chinese import CHINESE_FONT_NAME


class CartItemWidget(MDBoxLayout):
    """购物车项组件"""
    product_id = StringProperty()
    name = StringProperty()
    price = NumericProperty()
    quantity = NumericProperty()
    image_url = StringProperty()
    discount_price = NumericProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(2)
        self.padding = dp(5)
        self.size_hint_y = None
        self.height = dp(140)

        # ===== 第1行：商品信息横向布局 =====
        item_row = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(90),
            spacing=dp(10),
            padding=dp(5)
        )

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

        unit_price = self.discount_price if self.discount_price is not None else self.price
        self.subtotal_label = MDLabel(
            text=f"小计: ¥{unit_price * self.quantity:.1f}",
            theme_text_color="Secondary",
            font_style="Overline",
            size_hint_y=None,
            height=dp(20)
        )

        info_layout.add_widget(name_label)
        info_layout.add_widget(price_label)
        info_layout.add_widget(self.subtotal_label)

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
            size_hint_y=None,
            height=dp(40),
            pos_hint={'center_y': 0.5}
        )
        minus_btn.bind(on_release=self.decrease_quantity)

        self.quantity_field = MDTextField(
            text=str(self.quantity),
            mode="rectangle",
            size_hint_y=None,
            height=dp(40),
            pos_hint={'center_y': 0.5},
            input_filter="int"
        )
        self.quantity_field.bind(text=self.on_quantity_changed)

        plus_btn = MDIconButton(
            icon="plus",
            theme_text_color="Primary",
            icon_size='16sp',
            size_hint_y=None,
            height=dp(40),
            pos_hint={'center_y': 0.5}
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

        item_row.add_widget(image)
        item_row.add_widget(info_layout)
        item_row.add_widget(quantity_layout)
        item_row.add_widget(delete_btn)

        # ===== 第2行：折扣价设置布局 =====
        discount_row = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10),
            padding=[dp(10), 0]
        )

        discount_label = MDLabel(
            text="折扣单价:",
            theme_text_color="Custom",
            text_color=(0.2, 0.8, 0.2, 1),
            font_style="Overline",
            size_hint_x=None,
            width=dp(55)
        )

        self.discount_field = MDTextField(
            hint_text="...",
            text=f"{self.discount_price:.1f}" if self.discount_price is not None else "",
            # mode="fill",
            # fill_color=(0.94, 0.94, 0.94, 1),  # 浅灰色
            # text_color=(0.3, 0.69, 0.31, 1),    # 绿色
            size_hint_x=0.5,
            size_hint_y=None,
            height=dp(40),
            pos_hint={'center_y': 0.5},
            input_filter="float"
        )
        self.discount_field.font_name_hint_text = CHINESE_FONT_NAME
        self.discount_field.font_name = CHINESE_FONT_NAME

        set_btn = MDRaisedButton(
            text="设置",
            font_style="Overline",
            size_hint_x=None,
            height=dp(40),
            width=dp(60),
            md_bg_color=(0.2, 0.6, 0.86, 1)
        )
        set_btn.bind(on_release=self.set_discount_price)

        discount_row.add_widget(discount_label)
        discount_row.add_widget(self.discount_field)
        discount_row.add_widget(set_btn)

        self.add_widget(item_row)
        self.add_widget(discount_row)

    def update_subtotal_display(self):
        """更新小计显示"""
        unit_price = self.discount_price if self.discount_price is not None else self.price
        self.subtotal_label.text = f"小计: ¥{unit_price * self.quantity:.1f}"

    _UNSET = object()

    def refresh_display(self, quantity=None, discount_price=_UNSET):
        """增量刷新显示，不重建 widget

        Args:
            quantity: 新数量，为 None 时不更新
            discount_price: 新折扣价，使用 _UNSET 哨兵表示"不更新"，
                           传入 None 表示清空折扣价
        """
        if quantity is not None and quantity != self.quantity:
            self.quantity = quantity
            self.quantity_field.text = str(quantity)
        if discount_price is not CartItemWidget._UNSET:
            self.discount_price = discount_price
            self.discount_field.text = f"{discount_price:.1f}" if discount_price is not None else ""
        self.update_subtotal_display()

    def set_discount_price(self, *args):
        """设置折扣价"""
        from kivymd.uix.snackbar import MDSnackbar
        text = self.discount_field.text.strip()
        if not text:
            self.discount_price = None
        else:
            try:
                val = float(text)
                if val <= 0 or val > self.price:
                    MDSnackbar(
                        MDLabel(
                            text=f"折扣价必须大于0且不超过 ¥{self.price:.1f}",
                            theme_text_color="Custom",
                            text_color=(0.9, 0.2, 0.2, 1)
                        )
                    ).open()
                    return
                self.discount_price = val
            except ValueError:
                MDSnackbar(
                    MDLabel(
                        text="请输入有效的数字",
                        theme_text_color="Custom",
                        text_color=(0.9, 0.2, 0.2, 1)
                    )
                ).open()
                return

        from kivy.app import App
        app = App.get_running_app()
        app.update_cart_item_discount(self.product_id, self.discount_price)
        self.update_subtotal_display()

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
