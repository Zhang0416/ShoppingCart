from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import MDSnackbar
from kivy.metrics import sp

from screens.assets.config_chinese import register_chinese_font, set_kivymd_global_font
from screens.components.models import ShoppingCart, OrderManager, InventoryManager, Database
from screens.login_screen import LoginScreen, UserManager
from screens.home_screen import HomeScreen
from screens.product_screen import ProductScreen
from screens.cart_screen import CartScreen
from screens.checkout_screen import CheckoutScreen
from screens.profile_screen import ProfileScreen
from screens.orders_screen import OrdersScreen
from screens.inventory_screen import InventoryScreen

from kivy.config import Config
Config.set('input', 'keyboard_mode', 'system')


class ShoppingCartApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        self.cart = ShoppingCart()
        self.order_manager = OrderManager()
        self.inventory_manager = InventoryManager(self.db)
        self.screen_manager = None
        # 用户管理器
        self.user_manager = UserManager()
        self.user_info = None
        self.current_user = None

    def build(self):
        """构建应用"""
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Orange"

        # 1. 注册中文字体（全局仅需调用一次）
        register_chinese_font()

        # 2. 设置KivyMD全局字体（所有控件自动使用中文字体）
        set_kivymd_global_font(self.theme_cls)

        # 3. 创建屏幕管理器, 添加各个页面
        self.screen_manager = ScreenManager(size=(sp(450), sp(800)))
        self.screen_manager.add_widget(LoginScreen())
        self.screen_manager.add_widget(HomeScreen())
        self.screen_manager.add_widget(ProductScreen())
        self.screen_manager.add_widget(CartScreen())
        self.screen_manager.add_widget(CheckoutScreen())
        self.screen_manager.add_widget(ProfileScreen())
        self.screen_manager.add_widget(OrdersScreen())
        self.screen_manager.add_widget(InventoryScreen())

        return self.screen_manager

    def show_login(self):
        """显示登录界面"""
        self.screen_manager.current = "login"

    def show_home(self):
        """显示主页"""
        self.screen_manager.current = "home"

    def show_products(self):
        """显示商品界面"""
        self.screen_manager.current = "products"

    def show_cart(self):
        """显示购物车界面"""
        self.screen_manager.current = "cart"

    def show_checkout(self):
        """显示结算界面"""
        self.screen_manager.current = "checkout"

    def show_profile(self):
        """显示个人中心"""
        self.screen_manager.current = "profile"

    def show_orders(self):
        """显示订单管理"""
        self.screen_manager.current = "orders"

    def show_inventory(self):
        """显示库存管理"""
        self.screen_manager.current = "inventory"

    def add_to_cart(self, product_id):
        """添加商品到购物车"""
        product = self.db.get_product(product_id)
        if product:
            if product.stock <= 0:
                MDSnackbar(
                    MDLabel(text="商品库存不足", text_color=(0.9, 0.2, 0.2, 1))
                ).open()
                return False

            self.cart.add_item(product, 1)
            # 更新购物车界面
            cart_screen = self.screen_manager.get_screen("cart")
            cart_screen.update_cart()

            # 显示成功消息
            MDSnackbar(
                MDLabel(text=f"已添加 {product.name} 到购物车",
                        theme_text_color="Custom",
                        text_color=(0.2, 0.8, 0.2, 1)),
                duration=2,
            ).open()
            return True
        return False

    def update_cart_item(self, product_id, quantity):
        """更新购物车商品数量"""
        product = self.db.get_product(product_id)
        if product and quantity > product.stock:
            MDSnackbar(
                MDLabel(text=f"库存不足，最多可购买 {product.stock} 件", text_color=(0.9, 0.2, 0.2, 1))
            ).open()
            return

        self.cart.update_quantity(product_id, quantity)
        cart_screen = self.screen_manager.get_screen("cart")
        cart_screen.update_cart()

    def remove_from_cart(self, product_id):
        """从购物车移除商品"""
        self.cart.remove_item(product_id)
        cart_screen = self.screen_manager.get_screen("cart")
        cart_screen.update_cart()

    def complete_order(self, order_data):
        """完成订单"""
        from screens.components.models import Order

        # 创建订单对象
        order = Order(
            order_id=order_data['order_id'],
            user_name=self.current_user['name'],
            user_phone=self.current_user['phone'],
            items=order_data['items'],
            subtotal=order_data['subtotal'],
            discount=order_data['discount'],
            total=order_data['total'],
            address=order_data['address'],
            payment_method=order_data['payment_method'],
            status="delivered",  # 待付款状态，已完成状态，后续根须需求更改
            created_at=order_data['order_time']
        )

        # 添加到订单管理器
        self.order_manager.add_order(order)

        # 更新商品库存
        for item in order_data['items']:
            product = self.db.get_product(item['product_id'])
            if product:
                # 扣减库存
                new_stock = product.stock - item['quantity']
                if new_stock < 0:
                    new_stock = 0
                """ 库存管理, 不更新库存量 """
                self.inventory_manager.update_product_stock(product.id, new_stock)

        # 清空购物车
        self.cart.clear()

        return order

    def on_start(self):
        """应用启动时执行"""
        # 设置初始屏幕
        self.show_login()
