import sys
from pathlib import Path

# 必须在任何 kivy 模块导入前配置窗口大小
from kivy.config import Config
Config.set('graphics', 'width', '450')
Config.set('graphics', 'height', '900')
Config.set('graphics', 'resizable', '0')

cur_dir = Path(__file__).parent  # current directory
sys.path.extend([str(cur_dir.parent.parent), str(cur_dir.parent), str(cur_dir)])


from app import ShoppingCartApp

if __name__ == '__main__':
    ShoppingCartApp().run()
