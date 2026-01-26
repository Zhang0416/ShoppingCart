from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ListProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.behaviors import CommonElevationBehavior
from kivymd.uix.card import MDCard
from kivy.metrics import dp, sp

from .assets.config_chinese import CHINESE_FONT_NAME
from .components.models import ProductCategory
from .components.product_card import ProductCard


class ProductScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "products"
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
            text="商品列表",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_style="Headline6",
            font_size=sp(20),
            halign="center",
            size_hint=(0.6, 1)
        )

        # 购物车按钮
        cart_btn = MDIconButton(
            icon="cart",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)
        )
        cart_btn.bind(on_release=self.show_cart)

        toolbar.add_widget(back_btn)
        toolbar.add_widget(title)
        toolbar.add_widget(cart_btn)

        # 搜索栏
        search_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(80),
            padding=dp(10),
            spacing=dp(10)
        )

        self.search_input = MDTextField(
            hint_text="搜索商品...",
            mode="rectangle",
            size_hint=(0.8, 1)
        )
        self.search_input.font_name_hint_text = CHINESE_FONT_NAME
        self.search_input.font_name = CHINESE_FONT_NAME

        search_btn = MDRaisedButton(
            text="搜索",
            size_hint=(0.2, 1)
        )
        search_btn.bind(on_release=self.search_products)

        search_layout.add_widget(self.search_input)
        search_layout.add_widget(search_btn)

        # 分类标签
        self.tabs = ProductTabs()

        # 商品列表
        self.product_scroll = ScrollView()
        self.product_grid = GridLayout(
            cols=2,
            spacing=dp(5),
            padding=dp(5),
            size_hint_y=None
        )
        self.product_grid.bind(minimum_height=self.product_grid.setter('height'))
        self.product_scroll.add_widget(self.product_grid)

        main_layout.add_widget(toolbar)
        main_layout.add_widget(search_layout)
        main_layout.add_widget(self.tabs)
        main_layout.add_widget(self.product_scroll)

        self.add_widget(main_layout)

    def on_enter(self):
        """进入屏幕时加载商品"""
        self.load_products()

    def load_products(self, category=None, featured=False):
        """加载商品"""
        from kivy.app import App
        app = App.get_running_app()

        # 清空现有商品
        self.product_grid.clear_widgets()

        # 获取商品列表
        products = app.db.get_products(category=category, featured=featured)

        for product in products:
            card = ProductCard(
                product_id=product.id,
                name=product.name,
                description=product.description,
                price=product.price,
                image_url=product.images[0] if product.images else "",
                rating=product.rating,
                stock=product.stock
            )
            self.product_grid.add_widget(card)

    def search_products(self, *args):
        """搜索商品"""
        from kivy.app import App
        app = App.get_running_app()

        # 清空现有商品
        self.product_grid.clear_widgets()

        # 获取商品列表
        products = app.db.get_products()
        search_text = self.search_input.text.strip().lower()

        filtered_products = [
            p for p in products
            if search_text in str(p.name).lower() or search_text in str(p.category).lower()
        ]

        for product in filtered_products:
            card = ProductCard(
                product_id=product.id,
                name=product.name,
                description=product.description,
                price=product.price,
                image_url=product.images[0] if product.images else "",
                rating=product.rating,
                stock=product.stock
            )
            self.product_grid.add_widget(card)

    def go_back(self, *args):
        """返回登录页"""
        from kivy.app import App
        app = App.get_running_app()
        app.show_home()

    def show_cart(self, *args):
        """显示购物车"""
        from kivy.app import App
        app = App.get_running_app()
        app.show_cart()


class ProductTabs(MDBoxLayout):
    """商品分类标签"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (1, None)
        self.height = dp(50)
        self.spacing = dp(10)
        self.padding = dp(10)

        self._create_tabs()

    def _create_tabs(self):
        """创建分类标签"""
        categories = [
            ("全部", None),
            ("热门", ProductCategory.FEATURED),
            ("家居", ProductCategory.HOME),
            ("个护", ProductCategory.CARE),
            # ("服装", ProductCategory.CLOTHING),
            ("文具", ProductCategory.STATIONERY),
            ("电子", ProductCategory.ELECTRONICS)
        ]

        for name, category in categories:
            btn = MDRaisedButton(
                text=name,
                size_hint=(None, 1),
                width=dp(26)
            )
            cat_value = category.value if category is not None else category
            btn.bind(on_release=lambda x, cat=cat_value: self.on_tab_click(cat))
            self.add_widget(btn)

    def on_tab_click(self, category):
        """标签点击事件"""
        from kivy.app import App
        app = App.get_running_app()
        product_screen = app.root.get_screen("products")
        product_screen.load_products(category, category == "热门")
