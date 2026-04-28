import sys
from pathlib import Path

# 必须在任何 kivy 模块导入前配置窗口大小
from kivy.config import Config
# PC 端窗口设为 360×800 像素，density=1.0，与手机端 360dp 有效宽度一致
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '800')
Config.set('graphics', 'resizable', '0')

cur_dir = Path(__file__).parent  # current directory
sys.path.extend([str(cur_dir.parent.parent), str(cur_dir.parent), str(cur_dir)])


from app import ShoppingCartApp

if __name__ == '__main__':
    ShoppingCartApp().run()
