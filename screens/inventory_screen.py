from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import MDList, TwoLineListItem, TwoLineAvatarIconListItem, IconRightWidget
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.tab import MDTabsBase, MDTabs
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.chip import MDChip
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.snackbar import MDSnackbar
from kivy.metrics import dp, sp
import json

from .components.models import ProductCategory
from .assets.config_chinese import CHINESE_FONT_NAME


class StatsTab(MDFloatLayout, MDTabsBase):
    """统计概览标签页"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))

        # 统计卡片
        stats_card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(200),
            padding=dp(20),
            spacing=dp(10),
            elevation=dp(4),
            radius=[dp(15)]
        )

        stats_card.add_widget(MDLabel(
            text="库存统计",
            theme_text_color="Primary",
            font_style="H5"
        ))

        # 统计信息布局
        stats_grid = MDBoxLayout(orientation='vertical', spacing=dp(10))

        # 商品总数
        total_products_card = MDCard(
            orientation='horizontal',
            # size_hint=(0.3, 1),
            # padding=dp(20),
            # spacing=dp(10),
            elevation=dp(2),
            radius=[dp(10)],
            md_bg_color=(0.2, 0.6, 0.86, 0.2)
        )
        total_products_card.add_widget(MDLabel(
            text="商品总数",
            theme_text_color="Secondary",
            halign="center"
        ))
        self.total_products_label = MDLabel(
            text="0",
            theme_text_color="Primary",
            font_style="H6",
            halign="center"
        )
        total_products_card.add_widget(self.total_products_label)

        # 库存总量
        total_stock_card = MDCard(
            orientation='horizontal',
            # size_hint=(0.3, 1),
            # padding=dp(20),
            # spacing=dp(10),
            elevation=dp(2),
            radius=[dp(10)],
            md_bg_color=(0.2, 0.8, 0.4, 0.2)
        )

        total_stock_card.add_widget(MDLabel(
            text="库存总量",
            theme_text_color="Secondary",
            halign="center"
        ))
        self.total_stock_label = MDLabel(
            text="0",
            theme_text_color="Primary",
            font_style="H6",
            halign="center"
        )
        total_stock_card.add_widget(self.total_stock_label)

        # 商品总价值
        total_value_card = MDCard(
            orientation='horizontal',
            # size_hint=(0.3, 1),
            # padding=dp(20),
            # spacing=dp(10),
            elevation=dp(2),
            radius=[dp(10)],
            md_bg_color=(0.9, 0.6, 0.2, 0.2)
        )
        total_value_card.add_widget(MDLabel(
            text="商品总价值",
            theme_text_color="Secondary",
            halign="center"
        ))
        self.total_value_label = MDLabel(
            text="¥0",
            theme_text_color="Primary",
            font_style="H6",
            halign="center"
        )
        total_value_card.add_widget(self.total_value_label)

        stats_grid.add_widget(total_products_card)
        stats_grid.add_widget(total_stock_card)
        stats_grid.add_widget(total_value_card)

        stats_card.add_widget(stats_grid)

        # 快速操作
        quick_actions_card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(120),
            padding=dp(20),
            spacing=dp(10),
            elevation=dp(2),
            radius=[dp(15)]
        )

        quick_actions_card.add_widget(MDLabel(
            text="快速操作",
            theme_text_color="Primary",
            font_style="H5"
        ))

        actions_layout = MDBoxLayout(orientation='horizontal', spacing=10)

        add_product_btn = MDRaisedButton(
            text="添加商品",
            size_hint=(0.5, 1),
            md_bg_color=(0.2, 0.6, 0.86, 1)
        )
        add_product_btn.bind(on_release=self.add_product_callback)

        add_category_btn = MDRaisedButton(
            text="添加分类",
            size_hint=(0.5, 1),
            md_bg_color=(0.2, 0.8, 0.4, 1)
        )
        add_category_btn.bind(on_release=self.add_category_callback)

        actions_layout.add_widget(add_product_btn)
        actions_layout.add_widget(add_category_btn)

        quick_actions_card.add_widget(actions_layout)

        layout.add_widget(stats_card)
        layout.add_widget(quick_actions_card)
        layout.add_widget(MDBoxLayout())  # 占位空间

        self.add_widget(layout)

    def add_product_callback(self, *args):
        """添加商品回调"""
        from kivy.app import App
        app = App.get_running_app()
        inventory_screen = app.root.get_screen("inventory")
        if inventory_screen:
            inventory_screen.show_add_product_dialog()

    def add_category_callback(self, *args):
        """添加分类回调"""
        from kivy.app import App
        app = App.get_running_app()
        inventory_screen = app.root.get_screen("inventory")
        if inventory_screen:
            inventory_screen.show_add_category_dialog()

    def update_stats(self, products):
        """更新统计信息"""
        total_products = len(products)
        total_stock = sum(p.stock for p in products)
        total_value = sum(p.price * p.stock for p in products)

        self.total_products_label.text = str(total_products)
        self.total_stock_label.text = str(total_stock)
        self.total_value_label.text = f"¥{total_value:.1f}"


class ProductsTab(MDFloatLayout, MDTabsBase):
    """商品管理标签页"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical')

        # 搜索和筛选栏
        filter_card = MDCard(
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
            size_hint=(0.6, 1),
            icon_left="magnify"
        )
        self.search_input.font_name_hint_text = CHINESE_FONT_NAME
        self.search_input.font_name = CHINESE_FONT_NAME

        # 分类筛选
        self.category_filter_btn = MDRaisedButton(
            text="全部分类",
            size_hint=(0.4, 1)
        )
        self.category_filter_btn.bind(on_release=self.show_category_menu)

        filter_card.add_widget(self.search_input)
        filter_card.add_widget(self.category_filter_btn)

        # 商品列表
        self.product_scroll = MDScrollView()
        self.product_list = MDList()
        self.product_scroll.add_widget(self.product_list)

        layout.add_widget(filter_card)
        layout.add_widget(self.product_scroll)

        self.add_widget(layout)

    def show_category_menu(self, *args):
        """显示分类菜单"""
        from kivy.app import App
        app = App.get_running_app()
        inventory_screen = app.root.get_screen("inventory")
        if inventory_screen and inventory_screen.category_menu:
            inventory_screen.category_menu.open()

    def load_products(self, products, category_filter=None):
        """加载商品"""
        self.product_list.clear_widgets()

        # 应用分类筛选
        if category_filter and category_filter != "全部":
            products = [p for p in products if p.category.value == category_filter]

        # 应用搜索筛选
        search_text = self.search_input.text.strip().lower()
        if search_text:
            products = [p for p in products if search_text in p.name.lower() or search_text in p.description.lower()]

        if not products:
            empty_label = MDLabel(
                text="暂无商品",
                halign="center",
                theme_text_color="Hint",
                font_style="H5"
            )
            self.product_list.add_widget(empty_label)
            return

        for product in products:
            # 创建商品卡片
            product_card = MDCard(
                orientation='vertical',
                size_hint=(1, None),
                height=dp(180),
                padding=dp(15),
                spacing=dp(10),
                elevation=dp(2),
                radius=[dp(15)],
                ripple_behavior=True
            )

            # 商品信息
            info_layout = MDBoxLayout(
                orientation='vertical',
                size_hint=(1, 0.7)
            )

            # 名称和价格
            name_price_layout = MDBoxLayout(
                orientation='horizontal',
                size_hint=(1, None),
                height=dp(30)
            )

            name_label = MDLabel(
                text=product.name,
                theme_text_color="Primary",
                font_style="Headline6",
                size_hint=(0.7, 1)
            )

            price_label = MDLabel(
                text=f"¥{product.price:.1f}",
                theme_text_color="Error",
                size_hint=(0.3, 1),
                halign="right"
            )

            name_price_layout.add_widget(name_label)
            name_price_layout.add_widget(price_label)

            # 分类和库存
            category_stock_layout = MDBoxLayout(
                orientation='horizontal',
                size_hint=(1, None),
                height=dp(25)
            )

            # 分类标签
            # category_chip = MDChip(
            #     text=product.category,
            #     size_hint=(None, None),
            #     size=(100, 25)
            # )
            category_label = MDLabel(
                text=product.category,
                theme_text_color="Secondary",
                size_hint=(0.5, 1),
                halign="left"
            )

            stock_label = MDLabel(
                text=f"库存：{product.stock}",
                theme_text_color="Secondary",
                size_hint=(0.5, 1),
                halign="right"
            )

            category_stock_layout.add_widget(category_label)
            category_stock_layout.add_widget(stock_label)

            # 描述
            desc_label = MDLabel(
                text=product.description[:50] + "..." if len(product.description) > 50 else product.description,
                theme_text_color="Hint",
                font_style="Caption",
                size_hint_y=None,
                height=dp(40)
            )

            info_layout.add_widget(name_price_layout)
            info_layout.add_widget(category_stock_layout)
            info_layout.add_widget(desc_label)

            # 操作按钮
            actions_layout = MDBoxLayout(
                orientation='horizontal',
                size_hint=(1, None),
                height=dp(40),
                spacing=dp(10)
            )

            # 调整库存按钮
            adjust_btn = MDFlatButton(
                text="调整库存",
                size_hint=(0.33, 1)
            )
            adjust_btn.bind(on_release=lambda x, p=product: self.adjust_stock(p))

            # 编辑按钮
            edit_btn = MDFlatButton(
                text="编辑",
                size_hint=(0.33, 1)
            )
            edit_btn.bind(on_release=lambda x, p=product: self.edit_product(p))

            # 删除按钮
            delete_btn = MDFlatButton(
                text="删除",
                theme_text_color="Error",
                size_hint=(0.33, 1)
            )
            delete_btn.bind(on_release=lambda x, p=product: self.delete_product(p))

            actions_layout.add_widget(adjust_btn)
            actions_layout.add_widget(edit_btn)
            actions_layout.add_widget(delete_btn)

            product_card.add_widget(info_layout)
            product_card.add_widget(actions_layout)

            self.product_list.add_widget(product_card)

    def adjust_stock(self, product):
        """调整库存"""
        from kivy.app import App
        app = App.get_running_app()
        inventory_screen = app.root.get_screen("inventory")
        if inventory_screen:
            inventory_screen.adjust_stock(product)

    def edit_product(self, product):
        """编辑商品"""
        # MDSnackbar(MDLabel(text="编辑功能开发中", text_color=(0.2, 0.6, 0.86, 1))).open()
        from kivy.app import App
        app = App.get_running_app()
        inventory_screen = app.root.get_screen("inventory")
        if inventory_screen:
            inventory_screen.show_ecit_product_info_dialog(product)
    def delete_product(self, product):
        """删除商品"""
        from kivy.app import App
        app = App.get_running_app()
        inventory_screen = app.root.get_screen("inventory")
        if inventory_screen:
            inventory_screen.delete_product(product)


class CategoriesTab(MDFloatLayout, MDTabsBase):
    """分类管理标签页"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical')

        # 分类列表标题
        header_card = MDCard(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(60),
            padding=dp(20),
            spacing=dp(10),
            elevation=dp(2),
            radius=[dp(10)]
        )

        header_card.add_widget(MDLabel(
            text="商品分类",
            theme_text_color="Primary",
            font_style="H5",
            size_hint=(0.7, 1)
        ))

        add_btn = MDIconButton(
            icon="plus",
            theme_text_color="Primary",
            size_hint=(None, None),
            size=(sp(40), sp(40))
        )
        add_btn.bind(on_release=self.add_category_callback)

        header_card.add_widget(add_btn)

        # 分类列表
        self.category_scroll = MDScrollView()
        self.category_list = MDList()
        self.category_scroll.add_widget(self.category_list)

        layout.add_widget(header_card)
        layout.add_widget(self.category_scroll)

        self.add_widget(layout)

    def add_category_callback(self, *args):
        """添加分类回调"""
        from kivy.app import App
        app = App.get_running_app()
        inventory_screen = app.root.get_screen("inventory")
        if inventory_screen:
            inventory_screen.show_add_category_dialog()

    def load_categories(self, categories, products):
        """加载分类"""
        self.category_list.clear_widgets()

        if not categories:
            empty_label = MDLabel(
                text="暂无分类",
                halign="center",
                theme_text_color="Hint",
                font_style="H5"
            )
            self.category_list.add_widget(empty_label)
            return

        for category in categories:
            # 统计该分类下的商品数量
            category_products = [p for p in products if p.category == category.name]

            item = TwoLineAvatarIconListItem(
                text=category.name,
                secondary_text=f"{len(category_products)} 个商品",
                _txt_left_pad=dp(20)
            )

            # 添加操作按钮
            item_layout = MDBoxLayout(
                orientation='horizontal',
                adaptive_height=True,
                size_hint=(None, None),
                size=(sp(120), sp(40)),
                spacing=dp(5)
            )

            edit_btn = MDIconButton(
                icon="pencil",
                size_hint=(None, None),
                size=(sp(40), sp(40)),
                theme_text_color="Hint"
            )
            edit_btn.bind(on_release=lambda x, cat=category: self.edit_category(cat))

            delete_btn = MDIconButton(
                icon="delete",
                size_hint=(None, None),
                size=(sp(40), sp(40)),
                theme_text_color="Error"
            )
            delete_btn.bind(on_release=lambda x, cat=category: self.delete_category(cat))

            item_layout.add_widget(edit_btn)
            item_layout.add_widget(delete_btn)
            right_ = IconRightWidget(icon="", )
            right_.add_widget(item_layout)

            # item.add_widget(item_layout)
            item.add_widget(right_)
            self.category_list.add_widget(item)

    def edit_category(self, category):
        """编辑分类"""
        from kivy.app import App
        app = App.get_running_app()
        inventory_screen = app.root.get_screen("inventory")
        if inventory_screen:
            inventory_screen.edit_category(category)

    def delete_category(self, category):
        """删除分类"""
        from kivy.app import App
        app = App.get_running_app()
        inventory_screen = app.root.get_screen("inventory")
        if inventory_screen:
            inventory_screen.delete_category(category)


class InventoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "inventory"
        self._build_ui()
        # self.category_menu = None
        # self.stats_tab = None
        # self.products_tab = None
        # self.categories_tab = None

    def _build_ui(self):
        # 主布局
        main_layout = MDBoxLayout(orientation='vertical')

        # 顶部工具栏
        self.toolbar = MDTopAppBar(
            title="库存管理",
            elevation=dp(4),
            md_bg_color=(0.2, 0.6, 0.86, 1),
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[
                ["plus", lambda x: self.show_add_dialog()],
                ["refresh", lambda x: self.refresh_inventory()]
            ]
        )

        # 创建标签页容器
        self.tabs = MDTabs()
        self.tabs.font_name = CHINESE_FONT_NAME

        # 创建三个标签页
        self.stats_tab = StatsTab(title="统计概览")
        self.products_tab = ProductsTab(title="商品管理")
        self.categories_tab = CategoriesTab(title="分类管理")

        # 添加标签页到MDTabs
        self.tabs.add_widget(self.stats_tab)
        self.tabs.add_widget(self.products_tab)
        self.tabs.add_widget(self.categories_tab)

        main_layout.add_widget(self.toolbar)
        main_layout.add_widget(self.tabs)

        self.add_widget(main_layout)

    def on_enter(self):
        """进入页面时加载数据"""
        self.refresh_inventory()

    def refresh_inventory(self):
        """刷新库存数据"""
        from kivy.app import App
        app = App.get_running_app()

        # 获取数据
        products = app.inventory_manager.get_all_products()
        categories = app.inventory_manager.get_categories()

        # 更新统计标签页
        if self.stats_tab:
            self.stats_tab.update_stats(products)

        # 更新商品管理标签页
        if self.products_tab:
            self.products_tab.load_products(products)

        # 更新分类管理标签页
        if self.categories_tab:
            self.categories_tab.load_categories(categories, products)

        # 设置分类菜单
        self.setup_category_menu()
        MDSnackbar(MDLabel(text="库存数据已刷新", text_color=(0.2, 0.8, 0.2, 1))).open()

    def setup_category_menu(self):
        """设置分类菜单"""
        from kivy.app import App
        app = App.get_running_app()

        categories = app.inventory_manager.get_categories()

        menu_items = [
            {
                "text": "全部分类",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="全部": self.filter_by_category(x)
            }
        ]

        for category in categories:
            menu_items.append({
                "text": category.name,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=category.name: self.filter_by_category(x)
            })

        if self.products_tab and self.products_tab.category_filter_btn:
            self.category_menu = MDDropdownMenu(
                caller=self.products_tab.category_filter_btn,
                items=menu_items,
                width_mult=dp(4)
            )

    def filter_by_category(self, category_name):
        """按分类筛选"""
        if self.products_tab:
            self.products_tab.category_filter_btn.text = category_name

        # 重新加载商品
        from kivy.app import App
        app = App.get_running_app()
        products = app.inventory_manager.get_all_products()

        if self.products_tab:
            self.products_tab.load_products(products, category_filter=category_name)

        if self.category_menu:
            self.category_menu.dismiss()

    def show_add_dialog(self):
        """显示添加对话框（选择添加商品还是分类）"""
        dialog = MDDialog(
            title="添加内容",
            text="请选择要添加的内容类型：",
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="添加商品",
                    on_release=lambda x: self.show_add_product_dialog_after(dialog)
                ),
                MDRaisedButton(
                    text="添加分类",
                    on_release=lambda x: self.show_add_category_dialog_after(dialog)
                )
            ]
        )
        dialog.ids.title.font_name = CHINESE_FONT_NAME
        dialog.open()

    def show_add_product_dialog_after(self, dialog):
        """在关闭添加选择对话框后显示添加商品对话框"""
        dialog.dismiss()
        self.show_add_product_dialog()

    def show_add_category_dialog_after(self, dialog):
        """在关闭添加选择对话框后显示添加分类对话框"""
        dialog.dismiss()
        self.show_add_category_dialog()

    def show_add_product_dialog(self, *args):
        """显示添加商品对话框"""
        dialog = MDDialog(
            title="添加商品",
            type="custom",
            size_hint_x=None,
            width=dp(360),
            content_cls=MDBoxLayout(
                orientation='vertical',
                spacing=dp(0),
                size_hint_y=None,
                height=dp(500)
            ),
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="添加",
                    on_release=lambda x: self.add_product(dialog)
                )
            ]
        )
        dialog.ids.title.font_name = CHINESE_FONT_NAME

        scroll_view = MDScrollView()
        recent_list = MDList()

        # 商品名
        self.product_input = dict()
        self.product_input['name'] = MDTextField(hint_text="商品名称", mode="rectangle")
        self.product_input['name'].font_name_hint_text = CHINESE_FONT_NAME
        self.product_input['name'].font_name = CHINESE_FONT_NAME

        # 商品描述
        self.product_input['desc'] = MDTextField(hint_text="商品描述", mode="rectangle", multiline=True)
        self.product_input['desc'].font_name_hint_text = CHINESE_FONT_NAME
        self.product_input['desc'].font_name = CHINESE_FONT_NAME

        # 计量单位
        self.product_input['unit'] = MDTextField(hint_text="计量单位", mode="rectangle", multiline=True)
        self.product_input['unit'].font_name_hint_text = CHINESE_FONT_NAME
        self.product_input['unit'].font_name = CHINESE_FONT_NAME

        # 库存
        self.product_input['stock'] = MDTextField(
            hint_text="新增数量",
            mode="rectangle",
            input_filter="int",
            text="10"
        )
        self.product_input['stock'].font_name_hint_text = CHINESE_FONT_NAME
        self.product_input['stock'].font_name = CHINESE_FONT_NAME

        # unit_stock_layout = MDBoxLayout(
        #     orientation='horizontal',
        #     spacing=dp(5),
        #     size_hint_y=None,
        #     # height=dp(30)
        # )
        # unit_stock_layout.add_widget(self.product_input['unit'])
        # unit_stock_layout.add_widget(self.product_input['stock'])

        # 价格
        self.product_input['price'] = MDTextField(
            hint_text="价格",
            mode="rectangle",
            input_filter="float"
        )
        self.product_input['price'].font_name_hint_text = CHINESE_FONT_NAME
        self.product_input['price'].font_name = CHINESE_FONT_NAME

        self.product_input['suggest'] = MDTextField(
            hint_text="建议零售价格",
            mode="rectangle",
            input_filter="float"
        )
        self.product_input['suggest'].font_name_hint_text = CHINESE_FONT_NAME
        self.product_input['suggest'].font_name = CHINESE_FONT_NAME

        # price_suggest_layout = MDBoxLayout(
        #     orientation='horizontal',
        #     spacing=dp(10),
        #     size_hint_y=None,
        #     # height=dp(30)
        # )
        # price_suggest_layout.add_widget(self.product_input['price'])
        # price_suggest_layout.add_widget(self.product_input['suggest'])

        # 选择分类卡片
        self.product_input['category'] = MDCard(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(60),
            padding=dp(10),
            spacing=dp(20),
            elevation=dp(2),
            radius=[dp(10)]
        )
        self.product_input['cate_label'] = MDLabel(
            text="选择分类",
            theme_text_color="Hint",
            font_style="Subtitle2",
            height=dp(40),
        )
        self.product_input['cate_btn'] = MDRaisedButton(
            text="点击选择",
            size_hint=(None, None),
            size=(sp(100), sp(10)),
            on_release=self.open_category_menu
        )

        self.product_input['category'].add_widget(self.product_input['cate_label'])
        self.product_input['category'].add_widget(self.product_input['cate_btn'])

        # 是否推荐
        self.product_input['featured'] = MDCheckbox(
            size_hint=(None, None),
            size=(sp(40), sp(40))
        )

        featured_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(60)
        )
        featured_layout.add_widget(MDLabel(
            text="设为推荐商品",
            theme_text_color="Primary"
        ))
        featured_layout.add_widget(self.product_input['featured'])

        # 添加到对话框
        recent_list.add_widget(self.product_input['category'])
        recent_list.add_widget(self.product_input['name'])
        recent_list.add_widget(self.product_input['desc'])
        recent_list.add_widget(self.product_input['unit'])
        recent_list.add_widget(self.product_input['stock'])
        # recent_list.add_widget(unit_stock_layout)
        recent_list.add_widget(self.product_input['price'])
        recent_list.add_widget(self.product_input['suggest'])
        # recent_list.add_widget(price_suggest_layout)
        # recent_list.add_widget(featured_layout)
        scroll_view.add_widget(recent_list)

        dialog.content_cls.add_widget(scroll_view)
        dialog.open()

    def open_category_menu(self, *args):
        # 分类选择按钮
        from kivy.app import App
        app = App.get_running_app()
        categories = app.inventory_manager.get_categories()

        if categories:
            self.category_menu_for_product = MDDropdownMenu(
                caller=self.product_input['cate_btn'],
                items=[
                    {
                        "text": cat.name,
                        "viewclass": "OneLineListItem",
                        "height": dp(50),
                        "on_release": lambda x=cat.name: self.select_category_for_product(x),
                    } for cat in categories
                ],
                width_mult=1,
                # max_height=300,
                # position="center",
                hor_growth="right",  # 水平向右扩展（避免左侧裁剪）
            )
            self.category_menu_for_product.width = dp(500)
            self.category_menu_for_product.open()

    def select_category_for_product(self, category_name):
        """为商品选择分类"""
        self.product_input['cate_label'].text = category_name
        if self.category_menu_for_product:
            self.category_menu_for_product.dismiss()

    def add_product(self, dialog):
        """添加商品"""
        # 获取输入值
        name = self.product_input['name'].text.strip()
        description = self.product_input['desc'].text.strip()
        unit = self.product_input['unit'].text.strip()
        stock = self.product_input['stock'].text.strip()
        price = self.product_input['price'].text.strip()
        suggest = self.product_input['suggest'].text.strip()
        category_name = self.product_input['cate_label'].text.strip()

        # 验证输入
        errors = []
        if not name:
            errors.append("商品名称")
        if not description:
            errors.append("商品描述")
        if not unit:
            errors.append("计量单位")
        if not stock:
            errors.append("库存")
        if not price:
            errors.append("价格")
        if not suggest:
            errors.append("建议零售价")
        if not category_name:
            errors.append("分类")

        if errors:
            MDSnackbar(MDLabel(text=f"请填写: {', '.join(errors)}", text_color=(0.9, 0.2, 0.2, 1))).open()
            return

        try:
            price_val = float(price)
            suggest_val = float(suggest)
            stock_val = int(stock)

            if price_val <= 0:
                raise ValueError("价格必须大于0")
            if suggest_val < price_val:
                raise ValueError("建议零售价过低")
            if stock_val < 0:
                raise ValueError("库存不能为负数")
        except ValueError as e:
            MDSnackbar(MDLabel(text=f"输入错误: {str(e)}", text_color=(0.9, 0.2, 0.2, 1))).open()
            return

        # from kivy.app import App
        # app = App.get_running_app()
        #
        # # 检查分类是否存在
        # categories = app.inventory_manager.get_categories()
        # category_exists = any(cat.name == category_name for cat in categories)
        #
        # if not category_exists:
        #     MDSnackbar(MDLabel(text="请先创建该分类", text_color=(0.9, 0.2, 0.2, 1))).open()
        #     return

        # # 根据分类名称找到对应的枚举值
        # category_enum = None
        # for cat in ProductCategory:
        #     if cat.value == category_name:
        #         category_enum = cat
        #         break
        #
        # if not category_enum:
        #     # 如果没有找到对应的枚举，使用默认的电子产品分类
        #     category_enum = ProductCategory.HOME

        product_data = {
            'name': name,
            'price': price_val,
            'suggest': suggest,
            'stock': stock_val,
            'unit': unit,
            'category': category_name,
            'description': description,
            'is_featured': self.product_input['featured'].active,
            'images': ["./screens/assets/image/no_pic1.jpg"],
            'specifications': {}
        }

        from kivy.app import App
        app = App.get_running_app()
        new_product = app.inventory_manager.add_product(product_data)

        dialog.dismiss()

        # 刷新数据
        self.refresh_inventory()
        MDSnackbar(
            MDLabel(text=f"商品 '{name}' 添加成功", theme_text_color="Custom", text_color=(0.2, 0.8, 0.2, 1))
        ).open()

    def adjust_stock(self, product):
        """调整库存"""
        dialog = MDDialog(
            title="调整库存",
            type="custom",
            content_cls=MDBoxLayout(
                orientation='vertical',
                spacing=dp(15),
                size_hint_y=None,
                height=dp(200)
            ),
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="保存",
                    on_release=lambda x: self.save_stock_adjustment(dialog, product)
                )
            ]
        )
        dialog.ids.title.font_name = CHINESE_FONT_NAME

        # 当前库存信息
        info_label = MDLabel(
            text=f"商品: {product.name}\n当前库存: {product.stock}",
            theme_text_color="Primary"
        )

        # 库存调整输入
        self.stock_adjust_input = MDTextField(
            hint_text="输入新的库存数量",
            mode="rectangle",
            text=str(product.stock),
            input_filter="int"
        )
        self.stock_adjust_input.font_name_hint_text = CHINESE_FONT_NAME
        self.stock_adjust_input.font_name = CHINESE_FONT_NAME

        # 库存调整方式
        adjust_type_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(40),
            spacing=dp(10)
        )

        self.stock_adjust_type = "set"  # set: 设置, add: 增加, subtract: 减少

        set_btn = MDRaisedButton(
            text="设置",
            size_hint=(0.33, 1)
        )
        set_btn.bind(on_release=lambda x: self.set_adjust_type("set"))

        add_btn = MDFlatButton(
            text="增加",
            size_hint=(0.33, 1)
        )
        add_btn.bind(on_release=lambda x: self.set_adjust_type("add"))

        subtract_btn = MDFlatButton(
            text="减少",
            size_hint=(0.33, 1)
        )
        subtract_btn.bind(on_release=lambda x: self.set_adjust_type("subtract"))

        adjust_type_layout.add_widget(set_btn)
        adjust_type_layout.add_widget(add_btn)
        adjust_type_layout.add_widget(subtract_btn)

        dialog.content_cls.add_widget(info_label)
        dialog.content_cls.add_widget(self.stock_adjust_input)
        dialog.content_cls.add_widget(adjust_type_layout)

        dialog.open()

    def set_adjust_type(self, adjust_type):
        """设置库存调整类型"""
        self.stock_adjust_type = adjust_type

        # 更新按钮状态
        # 这里可以添加按钮状态更新逻辑

    def save_stock_adjustment(self, dialog, product):
        """保存库存调整"""
        try:
            input_val = int(self.stock_adjust_input.text)
        except ValueError:
            MDSnackbar(MDLabel(text="请输入有效的数字", text_color=(0.9, 0.2, 0.2, 1))).open()
            return

        from kivy.app import App
        app = App.get_running_app()

        new_stock = product.stock

        if self.stock_adjust_type == "set":
            new_stock = input_val
        elif self.stock_adjust_type == "add":
            new_stock = product.stock + input_val
        elif self.stock_adjust_type == "subtract":
            new_stock = product.stock - input_val

        if new_stock < 0:
            MDSnackbar(MDLabel(text="库存不能为负数", text_color=(0.9, 0.2, 0.2, 1))).open()
            return

        if app.inventory_manager.update_product_stock(product.id, new_stock):
            dialog.dismiss()

            # 刷新数据
            self.refresh_inventory()
            MDSnackbar(MDLabel(text="库存更新成功", text_color=(0.2, 0.8, 0.2, 1))).open()
        else:
            MDSnackbar(MDLabel(text="库存更新失败", text_color=(0.9, 0.2, 0.2, 1))).open()

    def show_ecit_product_info_dialog(self, product):
        dialog = MDDialog(
            title="编辑商品信息",
            type="custom",
            size_hint_x=None,
            width=dp(360),
            content_cls=MDBoxLayout(
                orientation='vertical',
                spacing=dp(0),
                size_hint_y=None,
                height=dp(500)
            ),
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="保存",
                    on_release=lambda x, p=product: self.save_edit_product_info(dialog, p)
                )
            ]
        )
        dialog.ids.title.font_name = CHINESE_FONT_NAME

        scroll_view = MDScrollView()
        mdtext_list = MDList()

        # 商品名
        self.product_edit_info = dict()
        self.product_edit_info['name'] = MDTextField(hint_text="商品名称", text=product.name, mode="rectangle")
        self.product_edit_info['name'].font_name_hint_text = CHINESE_FONT_NAME
        self.product_edit_info['name'].font_name = CHINESE_FONT_NAME

        # 商品描述
        self.product_edit_info['desc'] = MDTextField(hint_text="商品描述", text=product.description, mode="rectangle", multiline=True)
        self.product_edit_info['desc'].font_name_hint_text = CHINESE_FONT_NAME
        self.product_edit_info['desc'].font_name = CHINESE_FONT_NAME

        spec_str = "\n".join([f"{k}:{v}" for k, v in product.specifications.items()])
        self.product_edit_info['spec'] = MDTextField(hint_text="规格/配置/其他", text=spec_str, mode="rectangle", multiline=True)
        self.product_edit_info['spec'].font_name_hint_text = CHINESE_FONT_NAME
        self.product_edit_info['spec'].font_name = CHINESE_FONT_NAME

        # 计量单位
        self.product_edit_info['unit'] = MDTextField(hint_text="计量单位", text=product.unit, mode="rectangle", multiline=True)
        self.product_edit_info['unit'].font_name_hint_text = CHINESE_FONT_NAME
        self.product_edit_info['unit'].font_name = CHINESE_FONT_NAME

        # 价格
        self.product_edit_info['price'] = MDTextField(hint_text="价格", text=str(product.price), mode="rectangle", input_filter="float")
        self.product_edit_info['price'].font_name_hint_text = CHINESE_FONT_NAME
        self.product_edit_info['price'].font_name = CHINESE_FONT_NAME

        self.product_edit_info['suggest'] = MDTextField(hint_text="建议零售价格", text=str(product.suggest), mode="rectangle", input_filter="float")
        self.product_edit_info['suggest'].font_name_hint_text = CHINESE_FONT_NAME
        self.product_edit_info['suggest'].font_name = CHINESE_FONT_NAME

        mdtext_list.add_widget(self.product_edit_info['name'])
        mdtext_list.add_widget(self.product_edit_info['desc'])
        mdtext_list.add_widget(self.product_edit_info['spec'])
        mdtext_list.add_widget(self.product_edit_info['unit'])
        mdtext_list.add_widget(self.product_edit_info['price'])
        mdtext_list.add_widget(self.product_edit_info['suggest'])
        scroll_view.add_widget(mdtext_list)

        dialog.content_cls.add_widget(scroll_view)
        dialog.open()

    def save_edit_product_info(self, dialog, product):

        product.name = self.product_edit_info['name'].text.strip()
        product.description = self.product_edit_info['desc'].text.strip()
        product.unit = self.product_edit_info['unit'].text.strip()
        product.price = self.product_edit_info['price'].text.strip()
        product.suggest = self.product_edit_info['suggest'].text.strip()

        try:
            price_val = float(product.price)
            suggest_val = float(product.suggest)

            if price_val <= 0:
                raise ValueError("价格必须大于0")
            if suggest_val < price_val:
                raise ValueError("建议零售价过低")

        except ValueError as e:
            MDSnackbar(MDLabel(text=f"输入错误: {str(e)}", text_color=(0.9, 0.2, 0.2, 1))).open()
            return

        product.price = price_val
        product.suggest = suggest_val

        spec_str = self.product_edit_info['spec'].text.strip()
        product.specifications = dict()
        if len(spec_str):
            spec_dict = dict()
            for ss in spec_str.split('\n'):
                tmp = ss.split(':')
                if len(tmp) < 2:
                    MDSnackbar(MDLabel(text=f"{self.product_edit_info['spec'].hint_text}\n每行信息均要遵循‘特征:描述’的格式")).open()
                    return
                else:
                    product.specifications[tmp[0]] = ":".join(tmp[1:])

        from kivy.app import App
        app = App.get_running_app()

        if app.inventory_manager.update_product_info(product):
            dialog.dismiss()

            # 刷新数据
            self.refresh_inventory()
            MDSnackbar(MDLabel(text="库存更新成功", text_color=(0.2, 0.8, 0.2, 1))).open()
        else:
            MDSnackbar(MDLabel(text="库存更新失败", text_color=(0.9, 0.2, 0.2, 1))).open()


    def show_add_category_dialog(self, *args):
        """显示添加分类对话框"""
        dialog = MDDialog(
            title="添加分类",
            type="custom",
            content_cls=MDBoxLayout(
                orientation='vertical',
                spacing=dp(15),
                size_hint_y=None,
                height=dp(230)
            ),
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="添加",
                    on_release=lambda x: self.add_category(dialog)
                )
            ]
        )
        dialog.ids.title.font_name = CHINESE_FONT_NAME

        # 分类名称
        self.category_name_input = MDTextField(
            hint_text="分类名称",
            mode="rectangle"
        )
        self.category_name_input.font_name_hint_text = CHINESE_FONT_NAME
        self.category_name_input.font_name = CHINESE_FONT_NAME

        # 分类描述
        self.category_desc_input = MDTextField(
            hint_text="分类描述（可选）",
            mode="rectangle"
        )
        self.category_desc_input.font_name_hint_text = CHINESE_FONT_NAME
        self.category_desc_input.font_name = CHINESE_FONT_NAME

        # 分类图标
        self.category_icon_input = MDTextField(
            hint_text="图标名称（可选）",
            mode="rectangle"
        )
        self.category_icon_input.font_name_hint_text = CHINESE_FONT_NAME
        self.category_icon_input.font_name = CHINESE_FONT_NAME

        dialog.content_cls.add_widget(self.category_name_input)
        dialog.content_cls.add_widget(self.category_desc_input)
        dialog.content_cls.add_widget(self.category_icon_input)

        dialog.open()

    def add_category(self, dialog):
        """添加分类"""
        name = self.category_name_input.text.strip()
        description = self.category_desc_input.text.strip()
        icon = self.category_icon_input.text.strip()

        if not name:
            MDSnackbar(MDLabel(text="请输入分类名称", text_color=(0.9, 0.2, 0.2, 1))).open()
            return

        from kivy.app import App
        app = App.get_running_app()

        # 检查分类是否已存在
        categories = app.inventory_manager.get_categories()
        if any(cat.name == name for cat in categories):
            MDSnackbar(MDLabel(text="分类已存在", text_color=(0.9, 0.2, 0.2, 1))).open()
            return

        new_category = app.inventory_manager.add_category(name, icon, description)

        dialog.dismiss()

        # 刷新数据
        self.refresh_inventory()
        MDSnackbar(MDLabel(text=f"分类 '{name}' 添加成功", text_color=(0.2, 0.8, 0.2, 1))).open()

    def edit_category(self, category):
        """编辑分类"""
        dialog = MDDialog(
            title="编辑分类",
            type="custom",
            content_cls=MDBoxLayout(
                orientation='vertical',
                spacing=dp(15),
                size_hint_y=None,
                height=dp(200)
            ),
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="保存",
                    on_release=lambda x: self.save_category_edit(dialog, category)
                )
            ]
        )
        dialog.ids.title.font_name = CHINESE_FONT_NAME

        # 分类名称
        self.edit_category_name_input = MDTextField(
            hint_text="分类名称",
            text=category.name,
            mode="rectangle"
        )
        self.edit_category_name_input.font_name_hint_text = CHINESE_FONT_NAME
        self.edit_category_name_input.font_name = CHINESE_FONT_NAME

        # 分类描述
        self.edit_category_desc_input = MDTextField(
            hint_text="分类描述",
            text=category.description,
            mode="rectangle"
        )
        self.edit_category_desc_input.font_name_hint_text = CHINESE_FONT_NAME
        self.edit_category_desc_input.font_name = CHINESE_FONT_NAME

        # 分类图标
        self.edit_category_icon_input = MDTextField(
            hint_text="图标名称",
            text=category.icon,
            mode="rectangle"
        )
        self.edit_category_icon_input.font_name_hint_text = CHINESE_FONT_NAME
        self.edit_category_icon_input.font_name = CHINESE_FONT_NAME

        dialog.content_cls.add_widget(self.edit_category_name_input)
        dialog.content_cls.add_widget(self.edit_category_desc_input)
        dialog.content_cls.add_widget(self.edit_category_icon_input)

        dialog.open()

    def save_category_edit(self, dialog, category):
        """保存分类编辑"""
        # 注意：这里只是演示，实际应该更新分类信息
        # 由于我们的InventoryManager没有更新分类的方法，这里只是演示UI

        dialog.dismiss()

        MDSnackbar(MDLabel(text="编辑功能开发中", text_color=(0.2, 0.6, 0.86, 1))).open()

    def delete_product(self, product):
        """删除商品"""
        dialog = MDDialog(
            title="删除商品",
            text=f"确定要删除商品 '{product.name}' 吗？\n此操作不可撤销。",
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="删除",
                    md_bg_color=(0.9, 0.2, 0.2, 1),
                    on_release=lambda x: self.confirm_delete_product(dialog, product)
                )
            ]
        )
        dialog.ids.title.font_name = CHINESE_FONT_NAME
        dialog.open()

    def confirm_delete_product(self, dialog, product):
        """确认删除商品"""
        from kivy.app import App
        app = App.get_running_app()

        if app.inventory_manager.delete_product(product.id):
            dialog.dismiss()

            # 刷新数据
            self.refresh_inventory()
            MDSnackbar(MDLabel(text="商品删除成功", text_color=(0.2, 0.8, 0.2, 1))).open()
        else:
            MDSnackbar(MDLabel(text="商品删除失败", text_color=(0.9, 0.2, 0.2, 1))).open()

    def delete_category(self, category):
        """删除分类"""
        dialog = MDDialog(
            title="删除分类",
            text=f"确定要删除分类 '{category.name}' 吗？\n",
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="删除",
                    md_bg_color=(0.9, 0.2, 0.2, 1),
                    on_release=lambda x: self.confirm_delete_category(dialog, category)
                )
            ]
        )
        dialog.ids.title.font_name = CHINESE_FONT_NAME
        dialog.open()

    def confirm_delete_category(self, dialog, category):
        """确认删除分类"""
        # 注意：这里只是演示，实际应该删除分类
        # 由于我们的InventoryManager没有删除分类的方法，这里只是演示UI

        dialog.dismiss()
        # MDSnackbar(MDLabel(text="删除功能开发中", text_color=(0.2, 0.6, 0.86, 1))).open()

        from kivy.app import App
        app = App.get_running_app()

        app.inventory_manager.delete_category(category.name)
        app.inventory_manager.save_categories()

        # 刷新数据
        self.refresh_inventory()
        MDSnackbar(MDLabel(text=f"分类 '{category.name}' 删除成功", text_color=(0.2, 0.8, 0.2, 1)))

    def go_back(self):
        """返回主页"""
        from kivy.app import App
        app = App.get_running_app()
        app.show_orders()
