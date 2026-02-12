from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ListProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDIconButton
from kivymd.uix.behaviors import CommonElevationBehavior
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
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
        main_layout = MDBoxLayout(orientation='vertical', spacing=dp(10))

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

        # 徽章容器
        self.badge_layout = MDBoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            size=(dp(20), dp(5)),
            pos_hint={"right": 1, "top": 1},
            padding=0
        )

        # 徽章标签，用于显示购物车内商品数量
        self.badge_label = MDLabel(
            text='',
            font_style="Overline",
            bold=True,
            halign="right",
            size_hint=(1, 1),
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)  # 白色文字
        )
        self.badge_layout.add_widget(self.badge_label)

        toolbar.add_widget(back_btn)
        toolbar.add_widget(title)
        toolbar.add_widget(self.badge_layout)
        toolbar.add_widget(cart_btn)

        # 搜索和筛选栏
        search_card = MDCard(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(70),
            padding=dp(10),
            spacing=dp(10),
            elevation=dp(2),
            radius=[dp(10)]
        )

        # 搜索框
        self.search_input = MDTextField(
            hint_text="搜索商品...",
            mode="rectangle",
            size_hint=(0.7, 1),
            icon_left="magnify"
        )
        self.search_input.font_name_hint_text = CHINESE_FONT_NAME
        self.search_input.font_name = CHINESE_FONT_NAME

        # 分类筛选
        self.category_filter_btn = MDRaisedButton(
            text="选择分类",
            size_hint=(0.3, 1),
            md_bg_color=(0.2, 0.6, 0.2, 1)
        )
        self.category_filter_btn.bind(on_release=self.show_category_menu)

        search_card.add_widget(self.search_input)
        search_card.add_widget(self.category_filter_btn)

        # # 搜索栏
        # search_layout = MDBoxLayout(
        #     orientation='horizontal',
        #     size_hint=(1, None),
        #     height=dp(60),
        #     padding=dp(10),
        #     spacing=dp(10)
        # )
        #
        # self.search_input = MDTextField(
        #     hint_text="搜索商品...",
        #     mode="rectangle",
        #     size_hint=(0.8, 1)
        # )
        # self.search_input.font_name_hint_text = CHINESE_FONT_NAME
        # self.search_input.font_name = CHINESE_FONT_NAME
        #
        # search_btn = MDRaisedButton(
        #     text="搜索",
        #     size_hint=(0.2, 1),
        #     md_bg_color=(0.6, 0.4, 0.6, 1)
        # )
        # search_btn.bind(on_release=self.search_products)
        #
        # search_layout.add_widget(self.search_input)
        # search_layout.add_widget(search_btn)

        # 分类标签
        # categories = [
        #     ("全部", None),
        #     ("家居", ProductCategory.HOME),
        #     # ("个护", ProductCategory.CARE),
        #     # ("服装", ProductCategory.CLOTHING),
        #     # ("热门", ProductCategory.FEATURED),
        #     ("清洁", ProductCategory.CLEAN),
        #     ("文具", ProductCategory.STATIONERY),
        #     ("电子产品", ProductCategory.ELECTRONICS)
        # ]
        # tabs1 = ProductTabs(categories[:])
        # tabs2 = ProductTabs(categories[4:])

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
        main_layout.add_widget(search_card)
        # main_layout.add_widget(tabs1)
        # main_layout.add_widget(tabs2)
        main_layout.add_widget(self.product_scroll)

        self.add_widget(main_layout)

    def on_enter(self):
        """进入屏幕时加载商品"""
        self.category_filter_btn.text = "选择分类"  # 默认显示
        self.load_products()

    def load_products(self, category=None, featured=False):
        """加载商品"""
        from kivy.app import App
        app = App.get_running_app()

        # 清空现有商品
        self.product_grid.clear_widgets()
        # 更新购物车徽章显示
        self.update_badge_color_text(app.cart.item_count)

        # 获取商品列表
        products = app.db.get_products(category=category, featured=featured)

        # 应用搜索筛选
        search_text = self.search_input.text.strip().lower()
        if search_text:
            products = [p for p in products if search_text in p.name.lower() or search_text in p.description.lower()]

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

    def show_category_menu(self, *args):
        """获取分类菜单"""
        from kivy.app import App
        app = App.get_running_app()

        categories = app.inventory_manager.get_categories()

        menu_items = [
            {
                "text": "全部分类",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="全部": self.filter_by_category(x)
            },
            {
                "text": "热门分类",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="热门": self.filter_by_category(x)
            }
        ]

        for category in categories:
            menu_items.append({
                "text": category.name,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=category.name: self.filter_by_category(x)
            })

        if self.category_filter_btn:
            self.category_menu = MDDropdownMenu(
                caller=self.category_filter_btn,
                items=menu_items,
                width_mult=dp(4),
                hor_growth="left",  # 水平向左扩展
            )
            self.category_menu.open()

    def filter_by_category(self, category_name):
        """按分类筛选"""
        self.category_filter_btn.text = category_name  # 按钮显示分类名称

        # 重新加载商品
        if category_name == "全部":
            self.load_products()
        else:
            self.load_products(category_name, category_name == "热门")

        if self.category_menu:
            self.category_menu.dismiss()

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

    def update_badge_color_text(self, val):
        if val > 0:
            self.badge_label.text = str(val)
            self.badge_label.text_color = (0.8, 0.2, 0.1, 1)
        else:
            self.badge_label.text = ''

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

    def __init__(self, categories: list, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (1, None)
        self.height = dp(50)
        self.spacing = dp(10)
        self.padding = dp(10)

        self._create_tabs(categories)

    def _create_tabs(self, categories):
        """创建分类标签"""
        for i, (name, category) in enumerate(categories):
            btn = MDRaisedButton(
                text=name,
                size_hint=(1 / len(categories), 1),
                md_bg_color=(0.1, 0.5, 0.2, 0.8) if i > 0 else (0.2, 0.2, 0.6, 0.8)
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
