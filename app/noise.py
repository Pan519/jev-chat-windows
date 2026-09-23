# -*- coding: utf-8 -*-
"""群聊系统通知识别：纯 stdlib，不 import 任何重模块——悬浮窗（overlay）也要用它做兜底过滤，
而 app.ocr 模块级就拉着 RapidOCR，从那儿 import 会把 OCR 引擎拖进主进程。"""
import re

# 群聊系统通知的形状。**整行匹配**（先剥掉开头的引用名）：
# 系统通知整行就是通知本身；真人聊天里"聊到"这些词（「他刚才撤回了一条消息」）不会整行命中，不误杀。
_SYSTEM_NOISE = re.compile(
    r"通过扫描.{0,24}分享的二维码(加入|进入)了?群聊"
    r"|(?:你)?邀请.{1,24}(加入|进入)了?群聊"
    r"|加入了群聊"
    r"|退出群聊"
    r"|被.{1,20}移出群聊"
    r"|移出了群聊"
    r"|撤回了一条消息"
    r"|以上是打招呼的内容"
    r"|以下为新消息"
    r"|开启了朋友圈权限"
    r"|拍了拍.{0,12}"
)
_TIME_ONLY = re.compile(r"^\d{1,2}:\d{2}$")  # 纯时间戳分隔行
_LEADING_QUOTE = re.compile(r'^(?:["“」】][^"“「【】]{1,24}["”」】]|[「【][^」】]{1,24}[」】])\s*')


def is_system_noise(text: str) -> bool:
    """这行是不是群聊系统通知/时间戳（不是任何人说的话）。设置里的「过滤系统通知」开关用它。
    先剥掉系统通知开头的人名引用（"小白"退出群聊），再要求**整行**命中通知短语——
    只用子串搜索会把聊到这些词的真人消息一起误杀。"""
    t = str(text or "").strip()
    if _TIME_ONLY.match(t):
        return True
    while True:
        stripped = _LEADING_QUOTE.sub("", t)
        if stripped == t:
            break
        t = stripped
    return bool(_SYSTEM_NOISE.fullmatch(t))
