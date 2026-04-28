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
from kivy.clock import Clock
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics import Color, RoundedRectangle

from .assets.config_chinese import CHINESE_FONT_NAME
from .components.models import ProductCategory
from .components.product_card import ProductCard


class ProductScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "products"
        self._batch_event = None
        self._cached_products = None
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

        # 购物车按钮 + 徽章容器（RelativeLayout 实现徽章叠加在按钮右上角）
        cart_container = RelativeLayout(
            size_hint=(None, None),
            size=(dp(48), dp(48))
        )

        cart_btn = MDIconButton(
            icon="cart",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        cart_btn.bind(on_release=self.show_cart)

        # 徽章数字：红底白字、右上角、1位圆形/2位+圆角矩形
        self.badge_label = MDLabel(
            text='',
            halign="center",
            valign="middle",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),  # 白色文字
            bold=True,
            font_size=sp(11),
            size_hint=(None, None),
            size=(dp(20), dp(20)),
            pos_hint={"right": 0.95, "top": 0.95},
            opacity=0  # 默认隐藏
        )

        # 绘制红色背景（canvas.before 保证在文字下方）
        with self.badge_label.canvas.before:
            Color(0.9, 0.2, 0.1, 1)
            self.badge_bg = RoundedRectangle(
                pos=self.badge_label.pos,
                size=self.badge_label.size,
                radius=[dp(10)] * 4
            )
        self.badge_label.bind(pos=self._update_badge_bg, size=self._update_badge_bg)

        cart_container.add_widget(cart_btn)
        cart_container.add_widget(self.badge_label)

        toolbar.add_widget(back_btn)
        toolbar.add_widget(title)
        toolbar.add_widget(cart_container)

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
        # 清除缓存，从其他页面返回时数据可能已经变化
        self._cached_products = None
        # 延迟一帧加载，让页面框架先渲染，减少卡顿感
        Clock.schedule_once(lambda dt: self.load_products(), 0)

    def _load_products_batch(self, products):
        """分批添加商品卡片，避免一次性创建大量 widget 阻塞主线程"""
        # 取消之前的分批加载
        if self._batch_event:
            self._batch_event.cancel()
            self._batch_event = None

        self.product_grid.clear_widgets()

        if not products:
            return

        from kivy.app import App
        app = App.get_running_app()
        # Android 低端设备每帧少加载几个，PC 可以多加载
        from kivy.utils import platform
        batch_size = 3 if platform == 'android' else 6
        index = [0]

        def add_batch(dt):
            start = index[0]
            end = min(start + batch_size, len(products))
            for i in range(start, end):
                product = products[i]
                card = ProductCard(
                    product_id=product.id,
                    name=product.name,
                    description=product.description,
                    price=product.price,
                    image_url=app.resolve_image_path(product.images[0]) if product.images else "",
                    rating=product.rating,
                    stock=product.stock
                )
                self.product_grid.add_widget(card)
            index[0] = end
            if index[0] >= len(products):
                if self._batch_event:
                    self._batch_event.cancel()
                self._batch_event = None

        # 立即执行第一帧，然后每 0 秒（下一帧）继续
        self._batch_event = Clock.schedule_interval(add_batch, 0)

    def load_products(self, category=None, featured=False):
        """加载商品（支持缓存和分批加载）"""
        from kivy.app import App
        app = App.get_running_app()

        # 更新购物车徽章显示
        self.update_badge_color_text(app.cart.item_count)

        # 使用缓存避免重复读取 JSON
        if self._cached_products is None:
            self._cached_products = list(app.db.get_products())
        products = self._cached_products[:]

        # 应用分类筛选（与原 db.get_products 行为一致：
        # category 和 featured 独立处理，featured=True 时忽略 category 筛选）
        if category and category != "全部":
            products = [p for p in products if p.category == category]
        if featured:
            products = self._cached_products[:]
            products = [p for p in products if getattr(p, 'is_featured', False)]

        # 应用搜索筛选
        search_text = self.search_input.text.strip().lower()
        if search_text:
            products = [p for p in products if search_text in p.name.lower() or search_text in p.description.lower()]

        self._load_products_batch(products)

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

        # 更新购物车徽章显示
        self.update_badge_color_text(app.cart.item_count)

        # 使用缓存避免重复读取 JSON
        if self._cached_products is None:
            self._cached_products = list(app.db.get_products())
        products = self._cached_products[:]

        search_text = self.search_input.text.strip().lower()
        filtered_products = [
            p for p in products
            if search_text in str(p.name).lower() or search_text in str(p.category).lower()
        ]

        self._load_products_batch(filtered_products)

    def _update_badge_bg(self, instance, value):
        """同步更新徽章背景的位置和大小"""
        self.badge_bg.pos = instance.pos
        self.badge_bg.size = instance.size

    def update_badge_color_text(self, val):
        from kivy.core.text import Label as CoreLabel
        if val > 0:
            self.badge_label.text = str(val)
            self.badge_label.opacity = 1
            lbl = CoreLabel(text=str(val), font_size=sp(11), bold=True)
            lbl.refresh()
            tw = lbl.texture.size[0]
            if val < 10:
                # 1位数字：正圆形（宽=高）
                self.badge_label.size = (dp(20), dp(20))
            else:
                # 2位及以上：胶囊形圆角矩形
                self.badge_label.size = (max(dp(28), tw + dp(12)), dp(20))
        else:
            self.badge_label.text = ''
            self.badge_label.opacity = 0

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
