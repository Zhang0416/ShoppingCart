from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivymd.uix.behaviors import CommonElevationBehavior
from kivy.uix.modalview import ModalView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.chip import MDChip, MDChipText
from kivymd.uix.fitimage import FitImage
from kivy.uix.image import Image
from kivymd.uix.list import MDList
from kivymd.uix.scrollview import MDScrollView
from kivy.metrics import dp, sp


class ProductDetailDialog(ModalView):
    """商品详情对话框"""

    def __init__(self, product_data, **kwargs):
        super().__init__(**kwargs)
        self.product_data = product_data
        self.size_hint = (0.9, 0.9)
        self.auto_dismiss = True
        self.overlay_color = (1, 1, 1, 0.7)
        self.radius = [dp(25)] * 4

        self._build_ui()

    def _build_ui(self):
        """构建UI"""
        # 主容器
        main_box = MDBoxLayout(
            orientation="vertical",
            md_bg_color=(0.95, 0.95, 0.95, 1),
            spacing=dp(20),
            padding=dp(20)
        )

        # 标题栏
        title_bar = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(50)
        )

        title_label = MDLabel(
            text="商品详情",
            font_style="H5",
            bold=True,
            halign="center",
            size_hint_x=0.8
        )

        close_button = MDIconButton(
            icon="close",
            theme_icon_color="Custom",
            icon_color=(0.46, 0.46, 0.46, 1),
            on_release=lambda x: self.dismiss()
        )

        title_bar.add_widget(title_label)
        title_bar.add_widget(close_button)

        # 滚动区域
        scroll_view = MDScrollView(do_scroll_x=False)
        content_list = MDList()

        # 内容区域
        # content_box = MDBoxLayout(
        #     orientation="vertical",
        #     spacing=20
        # )

        # 商品大图
        detail_image = FitImage(
            source=self.product_data.images[0],
            size_hint=(None, None),  # 关键：禁用自动缩放
            size=(sp(200), sp(360)),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            radius=[dp(15)] * 4
        )

        # scroll_content = MDBoxLayout(
        #     orientation="vertical",
        #     spacing=15,
        #     size_hint_y=None,
        #     padding=10
        # )
        # scroll_content.bind(minimum_height=scroll_content.setter('height'))

        # 商品名称
        name_label = MDLabel(
            text=self.product_data.name,
            font_style="H6",
            bold=True,
            size_hint_y=None,
            height=dp(40),
            halign="left"
        )

        # 价格
        price_label = MDLabel(
            text=f"价格: ￥{self.product_data.price:.1f}",
            font_style="H6",
            theme_text_color="Error",
            bold=True,
            size_hint_y=None,
            height=dp(50)
        )

        # 标签行
        chip_row = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )

        category_chip = MDChip()
        category_chip.add_widget(MDChipText(text=self.product_data.category))

        stock_chip = MDChip()
        stock_chip.add_widget(MDChipText(text=f"库存: {self.product_data.stock}", text_color=(0, 1, 1, 1)))

        chip_row.add_widget(category_chip)
        chip_row.add_widget(stock_chip)

        # 描述标题
        desc_title = MDLabel(
            text="商品描述:",
            font_style="Subtitle1",
            bold=True,
            size_hint_y=None,
            height=dp(50),
            halign="left"
        )

        # 描述内容
        desc_label = MDLabel(
            text=self.product_data.description,
            font_style="Body1",
            size_hint_y=None,
            height=dp(50),
            halign="left"
        )

        spec_info_string = ""
        if isinstance(self.product_data.specifications, dict):
            for key, val in self.product_data.specifications.items():
                spec_info_string += f"{key}: {val}\n"
        elif isinstance(self.product_data.specifications, list):
            for val in self.product_data.specifications:
                spec_info_string += f"{val}\n"
        elif isinstance(self.product_data.specifications, str):
            spec_info_string = self.product_data.specifications
        spec_label = MDLabel(
            text=spec_info_string,
            font_style="Body2",
            size_hint_y=None,
            height=dp(50),
            halign="left"
        )

        # 商品ID
        id_label = MDLabel(
            text=f"商品ID: {self.product_data.id}",
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(20),
            halign="left"
        )

        # 添加到滚动内容
        content_list.add_widget(detail_image)
        content_list.add_widget(name_label)
        content_list.add_widget(price_label)
        content_list.add_widget(chip_row)
        content_list.add_widget(desc_title)
        content_list.add_widget(desc_label)
        content_list.add_widget(spec_label)
        content_list.add_widget(id_label)
        # scroll_content.height = sum([c.height for c in scroll_content.children]) + 100

        scroll_view.add_widget(content_list)

        # 加入购物车按钮
        cart_button = MDRaisedButton(
            text="加入购物车",
            size_hint_x=0.7,
            md_bg_color=(0.298, 0.686, 0.314, 1),
            on_release=self.add_to_cart
        )

        # 组装所有组件
        # content_box.add_widget(detail_image)
        # content_box.add_widget(scroll_view)

        main_box.add_widget(title_bar)
        main_box.add_widget(scroll_view)
        main_box.add_widget(cart_button)

        self.add_widget(main_box)

    def add_to_cart(self, *args):
        """添加到购物车"""
        from kivy.app import App
        app = App.get_running_app()
        app.add_to_cart(self.product_data.id)


class ProductCard(MDCard, CommonElevationBehavior):
    """商品卡片组件"""
    product_id = StringProperty()
    name = StringProperty()
    description = StringProperty()
    price = NumericProperty()
    image_url = StringProperty()
    rating = NumericProperty()
    stock = NumericProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        self.width = dp(200)
        self.height = dp(300)
        self.padding = dp(10)
        self.spacing = dp(5)
        self.radius = [dp(15)]

        # 绑定点击事件
        self.bind(on_release=self.show_product_detail)

        # 商品图片
        image = Image(
            source=self.image_url,
            size_hint=(1, 0.5),
            allow_stretch=True
        )

        # 商品信息
        info_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.5))

        # 名称
        name_label = MDLabel(
            text=self.name,
            theme_text_color="Primary",
            font_style="Headline6",
            size_hint_y=None,
            height=dp(30),
            halign="center"
        )

        # 价格
        price_label = MDLabel(
            text=f"¥{self.price:.1f}",
            theme_text_color="Error",
            font_style="Headline6",
            size_hint_y=None,
            height=dp(30),
            halign="center"
        )

        # 库存
        stock_label = MDLabel(
            text=f"库存: {self.stock}",
            theme_text_color="Hint",
            size_hint_y=None,
            height=dp(20)
        )

        # 添加到购物车按钮
        add_btn = MDRaisedButton(
            icon="cart-plus",
            icon_color=(0, 1, 0, 1),
            icon_size=sp(12),
            text="加入购物车",
            size_hint=(1, None),
            height=dp(40),
            md_bg_color=(0.2, 0.6, 0.86, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.6}
        )
        add_btn.bind(on_release=self.add_to_cart)

        info_layout.add_widget(name_label)
        info_layout.add_widget(price_label)
        # info_layout.add_widget(stock_label)
        info_layout.add_widget(add_btn)

        self.add_widget(image)
        self.add_widget(info_layout)

    def show_product_detail(self, *args):
        """显示商品详情"""
        from kivy.app import App
        app = App.get_running_app()

        # 获取商品列表
        products = app.db.get_products()
        product = next((p for p in products if p.id == self.product_id), None)

        # print(product)
        if product:
            dialog = ProductDetailDialog(product_data=product)
            dialog.open()

    def add_to_cart(self, *args):
        """添加到购物车"""
        from kivy.app import App
        app = App.get_running_app()
        app.add_to_cart(self.product_id)
