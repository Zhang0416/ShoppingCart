import json
import os
import uuid

from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict
from kivy.logger import Logger

import sys
from pathlib import Path

sys.path.append(str(Path(__file__)))


class ProductCategory(Enum):
    ELECTRONICS = "电子产品"
    FOOD = "食品饮料"
    BOOKS = "图书音像"
    HOME = "家居用品"
    CLOTHING = "服装服饰"
    SHOES = "鞋子"
    BEAUTY = "美妆"
    CARE = "个护"
    CLEAN = "清洁"
    STATIONERY = "文具"
    FEATURED = "热门"


@dataclass
class Product:
    """商品数据模型"""
    id: str
    name: str
    description: str
    price: float
    suggest: float
    category: ProductCategory
    stock: int
    unit: str
    images: List[str] = field(default_factory=list)
    specifications: Dict = field(default_factory=dict)
    rating: float = 0.0
    sales_count: int = 0
    is_featured: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        data = asdict(self)
        data['category'] = self.category.value if isinstance(self.category, ProductCategory) else str(self.category)
        return data

    @classmethod
    def from_dict(cls, data):
        data['category'] = ProductCategory(data['category'])
        return cls(**data)


@dataclass
class CartItem:
    """购物车项"""
    product_id: str
    product_name: str
    price: float
    quantity: int
    image: str = ""
    specifications: Dict = field(default_factory=dict)

    @property
    def subtotal(self):
        return self.price * self.quantity


class ShoppingCart:
    """购物车"""

    def __init__(self):
        self.items: Dict[str, CartItem] = {}
        self.coupon: Optional[Dict] = None

    def add_item(self, product: Product, quantity: int = 1, specifications=None):
        if product.id in self.items:
            self.items[product.id].quantity += quantity
        else:
            self.items[product.id] = CartItem(
                product_id=product.id,
                product_name=product.name,
                price=product.price,
                quantity=quantity,
                image=product.images[0] if product.images else "",
                specifications=specifications or {}
            )

    def remove_item(self, product_id: str):
        if product_id in self.items:
            del self.items[product_id]

    def update_quantity(self, product_id: str, quantity: int):
        if product_id in self.items:
            if quantity <= 0:
                self.remove_item(product_id)
            else:
                self.items[product_id].quantity = quantity

    def clear(self):
        self.items.clear()
        self.coupon = None

    def set_coupon(self, val):
        if self.coupon is None:
            self.coupon = {"value": val}
        elif isinstance(self.coupon, dict) and "value" in self.coupon.keys():
            self.coupon["value"] = val
        else:
            self.coupon = {"value": val}

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.values())

    @property
    def subtotal(self):
        return sum(item.subtotal for item in self.items.values())

    @property
    def discount(self):
        if self.coupon:
            # 简化折扣计算, 最低5折
            # return min(self.coupon.get('value', 0), self.subtotal * 0.5)
            return self.coupon.get('value', 0)
        return 0

    @property
    def total(self):
        return self.subtotal - self.discount

    def to_dict(self):
        return {
            'items': [asdict(item) for item in self.items.values()],
            'subtotal': self.subtotal,
            'discount': self.discount,
            'total': self.total,
            'item_count': self.item_count
        }


@dataclass
class Order:
    """订单模型"""
    order_id: str
    user_name: str
    user_phone: str
    items: List[Dict]
    subtotal: float
    discount: float
    total: float
    address: str
    payment_method: str
    status: str  # pending, paid, shipped, delivered, cancelled
    created_at: str
    updated_at: str = ""

    def to_dict(self):
        data = asdict(self)
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


@dataclass
class Category:
    """商品分类"""
    id: str
    name: str
    icon: str = ""
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        data = asdict(self)
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class OrderManager:
    """订单管理器"""

    def __init__(self, data_file: str = "/data/orders.json"):
        self.orders_file = str(Path(__file__).parent.parent.parent) + data_file
        self.orders = self.load_orders()

    def load_orders(self):
        """从文件加载订单"""
        if os.path.exists(self.orders_file):
            try:
                with open(self.orders_file, 'r', encoding='utf-8') as f:
                    orders_data = json.load(f)
                    return [Order.from_dict(order) for order in orders_data]
            except:
                return []
        return []

    def save_orders(self):
        """保存订单到文件"""
        try:
            with open(self.orders_file, 'w', encoding='utf-8') as f:
                orders_data = [order.to_dict() for order in self.orders]
                json.dump(orders_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            Logger.warning(f"保存订单失败: {e}")
            return False

    def add_order(self, order: Order):
        """添加订单"""
        self.orders.append(order)
        self.save_orders()

    def delete_order(self, order: Order):
        if order in self.orders:
            self.orders.remove(order)
            self.save_orders()
        return

    def get_orders_by_user(self, user_phone: str):
        """获取用户的订单"""
        return [order for order in self.orders if order.user_phone == user_phone]

    def get_all_orders(self):
        """获取所有订单"""
        return self.orders

    # def update_order_status(self, order_id: str, status: str):
    #     """更新订单状态"""
    #     for order in self.orders:
    #         if order.order_id == order_id:
    #             order.status = status
    #             order.updated_at = datetime.now().isoformat()
    #             self.save_orders()
    #             return True
    #     return False


class InventoryManager:
    """库存管理器"""

    def __init__(self, db, data_file: str = "/data/categories.json"):
        self.db = db
        self.categories_file = str(Path(__file__).parent.parent.parent) + data_file
        self.categories = self.load_categories()

    def load_categories(self):
        """加载分类"""
        if os.path.exists(self.categories_file):
            try:
                with open(self.categories_file, 'r', encoding='utf-8') as f:
                    categories_data = json.load(f)
                    return [Category.from_dict(cat) for cat in categories_data]
            except:
                # 默认分类
                return [
                    Category("electronics", "电子产品", "laptop"),
                    Category("clothing", "服装服饰", "tshirt-crew"),
                    Category("food", "食品饮料", "food"),
                    Category("books", "图书音像", "book"),
                    Category("home", "家居用品", "home"),
                    Category("beauty", "美妆个护", "face-woman")
                ]
        return []

    def save_categories(self):
        """保存分类"""
        try:
            with open(self.categories_file, 'w', encoding='utf-8') as f:
                categories_data = [cat.to_dict() for cat in self.categories]
                json.dump(categories_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            Logger.warning(f"保存分类失败: {e}")
            return False

    def get_categories(self):
        """获取所有分类"""
        return self.categories

    def get_category_by_id(self, category_id: str):
        """根据ID获取分类"""
        for cat in self.categories:
            if cat.id == category_id:
                return cat
        return None

    # 在 InventoryManager 类中添加以下方法

    def add_product(self, product_data: Dict):
        """添加商品"""
        import uuid
        from datetime import datetime

        # 生成唯一ID
        product_id = f"p{str(uuid.uuid4())[:8]}"

        # 创建商品
        # 这里需要将分类名称转换为 ProductCategory 枚举
        category_name = product_data['category']
        category_enum = None

        # 尝试找到对应的枚举
        for cat in ProductCategory:
            if cat.value == category_name:
                category_enum = cat
                break

        # 如果没有找到，使用默认分类
        if not category_enum:
            category_enum = ProductCategory.HOME

        new_product = Product(
            id=product_id,
            name=product_data['name'],
            description=product_data['description'],
            price=float(product_data['price']),
            suggest=float(product_data['suggest']),
            unit=product_data['unit'],
            category=category_enum,
            stock=int(product_data['stock']),
            images=product_data.get('images', []),
            specifications=product_data.get('specifications', {}),
            rating=0.0,
            sales_count=0,
            is_featured=product_data.get('is_featured', False),
            created_at=datetime.now().isoformat()
        )

        # 添加到数据库
        self.db.products[product_id] = new_product
        self.db.save_product_info()  # 保存
        return new_product

    def update_product_stock(self, product_id: str, new_stock: int):
        """更新商品库存"""
        if product_id in self.db.products:
            self.db.products[product_id].stock = new_stock
            self.db.save_product_info()  # 更新存储商品库存数量
            return True
        return False

    def update_product_info(self, product: Product):
        """更新商品信息"""
        if product.id in self.db.products:
            self.db.products[product.id] = product
            self.db.save_product_info()
            return True
        return False

    def delete_product(self, product_id: str):
        """删除商品"""
        if product_id in self.db.products:
            del self.db.products[product_id]
            self.db.save_product_info()  # 更新存储商品库存数量
            return True
        return False

    def add_category(self, name: str, icon: str = "", description: str = ""):
        """添加分类"""
        from datetime import datetime
        import uuid

        category_id = f"cat{str(uuid.uuid4())[:8]}"

        new_category = Category(
            id=category_id,
            name=name,
            icon=icon,
            description=description,
            created_at=datetime.now().isoformat()
        )

        self.categories.append(new_category)
        self.save_categories()
        return new_category

    def delete_category(self, name: str):
        for cat in self.categories:
            if name == cat.name:
                self.categories.remove(cat)
                break
        return

    def get_all_products(self):
        """获取所有商品"""
        return list(self.db.products.values())


class Database:
    """模拟数据库"""

    def __init__(self, data_file: str = "/data/products.json"):
        self.products_file = str(Path(__file__).parent.parent.parent) + data_file
        # self.products = self._create_sample_products()
        self.products = self.load_product_info()
        self.users = {}
        self.orders = []

    def _create_sample_products(self):
        """创建示例商品"""
        products = []

        sample_data = [
            {
                "id": "p001",
                "name": "iPhone 15 Pro",
                "description": "A17 Pro芯片，钛金属设计，超视网膜XDR显示屏",
                "price": 8999.0,
                "suggest": 8999.0,
                "category": "电子产品",
                "stock": 50,
                "unit": "台",
                "images": ["./assets/image/demo/iphone15pro.jpeg"],
                "rating": 4.8,
                "sales_count": 1200,
                "is_featured": True,
                "specifications": {
                    "颜色": ["深空黑", "银色", "金色"],
                    "存储": ["128GB", "256GB", "512GB", "1TB"]
                }
            },
            {
                "id": "p002",
                "name": "MacBook Air M2",
                "description": "13.6英寸Liquid视网膜显示屏，M2芯片",
                "price": 8499.0,
                "suggest": 8999.0,
                "category": "电子产品",
                "stock": 30,
                "unit": "台",
                "images": ["./assets/image/demo/macbookairm2.png"],
                "rating": 4.7,
                "sales_count": 850,
                "is_featured": True
            },
            {
                "id": "p003",
                "name": "男士休闲衬衫",
                "description": "纯棉材质，舒适透气，多色可选",
                "price": 299.0,
                "suggest": 299.0,
                "unit": "件",
                "category": "服装服饰",
                "stock": 100,
                "images": ["./assets/image/demo/tshirtman.jpeg"],
                "rating": 4.5,
                "sales_count": 3200,
                "specifications": {
                    "尺码": ["S", "M", "L", "XL", "XXL"],
                    "颜色": ["白色", "蓝色", "灰色", "黑色"]
                }
            },
            {
                "id": "p004",
                "name": "Java编程思想",
                "description": "Java编程经典书籍，第5版",
                "price": 89.0,
                "suggest": 99.0,
                "category": "图书音像",
                "stock": 200,
                "unit": "本",
                "images": ["https://via.placeholder.com/300x300/9b59b6/ffffff?text=书籍"],
                "rating": 4.9,
                "sales_count": 5600
            },
            {
                "id": "p005",
                "name": "巧克力礼盒",
                "description": "比利时进口巧克力，精美包装",
                "price": 199.0,
                "suggest": 199.0,
                "category": "食品饮料",
                "stock": 150,
                "unit": "盒",
                "images": ["https://via.placeholder.com/300x300/f39c12/ffffff?text=巧克力"],
                "rating": 4.6,
                "sales_count": 2100
            },
            {
                "id": "p006",
                "name": "智能手表",
                "description": "心率监测，GPS定位，50米防水",
                "price": 1299.0,
                "suggest": 1299.0,
                "category": "电子产品",
                "stock": 80,
                "unit": "个",
                "images": ["https://via.placeholder.com/300x300/1abc9c/ffffff?text=手表"],
                "rating": 4.4,
                "sales_count": 900
            },
            {
                "id": "p007",
                "name": "运动鞋",
                "description": "透气网面，减震鞋底，跑步健身",
                "price": 399.0,
                "suggest": 399.0,
                "category": "服装服饰",
                "stock": 120,
                "unit": "双",
                "images": ["https://via.placeholder.com/300x300/34495e/ffffff?text=运动鞋"],
                "rating": 4.7,
                "sales_count": 1800
            },
            {
                "id": "p008",
                "name": "无线耳机",
                "description": "降噪功能，30小时续航，蓝牙5.2",
                "price": 599.0,
                "suggest": 599.0,
                "category": "电子产品",
                "stock": 200,
                "unit": "副",
                "images": ["https://via.placeholder.com/300x300/7f8c8d/ffffff?text=耳机"],
                "rating": 4.3,
                "sales_count": 3500
            }
        ]

        for data in sample_data:
            products.append(Product(**data))

        return {p.id: p for p in products}

    def get_products(self, category=None, featured=False):
        """获取商品列表"""
        products = list(self.products.values())

        if category:
            products = [p for p in products if p.category == category]

        if featured:
            products = list(self.products.values())
            products = [p for p in products if p.is_featured]

        return products

    def get_product(self, product_id):
        """获取单个商品"""
        return self.products.get(product_id)

    # def add_order(self, order_data):
    #     """添加订单"""
    #     order_data['id'] = str(uuid.uuid4())[:8]
    #     order_data['created_at'] = datetime.now().isoformat()
    #     order_data['status'] = 'pending'
    #     self.orders.append(order_data)
    #     return order_data

    def load_product_info(self) -> Dict:
        """从JSON文件加载商品信息"""

        if not os.path.exists(self.products_file):
            Logger.warning(f"{self.products_file} not exist")
            Logger.warning(f"current path: {str(Path(__file__))}")
            return {}

        try:
            with open(self.products_file, 'r', encoding='utf-8') as f:
                sample_data = json.load(f)
                products = []
                for data in sample_data:
                    products.append(Product(**data))
                return {p.id: p for p in products}
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def save_product_info(self):
        """保存商品信息"""
        products_data = [self.products[key].to_dict() for key in self.products.keys()]
        with open(self.products_file, 'w', encoding='utf-8') as f:
            json.dump(products_data, f, ensure_ascii=False, indent=2)
