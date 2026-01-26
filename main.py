import sys
from pathlib import Path

cur_dir = Path(__file__).parent  # current directory
sys.path.extend([str(cur_dir.parent.parent), str(cur_dir.parent), str(cur_dir)])


from app import ShoppingCartApp

if __name__ == '__main__':
    ShoppingCartApp().run()
