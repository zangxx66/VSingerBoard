import re
import flet as ft
from src.utils import bilibili_emoji, douyin_emoji


class Danmaku:
    """
    处理点歌弹幕的 emoji 表情组件
    """

    _emojiexp = re.compile(r"\[[\u4E00-\u9FA5A-Za-z0-9_]+\]")
    _bili_dict = {item["emoji"]: item["url"] for item in bilibili_emoji}
    _douyin_dict = {item["display_name"]: item["url"] for item in douyin_emoji}

    @staticmethod
    def process(source: str, msg: str):
        """
        弹幕emoji转换
        """
        result = msg
        if source == "bilibili":
            result = Danmaku._emojiexp.sub(
                lambda m: f'<img src="{Danmaku._bili_dict[m.group(0)]}" referrerpolicy="no-referrer" width="20" />'
                if m.group(0) in Danmaku._bili_dict
                else m.group(0),
                msg,
            )
        elif source == "douyin":
            result = Danmaku._emojiexp.sub(
                lambda m: f'<img src="{Danmaku._douyin_dict[m.group(0)]}" referrerpolicy="no-referrer" width="20" />'
                if m.group(0) in Danmaku._douyin_dict
                else m.group(0),
                msg,
            )

        return ft.Markdown(value=result, extension_set=ft.MarkdownExtensionSet.GITHUB_WEB)
