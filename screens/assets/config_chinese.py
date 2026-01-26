# configs/font_config.py
# 全局共享的中文字体名称（所有文件统一使用这个名称）
CHINESE_FONT_NAME = "ChineseFont"

# 字体文件路径（项目根目录下的fonts文件夹）
FONT_FILE_PATH = "./screens/assets/fonts/msyhbd.ttc"


def register_chinese_font():
    """注册中文字体（全局仅需调用一次）"""
    from kivy.core.text import LabelBase

    # 注册字体（名称使用全局共享的CHINESE_FONT_NAME）
    LabelBase.register(
        name=CHINESE_FONT_NAME,
        fn_regular=FONT_FILE_PATH
    )


def set_kivymd_global_font(theme_cls):
    """配置KivyMD全局字体样式（所有控件生效）"""
    # 覆盖KivyMD所有默认字体样式，统一使用中文字体
    font_styles = {
        "H5": [CHINESE_FONT_NAME, 24, False, 0],
        "H6": [CHINESE_FONT_NAME, 20, False, 0.15],
        "Headline1": [CHINESE_FONT_NAME, 96, False, -0.015625],
        "Headline2": [CHINESE_FONT_NAME, 60, False, -0.008333333333333333],
        "Headline3": [CHINESE_FONT_NAME, 48, False, 0],
        "Headline4": [CHINESE_FONT_NAME, 34, False, 0.007352941176470588],
        "Headline5": [CHINESE_FONT_NAME, 24, False, 0],
        "Headline6": [CHINESE_FONT_NAME, 20, False, 0.0125],
        "Subtitle1": [CHINESE_FONT_NAME, 16, False, 0.009375],
        "Subtitle2": [CHINESE_FONT_NAME, 14, False, 0.007142857142857143],
        "Body1": [CHINESE_FONT_NAME, 16, False, 0.03125],
        "Body2": [CHINESE_FONT_NAME, 14, False, 0.017857142857142856],
        "Button": [CHINESE_FONT_NAME, 14, True, 0.08928571428571429],
        "Caption": [CHINESE_FONT_NAME, 12, False, 0.041666666666666664],
        "Overline": [CHINESE_FONT_NAME, 10, False, 0.05],
        "Title": [CHINESE_FONT_NAME, 16, False, 0.05],
        # 关键：新增TopAppBar标题专用样式（部分KivyMD版本需要）
        "TopAppBarTitle": [CHINESE_FONT_NAME, 20, False, 0.0125],
        "TopAppBarActionButton": [CHINESE_FONT_NAME, 14, True, 0.08928571428571429],
        # 关键：新增MDDialog标题专用样式
        "DialogTitle": [CHINESE_FONT_NAME, 20, False, 0.0125],  # 匹配标题默认大小
        "DialogContent": [CHINESE_FONT_NAME, 14, False, 0.017857142857142856],  # 顺带覆盖对话框内容文字
    }

    # 给theme_cls赋值，覆盖默认字体样式
    for style_name, style_config in font_styles.items():
        theme_cls.font_styles[style_name] = style_config

    # # 3. 关键兜底：设置默认字体（解决未指定font_style的MDLabel乱码）
    # theme_cls.default_font = CHINESE_FONT_NAME
    # # 额外：覆盖Kivy的全局默认字体（双重兜底，确保万无一失）
    # from kivy.config import Config
    # Config.set('kivy', 'default_font', [CHINESE_FONT_NAME, FONT_FILE_PATH])
