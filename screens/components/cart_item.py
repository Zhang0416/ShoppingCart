from kivy.app import App
from kivy.metrics import dp, sp
from kivy.properties import NumericProperty, BooleanProperty, StringProperty
from kivy.uix.image import AsyncImage
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton, MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.textfield import MDTextField

from ..assets.config_chinese import CHINESE_FONT_NAME


class CartItemWidget(MDBoxLayout):
    """购物车项组件"""
    product_id = StringProperty()
    name = StringProperty()
    price = NumericProperty()  # 零售价（建议零售价）
    cost_price = NumericProperty()  # 成本价
    quantity = NumericProperty()
    image_url = StringProperty()
    discount_price = NumericProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(2)
        self.padding = dp(5)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))

        # ===== 上层区域：图片 + 信息 =====
        upper_area = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(0),
            spacing=dp(8),
            padding=dp(2)
        )
        upper_area.bind(minimum_height=upper_area.setter('height'))

        # 商品图片
        image = AsyncImage(
            source=self.image_url,
            size_hint=(None, None),
            size=(dp(45), dp(45)),
            pos_hint={'center_y': 0.5}
        )

        # 信息区域（名称 + 价格/数量行）
        info_area = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(0),
            spacing=dp(1)
        )
        info_area.bind(minimum_height=info_area.setter('height'))

        # 商品名称（独占一行，横跨 info_area 全宽；高度自适应文字行数）
        name_label = MDLabel(
            text=self.name,
            theme_text_color="Primary",
            font_style="Caption",
            size_hint_y=None,
            height=dp(0),
            max_lines=2,
            halign='left',
            valign='top'
        )
        name_label.bind(
            width=lambda inst, val: setattr(inst, 'text_size', (val, None)),
            texture_size=lambda inst, val: setattr(inst, 'height', val[1])
        )

        # 详情行：价格/小计（左）+ 数量控制（右）
        details_row = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(0),
            spacing=dp(5)
        )
        details_row.bind(minimum_height=details_row.setter('height'))

        # 价格和小计（垂直排列）
        price_col = MDBoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            width=dp(90),
            height=dp(0),
            spacing=dp(1)
        )
        price_col.bind(minimum_height=price_col.setter('height'))

        price_label = MDLabel(
            text=f"¥{self.price:.1f}",
            theme_text_color="Error",
            font_style="Overline",
            size_hint_y=None,
            height=dp(18)
        )

        unit_price = self.discount_price if self.discount_price is not None else self.price
        self.subtotal_label = MDLabel(
            text=f"小计: ¥{unit_price * self.quantity:.1f}",
            theme_text_color="Secondary",
            font_style="Overline",
            size_hint_y=None,
            height=dp(18)
        )

        price_col.add_widget(price_label)
        price_col.add_widget(self.subtotal_label)

        # 弹性 spacer，将数量控制推到右侧
        spacer = Widget(size_hint_x=1)

        # 数量控制
        quantity_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint=(None, None),
            width=dp(106),
            height=dp(32),
            spacing=dp(2),
            pos_hint={'center_y': 0.5}
        )

        minus_btn = MDIconButton(
            icon="minus",
            theme_text_color="Primary",
            icon_size='14sp',
            size_hint=(None, None),
            size=(dp(28), dp(28)),
            pos_hint={'center_y': 0.5}
        )
        minus_btn.bind(on_release=self.decrease_quantity)

        # 使用 TextInput 替代 MDTextField，避免 KivyMD 的 minimum_height 绑定导致高度失控
        self.quantity_field = TextInput(
            text=str(self.quantity),
            size_hint=(None, None),
            width=dp(44),
            height=dp(32),
            pos_hint={'center_y': 0.5},
            input_filter="int",
            halign="center",
            multiline=False,
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            cursor_color=(0, 0, 0, 1),
            padding=[dp(4), dp(6), dp(4), dp(4)],
            font_size=sp(14)
        )
        self.quantity_field.bind(text=self.on_quantity_changed)

        plus_btn = MDIconButton(
            icon="plus",
            theme_text_color="Primary",
            icon_size='14sp',
            size_hint=(None, None),
            size=(dp(28), dp(28)),
            pos_hint={'center_y': 0.5}
        )
        plus_btn.bind(on_release=self.increase_quantity)

        quantity_layout.add_widget(minus_btn)
        quantity_layout.add_widget(self.quantity_field)
        quantity_layout.add_widget(plus_btn)

        details_row.add_widget(price_col)
        details_row.add_widget(spacer)
        details_row.add_widget(quantity_layout)

        info_area.add_widget(name_label)
        info_area.add_widget(details_row)

        upper_area.add_widget(image)
        upper_area.add_widget(info_area)

        # ===== 折扣价设置行 =====
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

        self.add_widget(upper_area)
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
        """设置折扣价：必须低于零售价，且高于成本价的30%"""
        text = self.discount_field.text.strip()
        if not text:
            self.discount_price = None
        else:
            try:
                val = float(text)
                min_price = self.cost_price * 0.3
                if val <= 0 or val > self.price:
                    MDSnackbar(
                        MDLabel(
                            text=f"折扣价必须大于0且不超过 ¥{self.price:.1f}",
                            theme_text_color="Custom",
                            text_color=(0.9, 0.2, 0.2, 1)
                        )
                    ).open()
                    return
                if val < min_price:
                    MDSnackbar(
                        MDLabel(
                            text=f"折扣价不能低于成本价的30% (¥{min_price:.1f})",
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

        app = App.get_running_app()
        app.update_cart_item_discount(self.product_id, self.discount_price)
        self.update_subtotal_display()

    def decrease_quantity(self, *args):
        """减少数量；当数量为1时再次点击，弹出确认删除对话框"""
        if self.quantity > 1:
            self.quantity -= 1
            self.quantity_field.text = str(self.quantity)
            self.update_cart()
        else:
            self._show_confirm_delete_dialog()

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
        app = App.get_running_app()
        app.update_cart_item(self.product_id, self.quantity)

        # 更新商品界面 购物车徽章
        product_screen = app.screen_manager.get_screen("products")
        product_screen.update_badge_color_text(app.cart.item_count)

    def _show_confirm_delete_dialog(self):
        """弹出确认删除商品对话框"""
        self.confirm_delete_dialog = MDDialog(
            title="删除商品",
            size_hint_x=0.9,
            background_color=(0, 0, 0, 0),
            type="custom",
            content_cls=MDBoxLayout(
                orientation='vertical',
                spacing=dp(10),
                size_hint_y=None,
                height=dp(40)
            ),
            buttons=[
                MDFlatButton(
                    text="点错了返回",
                    on_release=lambda x: self.confirm_delete_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="确认删除",
                    md_bg_color=(0.9, 0.2, 0.2, 1),
                    on_release=lambda x: (
                        self.confirm_delete_dialog.dismiss(),
                        self.remove_item()
                    )
                ),
            ]
        )
        self.confirm_delete_dialog.ids.title.font_name = CHINESE_FONT_NAME
        self.confirm_delete_dialog.open()

    def remove_item(self, *args):
        """移除商品"""
        app = App.get_running_app()
        app.remove_from_cart(self.product_id)
