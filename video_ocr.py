# -*- coding: utf-8 -*-
"""
Video Subtitle Extractor  --  TWST / 18TRIP 打轴 + Windows 自带 OCR
V23

V22 -> V23 的改动:
  1. 【快】find_anchor 里的"局部背景亮度"从 165x165 高斯换成方框模糊:
     高斯哪怕分离实现也要几十毫秒,方框模糊走积分图每像素 O(1)。
     这是流水线里最贵的一笔(V22 实测约 3.7 倍慢主要就是它),判定逻辑不变;
  2. 时间戳本来就有了,这里说明一下位置:开始是日志第一行
     `🚀 === Vxx 开始提取 2026-10-13 12:19:03 ===`,写完 SRT 会打一行
     `💾 已写入: ... (共 N 条, 耗时 X 分钟)`。

V21 -> V22 的改动(详见 README.md):
  1. 【修】圆钮判定条件原来是反的:旧代码写 fill>=0.55(只收实心暗块),而真圆钮是
     "空心环"(实测 fill=0.12~0.13) —— 于是专挑立绘的帽子/头发、专排真圆钮。
     这是从引入 find_anchor 起就有的 bug,由你看出来的。现在改成:
     fill 0.08~0.45、aspect 0.85~1.20、尺寸占画面高 6.5%~13%(实测 82px/884=9.3%);
  2. 【新】模板匹配:程序读 exe 旁边的 anchor_template.png(圆钮截图),按"内容区高度的
     9.4%"缩放后在框左边找最像的位置,分数低于 0.60 不认。圆钮尺寸跟着画面高度走,
     所以换分辨率也能用;没有这个文件就自动退回形状判据;
  3. 【修】选项的备用帧不再按"墨水最多"挑:选项被按下时整个框会膨胀一下,那一帧字最大、
     墨水也最多,但它是放大的乱画面,OCR 读出来不是日文。现在固定用"第一次通过判定的帧"。
  注意:anchor_template.png 要和 exe 放在同一个文件夹里。

V20 -> V21 的改动(只动性能,判定逻辑一个字没改):
  1. 【快】圆钮检测降频:改成每 3 帧找一次(find_anchor 要在大片区域上做高斯模糊 +
     连通域,是每帧最贵的一笔),中间帧沿用上次结果 —— 省掉约三分之二;
  2. 【快】泡泡平整度改成"先看墨水、再验平整":没墨水的帧直接跳过(绝大多数帧都没墨水),
     有墨水的帧才去算,而且改用 OpenCV 的 HSV 取亮度、只抽 1/4 像素算分位;
  3. 【便利】挂机友好:日志每 10 秒打一行 `⏱ 已跑 x% / y 帧/秒 / 预计剩余 z 分`;
  4. 记一笔账:慢的从来不是 OCR(每句话才调一次),而是上面那两笔"每帧"的开销。
     原版慢是因为它每帧把整幅画面转一次 HSV(V14 起已经删掉)。

V19 -> V20 的改动(详见 README.md):
  1. 【新】默认判据换成「泡泡判定」(界面下拉框里的第一项):框里必须是一大片
     "平整的浅色泡泡"而且有墨水 —— 这是原版米色判据的加强版,多加了一条
     "泡泡内部的颜色必须是平的"。天空有渐变、沙地有花纹、立绘和糖果花里胡哨,都过不了;
     而且它不看字数,所以两个字的短句也算,不会再重复"短句被整个丢掉"的老毛病。
  2. 【修】选项轨不再要求"OCR 必须读出日文"。V19 那条太狠:真选项只要那一帧没读出来,
     整段就消失了 —— 1 小时片子里只活下来 2 条,而你对照完整 SRT 看到有很多选项。
     现在 泡泡+墨水+(圆钮 或 文字行) 就算一行选项,读得出文字就带上,
     读不出就留 `Line N [Choice]` 占位行,至少时间轴对得上、你能手动定位。
  3. 三种判据都在界面下拉框里(泡泡 / 结构 / 墨水),哪个顺手用哪个,不用重新编译。

V18 -> V19 的改动(详见 README.md):
  1. 【改】选项轨只输出"读得出日文"的选项:结构判据 + 圆钮 + OCR 必须读出假名/汉字,
     三者齐了才写一行 `文字 [Choice]`;读不出文字的整段直接丢掉。
     依据:实测真实选项(1:13 的「信じられない」)读得出来,而 40 张假选项的候选图
     一张都读不出文字 —— 这一条能一次性解决"满江红"。
  2. 界面新增「选项轨」勾选框(默认开):不想跑就取消勾选,不必去改 json。
  3. 顺带提醒:从压缩包临时目录运行时 video_ocr_config.json 每次都会重新生成,
     所以能按到的界面开关才是可靠的。

V17 -> V18 的改动(详见 README.md):
  1. 【修】选项轨重新用结构判据,不再跟着"判定"下拉框走。V17 里它跟着变成"墨水判定"
     之后,选项段在那片花花绿绿的背景上永远关不掉 —— 实测 12 条选项里 7 条时长离谱
     (97 秒 / 60 秒 / 46 秒 / 39 秒 …),把中间的对话全包进去了;
  2. 【修】"选项还在"改成 = 框里有文字行 **且** 圆钮还在;另加保险丝:超过 12 秒的
     选项段强制结算;
  3. 新增 `use_choice_track` 开关,嫌选项轨吵可以整个关掉(默认开);
  4. 【取消】OCR 多帧补救按你的要求关掉了(`retry_ocr_frames: 0`):短句就留空白 Line 行,
     不做猜测。想再打开把它设成 4 即可;
  5. 【修】复核窗口:连点只会开一个;选完文件把窗口抬回前面;跑完弹提示;
  6. 【修】复核选项行时改用"选项框"去核(以前用对话框的框,周围的对话会替它作证,
     12 条假选项只揪出 1 条)。

V16 -> V17 的改动(详见 README.md):
  1. 选项标记回归:读不出文字的选项段也输出 `Line N [Choice]`(方便人工定位),
     OCR 读到文字就带上文字 —— V16 的"读不出就整段丢弃"太狠,把 1:13 那处也丢了;
  2. OCR 补救:有些句子"墨水最多那一帧"正好是空气泡(实测确实有),扫描结束后会在
     它的时间范围内换几帧重试,把"真台词却变成 Line N"的补回来;
  3. 新增「🔍 复核」小窗口(视频 + SRT):逐条跳到它自己的时间里抽几帧核实,默认只出
     报告;也可以另存"标记版 SRT"(可疑行前面加 [?],方便在 Aegisub 里过一遍),
     或者直接删掉空行(自动存 .bak)。带 [Choice] 的行永不删。

V15 -> V16 的改动(详见 README.md)。这一版的原则是"宁可多,不可漏":
  1. 【重要】对话框默认改回 V12 的"只数墨水"判据。结构判据要求"≥3 个字形 + 占框宽
     25%",2~4 个字的短句达不到 —— 拿那份翻译稿逐条对过:7 分钟里翻译稿 105 条、
     V15 只出 99 条,少掉的 12 条全是「硬糖!?」「嗯?」「不要不要不要~!!」这类短句,
     连占位行都没有。现在默认"墨水判定"(不漏,可能多);结构判定留在下拉框里;
  2. 墨水判据改成跟界面上的阈值滑杆走(V15 的 legacy 模式写死用配置里的值);
  3. 选项加一道"像不像日语"的过滤:背景招牌读出来的 "f1NISH"、")0"、",ノ"、"すR"
     这类垃圾选项全部丢掉;
  4. 选项锁定时把开始时间对齐到"这个静止窗口的开头",不再把前面被误判的十几秒算进去。

V14 -> V15 的改动(详见 README.md):
  1. 【修】拖放失效:ctypes 把函数指针 cast 成 c_ssize_t(那是指针类型才行的位置),
     直接抛异常 → 日志里的"拖拽: 不可用"。改成 c_void_p,并补上 GetParent 的 restype;
  2. 【修】打字机效果导致的碎句:墨水正在增加的那些帧不算"换句",要连续若干帧墨水
     不再增长才允许按画面变化切断(60fps 下 1.3 的灵敏度会每多一个字就切一刀);
  3. 【修】缝合不再要求两句"完全相等":开头 70% 一致就合并,并保留更长的那句
     (「ひとりぼっちの主人公に」+「…になんの意味があるのだ?」合成一条);
  4. 【改】选项改成"锁定那一刻就试 OCR":读不出字的静止画面(立绘头发/护目镜、
     糖果装饰、黑影人物)不再锁定,继续等下一个静止瞬间;整段都读不出文字就直接丢弃,
     不再产出 `Line N [Choice]` —— 你那条片子 40 条假选项就是这么来的。

V13 -> V14 的改动(详见 README.md):
  1. 【修】OCR 不再复用事件循环。V13 把 asyncio.run 换成常驻 loop 之后,
     165 条里 136 条"判定认出了文字但 OCR 返回空" —— 这是最主要的问题,已退回 V12 写法;
  2. 【修】帧数阈值改成按秒换算:60fps 下"连丢 2 帧"只有 33ms,会把一句台词切得比
     30fps 碎很多;
  3. 【修】文字必须坐在"气泡底色"上:笔画周围要够浅够不花(黑字),或够暗(白字)。
     少了这一条,立绘的头发、护目镜、糖果装饰都会被当成"一行字" ——
     你那条片子多出来的 20 多条假 [Choice] 就是这么来的;
  4. OCR 取图分轨道:对话框先喂整个框(V12 一直这么干,最可靠;紧缩图实测会把
     一句话裁掉一截),选项框先喂紧缩图(顺手把左边圆钮排除),两个都不行就把图
     存到 _review/ocr_fail/;
  5. 日志会打出每次 OCR 用了哪块图、读到了什么、读不出时引擎报的什么原因;
  6. 判定/复核下拉框改成中文;
  7. 加拖放:视频文件拖进窗口即可加载。

V12 -> V13 的既有改动:阈值滑杆接进 TWST;判定换成"文字行结构"(字形连通域 + 同一
基线),不再用"区块浅色占比";选项判定改成"圆钮锚定 + 行内有文字",删掉背景红框那一套;
切断门槛改成相对值;区域改成内容区百分比并自动去黑边;进度条带时间码和输入跳转;
复核轮(可疑行报告,可选自动删除并备份);参数集中在 video_ocr_config.json。

注意:区域百分比相对"内容区"(去掉黑边之后),不是整帧。
"""
from __future__ import annotations

import asyncio
import datetime
import json
import os
import queue
import sys
import threading
import time
import traceback

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import cv2
import numpy as np
import srt
from PIL import Image, ImageTk

try:
    from _build_info import APP_VERSION, BUILD_DATE
except Exception:
    APP_VERSION, BUILD_DATE = "V13-dev", "2026-10-11"

APP_NAME = "Video Subtitle Extractor"

HAS_WIN_OCR = False
try:
    from winsdk.windows.media.ocr import OcrEngine
    from winsdk.windows.globalization import Language
    from winsdk.windows.graphics.imaging import SoftwareBitmap, BitmapPixelFormat
    import winsdk.windows.storage.streams as streams

    HAS_WIN_OCR = True
except ImportError:
    print("未安装 winsdk 库或不在 Windows 环境")


# 参数第一次运行会写成 exe 旁边的 video_ocr_config.json,之后直接改 json 就生效,
# 不用重新编译。删掉 json 会重新生成默认值。
DEFAULT_CONFIG = {
    "bin_threshold_twst": 175,
    "bin_threshold_white": 130,
    "bin_threshold_min": 110,
    "bin_threshold_max": 240,
    "text_start_density": 0.004,
    "cut_peak_ratio": 0.30,
    "cut_abs_floor": 0.0015,
    "min_dur_dialog": 0.25,
    "miss_seconds_to_cut": 0.08,
    "motion_cut_after": 0.20,
    "min_dur_choice": 0.50,
    "choice_still_seconds": 0.30,
    "choice_absent_seconds": 0.35,
    "motion_cut_stable_frames": 3,
    "merge_prefix_ratio": 0.7,
    "drop_unreadable_choice": False,
    "choice_min_jp_chars": 2,
    "choice_max_tries": 3,
    "retry_ocr_frames": 0,
    "use_choice_track": True,
    "choice_use_structure": True,
    "choice_max_seconds": 12.0,
    "check_frames": 4,
    "check_mark": "[?]",
    "check_min_glyphs": 2,
    "check_span_ratio": 0.08,
    "check_ocr_frames": 4,
    "check_min_seconds": 0.6,
    "still_diff": 0.001,
    "choice_start_density": 0.004,
    "min_glyphs": 3,
    "glyph_fill_min": 0.12,
    "glyph_fill_max": 0.62,
    "glyph_width_cv_min": 0.0,
    "ink_density_max": 0.45,
    "bg_pale_ratio_min": 0.50,
    "bg_pale_v_min": 140,
    "bg_pale_s_max": 90,
    "bg_dark_ratio_min": 0.40,
    "bg_dark_v_max": 120,
    "glyph_h_min_ratio": 0.022,
    "glyph_h_max_ratio": 0.14,
    "row_span_min_ratio": 0.25,
    "local_contrast": 18,
    "try_opposite_polarity": True,
    "anchor_search_left": 1.2,
    "anchor_search_updown": 0.9,
    # 圆钮实测(实拍帧 1914x884):82x82、fill=0.12~0.13、aspect=1.00、约占画面高 9.3%。
    # 旧版这里写的是 fill>=0.55 —— 只收实心暗块,把"空心环"的真圆钮全部排除,
    # 于是专挑立绘帽子/头发那种 fill=0.9 的块。这是从引入起就存在的真 bug。
    "anchor_aspect_min": 0.85,
    "anchor_aspect_max": 1.20,
    "anchor_fill_min": 0.08,
    "anchor_fill_max": 0.45,
    "anchor_h_min_ratio": 0.065,
    "anchor_h_max_ratio": 0.130,
    "anchor_h_ratio": 0.094,
    "anchor_tpl_min": 0.60,
    "require_anchor_in_white_mode": False,
    "detect_mode": "bubble",
    # 实测:室外选项条 浅色占比 0.86、室内选项条 0.93(但 V 跨度 59~82,带渐变),
    # 而室内背景(墙+地板)只有 0.34。所以:占比门槛提到 0.55,平整度放到 90 ——
    # 这样室内那种"稍微带渐变"的条子能过,背景依旧过不了。
    "bubble_ratio_min": 0.55,
    "bubble_sat_max": 100,
    "bubble_v_min": 120,
    "bubble_spread_max": 90,
    "anchor_every": 3,
    "review_mode": "report",
    "ocr_crop_to_text": True,
    "enable_drag_drop": True,
    "ocr_crop_pad_ratio": 0.6,
    "ocr_upscale_min_height": 96,
    "ocr_upscale_max_scale": 4.0,
    "ocr_fallback_full_roi": True,
    "save_failed_crops": True,
    "save_failed_crops_max": 40,
    "rect_d_pct": [26.0, 79.0, 47.0, 13.0],
    "rect_c_pct": [36.0, 29.0, 32.0, 11.0],
    "sensitivity": 1.3,
}


def app_dir():
    if "__compiled__" in globals() or getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.dirname(os.path.abspath(__file__))


def load_config():
    cfg = dict(DEFAULT_CONFIG)
    path = os.path.join(app_dir(), "video_ocr_config.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as fp:
                cfg.update(json.load(fp))
        except Exception:
            pass
    else:
        try:
            with open(path, "w", encoding="utf-8") as fp:
                json.dump(cfg, fp, ensure_ascii=False, indent=2)
        except Exception:
            pass
    return cfg


def fmt_timecode(seconds):
    seconds = max(0.0, float(seconds))
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    rest = seconds % 60
    if hours:
        return "%d:%02d:%04.1f" % (hours, minutes, rest)
    return "%02d:%04.1f" % (minutes, rest)


def parse_timecode(text, total_seconds):
    text = (text or "").strip().replace("：", ":")
    if not text:
        return None
    try:
        parts = text.split(":")
        if len(parts) > 3:
            return None
        value = 0.0
        for part in parts:
            value = value * 60.0 + float(part)
        if value < 0:
            return None
        return min(value, total_seconds)
    except Exception:
        return None


def write_image_unicode(path, img):
    """cv2.imwrite 碰到中文路径会静默失败,用 imencode + tofile 绕开。"""
    try:
        ext = os.path.splitext(path)[1] or ".jpg"
        ok, buf = cv2.imencode(ext, img)
        if ok:
            buf.tofile(path)
            return True
    except Exception:
        pass
    return False


def similar_prefix(a, b, ratio=0.7, min_chars=4):
    """两句开头有多少字一样 —— 用来把"打字机效果"造成的碎句缝回去。

    例如「ひとりぼっちの主人公に」和「ひとりぼっちの主人公になんの意味があるのだ?」
    开头 11 个字一致,就该合成一条(保留长的那句),而不是当成两句台词。
    OCR 尾部偶尔多个垃圾字符也没关系,只看开头。
    """
    if not a or not b:
        return False
    shorter = min(len(a), len(b))
    if shorter < min_chars:
        return False
    common = 0
    for x, y in zip(a, b):
        if x != y:
            break
        common += 1
    return common >= max(min_chars, int(shorter * ratio))


def jp_char_count(text):
    """数一句话里有多少假名/汉字。

    用来把从背景招牌上读来的垃圾选项滤掉:实测出现过 "f1NISH"(FINISH 横幅)、
    ")0"、",ノ"、"すR" 这种,而真选项(比如「信じられない」)全是假名。
    """
    count = 0
    for ch in text or "":
        code = ord(ch)
        if (0x3040 <= code <= 0x30FF or 0x4E00 <= code <= 0x9FFF
                or 0x3400 <= code <= 0x4DBF):
            count += 1
    return count


def tight_crop(roi, info, cfg):
    """按文字行裁一块给 OCR 用,上下留余量,免得变成又长又窄的一条。

    V13 初版这里只留 3 像素,结果 700x40 那种细条 Windows OCR 经常读不出东西;
    现在按字高的 0.6 倍上下补白,并交给 prepare_ocr_image 放大。
    """
    if roi is None or getattr(roi, "size", 0) == 0:
        return None
    if not cfg.get("ocr_crop_to_text", True) or not info or not info.get("text_bbox"):
        return roi.copy()
    bx, by, bw, bh = info["text_bbox"]
    pad_y = int(bh * float(cfg.get("ocr_crop_pad_ratio", 0.6))) + 4
    x0 = max(0, bx - 4)
    y0 = max(0, by - pad_y)
    x1 = min(roi.shape[1], bx + bw + 4)
    y1 = min(roi.shape[0], by + bh + pad_y)
    if x1 <= x0 or y1 <= y0:
        return roi.copy()
    return roi[y0:y1, x0:x1].copy()


def prepare_ocr_image(crop, cfg):
    """小图放大再送 OCR(Windows OCR 对几十像素高的图很不友好)。"""
    if crop is None or getattr(crop, "size", 0) == 0:
        return crop
    min_h = int(cfg.get("ocr_upscale_min_height", 96))
    if min_h <= 0:
        return crop
    height, width = crop.shape[:2]
    if height >= min_h or height <= 0:
        return crop
    scale = min(float(cfg.get("ocr_upscale_max_scale", 4.0)),
                max(2.0, min_h / float(height)))
    return cv2.resize(crop, (max(1, int(width * scale)), max(1, int(height * scale))),
                      interpolation=cv2.INTER_CUBIC)


def grab_frame(cap, index):
    """跳到指定帧读一张图。seek 会从关键帧开始解,偶尔偏几帧,复核够用了。"""
    try:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(max(0, index)))
        ok, frame = cap.read()
        return frame if ok else None
    except Exception:
        return None


def _ink_mask(gray, dark_on_light, thr, local_contrast):
    """二值化 + 局部对比过滤:只有比周围明显暗(或亮)的细东西才算笔画。"""
    height = gray.shape[0]
    ksize = max(5, int(round(height * 0.7)) | 1)
    bg = cv2.GaussianBlur(gray, (ksize, ksize), 0)
    g16 = gray.astype(np.int16)
    b16 = bg.astype(np.int16)
    if dark_on_light:
        local = b16 - g16
        _, ink = cv2.threshold(gray, int(thr), 255, cv2.THRESH_BINARY_INV)
    else:
        local = g16 - b16
        _, ink = cv2.threshold(gray, int(thr), 255, cv2.THRESH_BINARY)
    gate = (local > int(local_contrast)).astype(np.uint8) * 255
    return cv2.bitwise_and(ink, gate)


def analyze_text(roi, dark_on_light, thr, content_h, cfg, prev_mask=None):
    """在 roi(BGR) 里判断有没有一行文字。

    返回 dict: ok / nglyph / glyph_h / ink_density / diff_score / mask / text_bbox
    """
    if roi is None or getattr(roi, "size", 0) == 0:
        return None
    height, width = roi.shape[:2]
    if width < 8 or height < 6:
        return None

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    ink = _ink_mask(gray, dark_on_light, thr, cfg["local_contrast"])
    dil = cv2.dilate(ink, np.ones((3, 3), np.uint8), iterations=1)
    density = cv2.countNonZero(dil) / float(width * height)
    diff = 0.0
    if prev_mask is not None and prev_mask.shape == ink.shape:
        diff = cv2.countNonZero(cv2.absdiff(ink, prev_mask)) / float(width * height)

    info = {
        "ok": False, "nglyph": 0, "glyph_h": 0.0, "ink_density": density,
        "diff_score": diff, "mask": ink, "text_bbox": None,
        "bg_pale": 0.0, "bg_dark": 0.0,
    }
    if density > cfg["ink_density_max"] * 1.6:
        return info

    try:
        count, _labels, stats, _cents = cv2.connectedComponentsWithStats(ink, 8)
    except Exception:
        return info

    boxes = []
    for i in range(1, count):
        x, y, bw, bh, area = (int(stats[i][j]) for j in range(5))
        if area < 12 or bh < 6 or bw < 2:
            continue
        aspect = bw / float(bh)
        if aspect < 0.10 or aspect > 2.4:
            continue
        fill = area / float(bw * bh)
        if fill < cfg["glyph_fill_min"] or fill > cfg["glyph_fill_max"]:
            continue
        boxes.append((x, y, bw, bh))

    if len(boxes) < max(2, int(cfg["min_glyphs"]) - 1):
        return info

    med_h = float(np.median([b[3] for b in boxes]))
    if med_h < max(6.0, cfg["glyph_h_min_ratio"] * content_h):
        return info
    if med_h > cfg["glyph_h_max_ratio"] * content_h:
        return info

    keep = [b for b in boxes if 0.55 * med_h <= b[3] <= 1.75 * med_h]
    if len(keep) < int(cfg["min_glyphs"]):
        return info

    keep.sort(key=lambda b: b[1] + b[3] / 2.0)
    rows = []
    for box in keep:
        cy = box[1] + box[3] / 2.0
        for row in rows:
            if abs(row["cy"] - cy) <= 0.7 * med_h:
                row["items"].append(box)
                row["cy"] = sum(it[1] + it[3] / 2.0 for it in row["items"]) / len(row["items"])
                break
        else:
            rows.append({"cy": cy, "items": [box]})
    rows.sort(key=lambda r: -len(r["items"]))
    items = rows[0]["items"]
    if len(items) < int(cfg["min_glyphs"]):
        return info

    xs0 = min(it[0] for it in items)
    xs1 = max(it[0] + it[2] for it in items)
    if (xs1 - xs0) < cfg["row_span_min_ratio"] * width:
        return info

    if cfg.get("glyph_width_cv_min", 0) > 0:
        widths = np.array([it[2] for it in items], dtype=np.float64)
        if widths.mean() > 0 and (widths.std() / widths.mean()) < cfg["glyph_width_cv_min"]:
            return info

    ys0 = min(it[1] for it in items)
    ys1 = max(it[1] + it[3] for it in items)

    # 关键的一条:文字得坐在"气泡底色"上。
    # 黑字(TWST) → 笔画周围要够浅、不花;白字/章节卡 → 周围要够暗。
    # 少了这一条,立绘的头发、护目镜、糖果装饰都会被当成"一行字"。
    y_lo = max(0, ys0 - 2)
    y_hi = ys1 + 3
    x_lo = max(0, xs0 - 2)
    x_hi = xs1 + 3
    bg_pale = 0.0
    bg_dark = 0.0
    try:
        sub = roi[y_lo:y_hi, x_lo:x_hi].astype(np.int16)
        sub_ink = ink[y_lo:y_hi, x_lo:x_hi]
        mx = sub.max(axis=2)
        mn = sub.min(axis=2)
        sat = np.where(mx > 0, (mx - mn) * 255 // np.maximum(mx, 1), 0)
        pale = (sat < cfg["bg_pale_s_max"]) & (mx >= cfg["bg_pale_v_min"])
        darkpx = mx <= cfg["bg_dark_v_max"]
        bgmask = sub_ink == 0
        if int(bgmask.sum()) > 20:
            bg_pale = float(pale[bgmask].mean())
            bg_dark = float(darkpx[bgmask].mean())
    except Exception:
        pass
    info["bg_pale"] = bg_pale
    info["bg_dark"] = bg_dark
    if dark_on_light:
        if bg_pale < cfg["bg_pale_ratio_min"]:
            return info
    else:
        if bg_dark < cfg["bg_dark_ratio_min"]:
            return info

    info["ok"] = True
    info["nglyph"] = len(items)
    info["glyph_h"] = med_h
    info["text_bbox"] = (xs0, ys0, xs1 - xs0 + 1, ys1 - ys0 + 1)
    return info


def analyze_text_auto(roi, dark_on_light, thr, content_h, cfg, prev_mask=None):
    """先按设定极性认;认不出且允许的话,反过来再认一次(章节卡那种反极性文字)。"""
    info = analyze_text(roi, dark_on_light, thr, content_h, cfg, prev_mask)
    if info and info["ok"]:
        return info
    if not cfg.get("try_opposite_polarity", True):
        return info
    strict = dict(cfg)
    strict["min_glyphs"] = int(cfg["min_glyphs"]) + 1
    alt = analyze_text(roi, not dark_on_light, thr, content_h, strict, prev_mask)
    if alt and alt["ok"]:
        return alt
    return info


def legacy_density(roi, dark_on_light, thr, cfg, prev_mask=None):
    """V12 的老判据:只数墨水(二值化后的像素占比)。

    V16 起这是对话框的默认判据。原因是结构判据要求"至少 3 个字形 + 占框宽 25%",
    而 2~4 个字的短句天生达不到 —— 实测那一版把 105 条里的 12 条整个丢掉了,
    丢的全是「硬糖!?」「嗯?」「不要不要不要~!!」这类短句,连 Line N 占位都没有。
    只数墨水就不会漏:短句照样成行,顶多 OCR 读不出、留个占位行给你手补。
    """
    height, width = roi.shape[:2]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    if dark_on_light:
        _, ink = cv2.threshold(gray, int(thr), 255, cv2.THRESH_BINARY_INV)
    else:
        _, ink = cv2.threshold(gray, int(thr), 255, cv2.THRESH_BINARY)
    dil = cv2.dilate(ink, np.ones((3, 3), np.uint8), iterations=1)
    density = cv2.countNonZero(dil) / float(width * height)
    diff = 0.0
    if prev_mask is not None and prev_mask.shape == ink.shape:
        diff = cv2.countNonZero(cv2.absdiff(ink, prev_mask)) / float(width * height)
    return {
        "ok": density > cfg["text_start_density"], "nglyph": -1, "glyph_h": 0.0,
        "ink_density": density, "diff_score": diff, "mask": ink, "text_bbox": None,
    }


def bubble_stats(roi, cfg):
    """看看这块地方是不是"一大片平整的浅色泡泡"。

    这是原版那个米色占比判据的加强版:原版只看"浅色占多少",所以天空、沙子、
    白栅栏都能骗过它;这里再加一条 —— 泡泡内部的颜色必须是"平的"(颜色跨度小),
    而天空有渐变、沙地有花纹、立绘和糖果更是花里胡哨,都过不了这一关。
    好处是不看字数(短句照样算),也不看位置。
    返回 (浅色占比, 底色跨度, 是否像泡泡)。
    """
    try:
        # 用 OpenCV 的 HSV(C 实现)取饱和度和亮度,比在 numpy 里做 int16 运算快得多
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        sat = hsv[:, :, 1]
        vch = hsv[:, :, 2]
        pale = (sat < cfg["bubble_sat_max"]) & (vch >= cfg["bubble_v_min"])
        ratio = float(pale.mean())
        vals = vch[pale]
        if vals.size < 50:
            return ratio, 999.0, False
        if vals.size > 4000:
            vals = vals[::4]           # 抽 1/4 足够,省掉大半排序开销
        spread = float(np.percentile(vals, 90) - np.percentile(vals, 10))
        ok = (ratio >= cfg["bubble_ratio_min"]
              and spread <= cfg["bubble_spread_max"])
        return ratio, spread, ok
    except Exception:
        return 0.0, 999.0, False


def bubble_density(roi, dark_on_light, thr, cfg, prev_mask=None):
    """泡泡判定:框里得是一大片平整的浅色泡泡,而且里面有墨水。"""
    info = legacy_density(roi, dark_on_light, thr, cfg, prev_mask)
    # 先看墨水:没墨水的帧(绝大多数)直接跳过后面那笔昂贵计算
    if info["ink_density"] < cfg["text_start_density"]:
        info["bubble_ratio"] = 0.0
        info["bubble_spread"] = 999.0
        info["ok"] = False
        return info
    ratio, spread, flat = bubble_stats(roi, cfg)
    info["bubble_ratio"] = ratio
    info["bubble_spread"] = spread
    info["ok"] = bool(flat)
    return info


def find_anchor(frame, rect_px, content, cfg):
    """在框的左边和上下找棕色底的黑色圆钮(▶),返回 (x, y, w, h) 或 None。"""
    cx0, cy0, cw, chh = content
    x, y, w, h = rect_px
    sx0 = int(max(cx0, x - cfg["anchor_search_left"] * w))
    sx1 = int(min(cx0 + cw, x + w * 0.6))
    sy0 = int(max(cy0, y - cfg["anchor_search_updown"] * h))
    sy1 = int(min(cy0 + chh, y + h + cfg["anchor_search_updown"] * h))
    if sx1 - sx0 < 24 or sy1 - sy0 < 24:
        return None

    sub = frame[sy0:sy1, sx0:sx1]
    gray = cv2.cvtColor(sub, cv2.COLOR_BGR2GRAY)
    ksize = max(5, int(round(sub.shape[0] * 0.55)) | 1)
    # 这里只需要"局部背景亮度",用不着高斯:方框模糊走积分图,每像素 O(1),
    # 而 165x165 的高斯哪怕分离实现也要几十毫秒 —— 这是流水线里最贵的一笔。
    bg = cv2.blur(gray, (ksize, ksize))
    dark = ((bg.astype(np.int16) - gray.astype(np.int16)) > 30).astype(np.uint8) * 255
    try:
        count, _labels, stats, _cents = cv2.connectedComponentsWithStats(dark, 8)
    except Exception:
        return None

    best = None
    for i in range(1, count):
        bx, by, bw, bh, area = (int(stats[i][j]) for j in range(5))
        if bh < cfg["anchor_h_min_ratio"] * chh or bh > cfg["anchor_h_max_ratio"] * chh:
            continue
        aspect = bw / float(bh)
        if aspect < cfg["anchor_aspect_min"] or aspect > cfg["anchor_aspect_max"]:
            continue
        fill = area / float(bw * bh)
        if fill < cfg["anchor_fill_min"] or fill > cfg["anchor_fill_max"]:
            continue
        gx, gy = sx0 + bx, sy0 + by
        if gx + bw < x - w * 0.4:
            continue
        if gy + bh < y - h * 0.8 or gy > y + h + h * 0.8:
            continue
        if best is None or area > best[0]:
            best = (area, (gx, gy, bw, bh))
    return None if best is None else best[1]


def load_anchor_template():
    """读 exe 旁边的 anchor_template.png(圆钮小截图)。没有就返回 None,自动退回形状判据。"""
    try:
        path = os.path.join(app_dir(), "anchor_template.png")
        if not os.path.exists(path):
            return None
        buf = np.fromfile(path, dtype=np.uint8)
        img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
        if img is None or img.size == 0:
            return None
        return img
    except Exception:
        return None


def find_anchor_tpl(frame, rect_px, content, cfg, tpl):
    """用模板匹配找圆钮 —— 比手写形状规则可靠得多。

    模板按"内容区高度的 9.4%"缩放(圆钮尺寸跟着画面高度走,所以换分辨率也能用),
    再上下浮动两档,在框左边那块区域里取相似度最高的位置。
    返回 (位置, 最高分);分数不到 anchor_tpl_min 就不认。
    """
    try:
        cx0, cy0, cw, chh = content
        x, y, w, h = rect_px
        sx0 = int(max(cx0, x - cfg["anchor_search_left"] * w))
        sx1 = int(min(cx0 + cw, x + w * 0.5))
        sy0 = int(max(cy0, y - cfg["anchor_search_updown"] * h))
        sy1 = int(min(cy0 + chh, y + h + cfg["anchor_search_updown"] * h))
        if sx1 - sx0 < 40 or sy1 - sy0 < 40:
            return None, 0.0
        sub = frame[sy0:sy1, sx0:sx1]
        th, tw = tpl.shape[:2]
        want = max(8.0, chh * float(cfg.get("anchor_h_ratio", 0.094)))
        best, best_score = None, 0.0
        for scale in (want / th, want / th * 1.15, want / th * 0.87):
            nw, nh = max(8, int(tw * scale)), max(8, int(th * scale))
            if nh >= sub.shape[0] or nw >= sub.shape[1]:
                continue
            t = cv2.resize(tpl, (nw, nh),
                           interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC)
            res = cv2.matchTemplate(sub, t, cv2.TM_CCOEFF_NORMED)
            _mn, mx, _ml, ml = cv2.minMaxLoc(res)
            if float(mx) > best_score:
                best_score = float(mx)
                best = (sx0 + int(ml[0]), sy0 + int(ml[1]), nw, nh)
        if best is None or best_score < float(cfg.get("anchor_tpl_min", 0.60)):
            return None, best_score
        return best, best_score
    except Exception:
        return None, 0.0


def detect_content_area(frames, width, height):
    """去掉录屏常见的上下/左右黑边,返回 (x0, y0, w, h)。"""
    if not frames:
        return (0, 0, width, height)
    grays = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in frames]
    stack = np.min(np.stack(grays, axis=0), axis=0)
    dark_row = (stack < 40).mean(axis=1) > 0.9
    dark_col = (stack < 40).mean(axis=0) > 0.9
    y0, y1 = 0, height - 1
    while y0 < height and dark_row[y0]:
        y0 += 1
    while y1 > y0 and dark_row[y1]:
        y1 -= 1
    x0, x1 = 0, width - 1
    while x0 < width and dark_col[x0]:
        x0 += 1
    while x1 > x0 and dark_col[x1]:
        x1 -= 1
    cw, chh = x1 - x0 + 1, y1 - y0 + 1
    if cw < width * 0.5 or chh < height * 0.4 or cw < 16 or chh < 16:
        return (0, 0, width, height)
    return (x0, y0, cw, chh)


# ---- 以下为主程序部分(App / 主流程 / 复核) ----

# 说明:OCR 每次调用都新建事件循环(asyncio.run)。
# V13 里改成"复用同一个事件循环"之后,Windows OCR 大部分时候返回空字符串
# (实测 165 条里 136 条拿不到文本),所以退回 V12 的写法。


class VideoProcessor:
    def __init__(self, logger):
        self.ocr_engine = None
        self.last_error = ""
        self.logger = logger
        if HAS_WIN_OCR:
            try:
                lang = Language("ja-JP")
                if OcrEngine.is_language_supported(lang):
                    self.ocr_engine = OcrEngine.try_create_from_language(lang)
                    self.logger("✅ [系统] Windows OCR (日语) 就绪。")
                else:
                    self.logger("⚠️ [系统] OCR 初始化失败：未安装日语语言包。")
            except Exception as exc:
                self.logger("❌ [系统] OCR 初始化异常: %s" % exc)

    async def _run_win_ocr(self, cv2_img):
        if not self.ocr_engine:
            self.last_error = "OCR引擎未初始化"
            return ""
        try:
            bgra = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2BGRA)
            height, width = bgra.shape[:2]
            writer = streams.DataWriter()
            writer.write_bytes(bgra.tobytes())
            ibuffer = writer.detach_buffer()
            bitmap = SoftwareBitmap.create_copy_from_buffer(
                ibuffer, BitmapPixelFormat.BGRA8, width, height
            )
            result = await self.ocr_engine.recognize_async(bitmap)
            return result.text.replace(" ", "")
        except Exception as exc:
            self.last_error = "%s: %s" % (type(exc).__name__, exc)
            return ""

    def ocr_image(self, img):
        """返回识别到的文本;失败原因记在 self.last_error 里(方便排查)。"""
        self.last_error = ""
        if not HAS_WIN_OCR:
            self.last_error = "winsdk 不可用"
            return ""
        if img is None or getattr(img, "size", 0) == 0:
            self.last_error = "图片为空"
            return ""
        try:
            text = asyncio.run(self._run_win_ocr(img))
        except Exception as exc:
            self.last_error = "%s: %s" % (type(exc).__name__, exc)
            return ""
        if not text and not self.last_error:
            self.last_error = "引擎没报错但结果为空"
        elif text and len(text.strip()) < 2:
            self.last_error = "结果太短: %r" % text[:20]
        return text


class Rec:
    """一条字幕 + 复核要用的信息。"""

    __slots__ = ("st", "et", "content", "kind", "crop", "nglyph", "ocr_ok",
                 "anchor", "i0", "i1", "reason")

    def __init__(self, st, et, content, kind):
        self.st = st
        self.et = et
        self.content = content
        self.kind = kind
        self.crop = None
        self.nglyph = 0
        self.ocr_ok = False
        self.anchor = False
        self.i0 = 0
        self.i1 = 0
        self.reason = []


def install_drop_target(root, on_files):
    """让窗口能接收"把文件拖进来"(Win32 WM_DROPFILES,不需要额外依赖)。

    失败就静默放弃,不影响其它功能。回调必须留引用,否则会被 Python 回收。
    """
    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        shell32 = ctypes.windll.shell32
        # 指针一律用 c_void_p。V14 这里写的是 c_ssize_t 加 ctypes.cast(..., c_ssize_t),
        # 而 cast 的第二个参数必须是"指针类型",于是抛异常、拖放整个失效
        # (日志里那句"拖拽: 不可用(用按钮加载也一样)"就是这么来的)。
        PTR = ctypes.c_void_p
        user32.GetParent.restype = wintypes.HWND
        user32.GetParent.argtypes = [wintypes.HWND]
        user32.GetWindowLongPtrW.restype = PTR
        user32.GetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int]
        user32.SetWindowLongPtrW.restype = PTR
        user32.SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, PTR]
        user32.CallWindowProcW.restype = ctypes.c_ssize_t
        user32.CallWindowProcW.argtypes = [PTR, wintypes.HWND, ctypes.c_uint,
                                           PTR, PTR]
        shell32.DragQueryFileW.argtypes = [PTR, ctypes.c_uint,
                                           ctypes.c_wchar_p, ctypes.c_uint]
        shell32.DragQueryFileW.restype = ctypes.c_uint
        shell32.DragFinish.argtypes = [PTR]
        shell32.DragAcceptFiles.argtypes = [wintypes.HWND, wintypes.BOOL]

        root.update_idletasks()
        hwnd = user32.GetParent(root.winfo_id()) or root.winfo_id()
        wm_dropfiles = 0x0233
        gwlp_wndproc = -4
        proc_type = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, wintypes.HWND, ctypes.c_uint,
                                       PTR, PTR)
        old_proc = user32.GetWindowLongPtrW(hwnd, gwlp_wndproc) or 0

        def handler(h, msg, wparam, lparam):
            if msg == wm_dropfiles:
                try:
                    count = shell32.DragQueryFileW(wparam, 0xFFFFFFFF, None, 0)
                    files = []
                    for i in range(count):
                        buf = ctypes.create_unicode_buffer(1024)
                        if shell32.DragQueryFileW(wparam, i, buf, 1024):
                            files.append(buf.value)
                    shell32.DragFinish(wparam)
                    if files:
                        root.after(10, lambda f=files: on_files(f))
                except Exception:
                    pass
                return 0
            return user32.CallWindowProcW(old_proc, h, msg, wparam, lparam)

        proc = proc_type(handler)
        user32.SetWindowLongPtrW(hwnd, gwlp_wndproc, ctypes.cast(proc, PTR))
        shell32.DragAcceptFiles(hwnd, True)
        root._drop_proc = proc
        return True
    except Exception:
        return False


class App:
    def __init__(self, root, cfg):
        self.cfg = cfg
        self.root = root
        self.root.title("%s %s (%s)  结构判定版" % (APP_NAME, APP_VERSION, BUILD_DATE))
        self.root.geometry("1280x900")

        self.rect_pct = {
            "d": list(cfg["rect_d_pct"]),
            "c": list(cfg["rect_c_pct"]),
        }
        self.content = (0, 0, 0, 0)
        self.video_path = ""
        self.cap = None
        self.total_frames = 0
        self.fps = 30.0
        self.is_processing = False
        self.preview_index = 0
        self.preview_cache = (None, None)
        self.log_q = queue.Queue()

        self._setup_ui()
        self.processor = VideoProcessor(self.log)
        if self.cfg.get("enable_drag_drop", True):
            self.drop_ok = install_drop_target(self.root, self._on_drop_files)
        else:
            self.drop_ok = False
        self.log("ℹ️ 版本 %s / 构建 %s" % (APP_VERSION, BUILD_DATE))
        self.log("ℹ️ 参数文件: %s" % os.path.join(app_dir(), "video_ocr_config.json"))
        self.log("ℹ️ 拖拽: %s" % ("已启用" if self.drop_ok else "不可用(用按钮加载也一样)"))
        self.root.after(120, self._drain_log)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------------- 日志 / 收尾 ----------------
    def log(self, message):
        self.log_q.put(str(message))

    def _drain_log(self):
        try:
            for _ in range(300):
                msg = self.log_q.get_nowait()
                self.txt_log.config(state=tk.NORMAL)
                self.txt_log.insert(tk.END, msg + "\n")
                self.txt_log.see(tk.END)
                self.txt_log.config(state=tk.DISABLED)
        except queue.Empty:
            pass
        except Exception:
            pass
        self.root.after(120, self._drain_log)

    def on_close(self):
        self.is_processing = False
        try:
            if self.cap:
                self.cap.release()
        except Exception:
            pass
        self.root.destroy()

    # ---------------- 界面 ----------------
    def _setup_ui(self):
        f_top1 = tk.Frame(self.root, pady=5)
        f_top1.pack(fill=tk.X, padx=10)
        tk.Button(f_top1, text="📂 加载视频", command=self.load_video,
                  font=("微软雅黑", 10)).pack(side=tk.LEFT)
        tk.Button(f_top1, text="🔍 复核(视频+SRT)", command=self.open_check_window,
                  font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=8)
        self.lbl_info = tk.Label(f_top1, text="未加载...", fg="blue")
        self.lbl_info.pack(side=tk.LEFT, padx=10)
        self.lbl_content = tk.Label(f_top1, text="内容区: -", fg="#666")
        self.lbl_content.pack(side=tk.LEFT)

        f_top2 = tk.Frame(self.root, pady=5)
        f_top2.pack(fill=tk.X, padx=10)
        self.var_mode = tk.StringVar(value="BLACK")
        tk.Label(f_top2, text="模式:", font=("微软雅黑", 10, "bold")).pack(side=tk.LEFT)
        tk.Radiobutton(f_top2, text="TWST (黑字)", variable=self.var_mode,
                       value="BLACK").pack(side=tk.LEFT)
        tk.Radiobutton(f_top2, text="18TRIP (白字)", variable=self.var_mode,
                       value="WHITE").pack(side=tk.LEFT, padx=10)

        _dm = str(self.cfg.get("detect_mode", "bubble"))
        init_detect = ("泡泡判定" if _dm.startswith("bub")
                       else ("结构判定" if _dm.startswith("str") else "墨水判定"))
        self.var_detect = tk.StringVar(value=init_detect)
        tk.Label(f_top2, text="判定:").pack(side=tk.LEFT, padx=(14, 2))
        ttk.Combobox(f_top2, textvariable=self.var_detect, width=10, state="readonly",
                     values=("泡泡判定", "结构判定", "墨水判定")).pack(side=tk.LEFT)

        init_review = {"off": "关闭", "report": "只报告", "report+delete": "报告并删除"}.get(
            str(self.cfg.get("review_mode", "report")), "只报告")
        self.var_review = tk.StringVar(value=init_review)
        tk.Label(f_top2, text="复核:").pack(side=tk.LEFT, padx=(14, 2))
        ttk.Combobox(f_top2, textvariable=self.var_review, width=10, state="readonly",
                     values=("关闭", "只报告", "报告并删除")).pack(side=tk.LEFT)

        self.var_ocr = tk.BooleanVar(value=False)
        cb_ocr = tk.Checkbutton(f_top2, text="启用 OCR", variable=self.var_ocr,
                                font=("微软雅黑", 10, "bold"), fg="purple")
        cb_ocr.pack(side=tk.LEFT, padx=14)
        if not HAS_WIN_OCR:
            cb_ocr.config(state=tk.DISABLED, text="OCR不可用")

        # 选项轨开关放到界面上:从压缩包临时目录运行时 json 每次都重新生成,
        # 改 json 等于没用,所以这类开关必须在界面上能按到。
        self.var_choice = tk.BooleanVar(value=bool(self.cfg.get("use_choice_track", True)))
        tk.Checkbutton(f_top2, text="选项轨", variable=self.var_choice,
                       font=("微软雅黑", 10, "bold"), fg="#a0522d"
                       ).pack(side=tk.LEFT, padx=(14, 0))

        self.var_verbose = tk.BooleanVar(value=True)
        tk.Checkbutton(f_top2, text="诊断日志", variable=self.var_verbose).pack(side=tk.LEFT)

        self.btn_run = tk.Button(f_top2, text="▶️ 开始处理", command=self.start_task,
                                 bg="#ddffdd", font=("微软雅黑", 11, "bold"))
        self.btn_run.pack(side=tk.RIGHT)
        self.btn_stop = tk.Button(f_top2, text="🛑 停止", command=self.stop_task,
                                  bg="#ffdddd", font=("微软雅黑", 11), state=tk.DISABLED)
        self.btn_stop.pack(side=tk.RIGHT, padx=10)

        f_mid = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        f_mid.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        canvas_frame = tk.Frame(f_mid, bg="#222")
        f_mid.add(canvas_frame, stretch="always")
        self.canvas = tk.Canvas(canvas_frame, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.create_text(440, 180,
                                text="把视频文件拖到这里\n（或点左上角「📂 加载视频」）",
                                fill="#8a8a8a", font=("微软雅黑", 16), tags="hint")

        f_log = tk.Frame(f_mid)
        f_mid.add(f_log, width=380)
        tk.Label(f_log, text="📜 运行日志").pack(anchor="w")
        self.txt_log = tk.Text(f_log, bg="#1e1e1e", fg="#00ff00",
                               font=("Consolas", 9), state=tk.DISABLED)
        self.txt_log.pack(fill=tk.BOTH, expand=True)

        f_ctrl = tk.Frame(self.root, height=180)
        f_ctrl.pack(fill=tk.X, padx=10, pady=5)
        self.nb = ttk.Notebook(f_ctrl)
        self.nb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.rect_ui = {}
        self.create_tab("对话框(绿)", "d")
        self.create_tab("选项框(蓝)", "c")
        self.nb.bind("<<NotebookTabChanged>>", lambda _e: self.update_preview(force=True))

        f_sets = tk.LabelFrame(f_ctrl, text="设置", padx=5)
        f_sets.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        tk.Label(f_sets, text="防连读灵敏度(越小越容易切断):").pack(anchor="w")
        self.s_diff = tk.Scale(f_sets, from_=0.3, to=10.0, resolution=0.1,
                               orient=tk.HORIZONTAL)
        self.s_diff.set(float(self.cfg["sensitivity"]))
        self.s_diff.pack(fill=tk.X)

        tk.Label(f_sets, text="文字/边缘 阈值(TWST 也生效):").pack(anchor="w")
        self.s_bin = tk.Scale(f_sets, from_=float(self.cfg["bin_threshold_min"]),
                              to=float(self.cfg["bin_threshold_max"]),
                              orient=tk.HORIZONTAL, command=self.on_bin_change)
        self.s_bin.set(float(self.cfg["bin_threshold_twst"]))
        self.s_bin.pack(fill=tk.X)

        f_bot = tk.Frame(self.root)
        f_bot.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=8)
        line1 = tk.Frame(f_bot)
        line1.pack(fill=tk.X)
        self.lbl_time = tk.Label(line1, text="00:00.0 / 00:00.0", width=22, anchor="w")
        self.lbl_time.pack(side=tk.LEFT)
        self.ent_jump = tk.Entry(line1, width=12)
        self.ent_jump.pack(side=tk.LEFT, padx=(6, 2))
        self.ent_jump.bind("<Return>", lambda _e: self.jump_to_entry())
        tk.Button(line1, text="跳转", command=self.jump_to_entry).pack(side=tk.LEFT)
        tk.Label(line1, text="(可填 90 / 1:30 / 01:02:03)").pack(side=tk.LEFT, padx=6)

        self.s_time = tk.Scale(f_bot, from_=0.0, to=100.0, resolution=0.1,
                               orient=tk.HORIZONTAL, showvalue=0, command=self.on_seek)
        self.s_time.pack(fill=tk.X)
        self.progress = ttk.Progressbar(f_bot, mode="determinate")
        self.progress.pack(fill=tk.X, pady=5)
        self.progress.bind("<Button-1>", self.on_progress_click)

    def create_tab(self, title, key):
        frame = tk.Frame(self.nb)
        self.nb.add(frame, text=title)
        self.rect_ui[key] = []
        for idx, label in enumerate("XYWH"):
            row = tk.Frame(frame)
            row.pack(fill=tk.X, padx=4, pady=1)
            tk.Label(row, text=label + " %", width=4).pack(side=tk.LEFT)
            scale = tk.Scale(row, from_=0.0, to=100.0, resolution=0.5,
                             orient=tk.HORIZONTAL,
                             command=lambda v, k=key, i=idx: self.on_rect(v, i, k))
            scale.set(self.rect_pct[key][idx])
            scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
            entry = tk.Entry(row, width=6)
            entry.insert(0, "%.1f" % self.rect_pct[key][idx])
            entry.bind("<Return>", lambda _e, k=key, i=idx: self.on_rect_entry(k, i))
            entry.pack(side=tk.LEFT)
            self.rect_ui[key].append((scale, entry))
        if key == "c":
            # 判定选项时要用左边那个 ▶ 圆钮:模板匹配也好、形状判据也好,
            # 都得能在那块区域里找到它。所以这里明确提示一句。
            tk.Label(frame,
                     text="⚠️ 请把左边的 ▶ 箭头按钮也框进蓝框(判定要用它;框宽一点没关系)",
                     fg="#c00000", font=("微软雅黑", 9)).pack(anchor="w", padx=4,
                                                              pady=(3, 0))

    # ---------------- 区域 / 预览 ----------------
    def on_rect(self, value, idx, key):
        try:
            self.rect_pct[key][idx] = float(value)
        except Exception:
            return
        _scale, entry = self.rect_ui[key][idx]
        entry.delete(0, tk.END)
        entry.insert(0, "%.1f" % self.rect_pct[key][idx])
        self.update_preview()

    def on_rect_entry(self, key, idx):
        scale, entry = self.rect_ui[key][idx]
        try:
            value = float(entry.get())
        except Exception:
            entry.delete(0, tk.END)
            entry.insert(0, "%.1f" % self.rect_pct[key][idx])
            return
        value = max(0.0, min(100.0, value))
        self.rect_pct[key][idx] = value
        scale.set(value)
        self.update_preview()

    def on_bin_change(self, _value=None):
        self.update_preview()

    def rect_px_in(self, content, key):
        """按给定的内容区把百分比换成像素(复核别的视频时要用)。"""
        cx, cy, cw, chh = content or (0, 0, 0, 0)
        if cw <= 0 or chh <= 0:
            return [0, 0, 0, 0]
        px, py, pw, ph = self.rect_pct[key]
        return [
            int(cx + cw * px / 100.0),
            int(cy + chh * py / 100.0),
            max(1, int(cw * pw / 100.0)),
            max(1, int(chh * ph / 100.0)),
        ]

    def rect_px(self, key):
        return self.rect_px_in(self.content, key)

    def active_tab(self):
        try:
            return "d" if self.nb.index(self.nb.select()) == 0 else "c"
        except Exception:
            return "d"

    def load_video(self):
        path = filedialog.askopenfilename()
        if not path:
            return
        self.open_video(path)

    def _on_drop_files(self, files):
        """拖进来的文件:第一个认识的视频就打开。"""
        exts = (".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".ts", ".m4v", ".webm")
        for path in files:
            if str(path).lower().endswith(exts):
                self.open_video(path)
                return
        self.log("⚠️ 拖进来的不是认识的视频格式: %s" % (files[0] if files else ""))

    def open_video(self, path):
        if self.is_processing:
            self.log("⚠️ 正在处理中,先按「停止」再换视频")
            return
        self.video_path = path
        if self.cap:
            self.cap.release()
        self.cap = cv2.VideoCapture(path)
        if not self.cap.isOpened():
            self.log("❌ 打不开这个视频: %s" % path)
            self.video_path = ""
            return
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.fps = float(fps) if fps and fps > 0 else 30.0
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        samples = []
        try:
            for frac in (0.02, 0.5, 0.95):
                idx = int(max(0, min(max(0, self.total_frames - 1),
                                      self.total_frames * frac)))
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ok, frame = self.cap.read()
                if ok:
                    samples.append(frame)
        except Exception:
            samples = []
        try:
            self.content = detect_content_area(samples, width, height)
        except Exception:
            self.content = (0, 0, width, height)
        cx, cy, cw, chh = self.content

        duration = (self.total_frames / self.fps) if self.fps > 0 else 0.0
        self.s_time.config(to=max(1.0, duration))
        self.lbl_info.config(text="%s (%dx%d, %.2ffps, %s)" % (
            os.path.basename(path), width, height, self.fps, fmt_timecode(duration)))
        self.lbl_content.config(text="内容区: %d,%d %dx%d" % (cx, cy, cw, chh))
        self.log("📂 已加载: %s" % path)
        self.log("ℹ️ 内容区(去黑边后) = (%d, %d) %d x %d" % (cx, cy, cw, chh))
        low_dir = app_dir().lower()
        if "rar$" in low_dir or "\\temp\\" in low_dir or low_dir.endswith("\\temp"):
            self.log("⚠️ 程序现在跑在临时目录里,参数文件和复核结果可能被清掉")
            self.log("   → 建议把 zip 解压到固定文件夹再运行(例如 D:\\VideoOCR)")
        self.preview_cache = (None, None)
        self.preview_index = 0
        self.s_time.set(0.0)
        self.update_preview(force=True)

    def on_seek(self, _value=None):
        self.update_preview()

    def jump_to_entry(self):
        if not self.cap:
            return
        duration = max(1.0, self.total_frames / self.fps)
        seconds = parse_timecode(self.ent_jump.get(), duration)
        if seconds is None:
            self.log("⚠️ 跳转失败: 看不懂的时间 %s" % self.ent_jump.get())
            return
        self.s_time.set(seconds)
        self.update_preview(force=True)

    def on_progress_click(self, event):
        if not self.cap or self.total_frames <= 0:
            return
        width = max(1, self.progress.winfo_width())
        frac = max(0.0, min(1.0, event.x / float(width)))
        self.s_time.set(frac * (self.total_frames / self.fps))
        self.update_preview(force=True)

    def _grab(self, index):
        """缓存当前帧:拖动滑杆时不再重新 seek(H.264 重新解码就是卡顿的根源)。"""
        cached_idx, cached_img = self.preview_cache
        if cached_img is not None and cached_idx == index:
            return cached_img
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, index)
        ok, frame = self.cap.read()
        if not ok:
            return None
        self.preview_cache = (index, frame)
        return frame

    def update_preview(self, _value=None, force=False):
        if not self.cap or self.is_processing:
            return
        index = int(self.s_time.get() * self.fps)
        top = max(0, self.total_frames - 1)
        index = max(0, min(top, index))
        self.preview_index = index
        frame = self._grab(index)
        if frame is None:
            return
        frame = frame.copy()
        self._draw_overlay(frame, self.active_tab())
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        cw = self.canvas.winfo_width()
        chh = self.canvas.winfo_height()
        if cw > 1 and chh > 1:
            img.thumbnail((cw, chh))
        self.photo = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(cw // 2, chh // 2, image=self.photo, anchor=tk.CENTER)
        self.lbl_time.config(text="%s / %s" % (
            fmt_timecode(index / self.fps),
            fmt_timecode(self.total_frames / self.fps)))

    def _draw_overlay(self, frame, tab):
        dark_on_light = (self.var_mode.get() == "BLACK")
        thr = float(self.s_bin.get())
        cx, cy, cw, chh = self.content
        if cw > 0 and chh > 0:
            cv2.rectangle(frame, (cx, cy), (cx + cw - 1, cy + chh - 1), (90, 90, 90), 1)

        x, y, w, h = self.rect_px(tab)
        if w > 4 and h > 4 and y + h <= frame.shape[0] and x + w <= frame.shape[1]:
            roi = frame[y:y + h, x:x + w]
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            ink = _ink_mask(gray, dark_on_light, thr, self.cfg["local_contrast"])
            ink_bgr = cv2.cvtColor(ink, cv2.COLOR_GRAY2BGR)
            frame[y:y + h, x:x + w] = cv2.addWeighted(roi, 0.35, ink_bgr, 0.65, 0)

        x, y, w, h = self.rect_px("d")
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        x, y, w, h = self.rect_px("c")
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)
        anchor = find_anchor(frame, self.rect_px("c"), self.content, self.cfg)
        if anchor:
            ax, ay, aw, ah = anchor
            cv2.rectangle(frame, (ax, ay), (ax + aw, ay + ah), (0, 165, 255), 2)

    # ---------------- 任务控制 ----------------
    # ---------------- 复核:视频 + SRT → 只报告 / 标记 / 删空行 ----------------
    def open_check_window(self):
        # 已经开着就别再开一个(V17 里连点会开出好几个,自己都找不着)
        try:
            if (getattr(self, "chk_win", None) is not None
                    and self.chk_win.winfo_exists()):
                self.chk_win.deiconify()
                self.chk_win.lift()
                self.chk_win.focus_force()
                return
        except Exception:
            pass
        win = tk.Toplevel(self.root)
        win.title("复核:视频 + SRT")
        win.geometry("790x340")
        self.chk_win = win
        row = tk.Frame(win)
        row.pack(fill=tk.X, padx=10, pady=6)
        tk.Label(row, text="视频:", width=6).pack(side=tk.LEFT)
        self.chk_video = tk.StringVar(value=self.video_path or "")
        tk.Entry(row, textvariable=self.chk_video).pack(side=tk.LEFT, fill=tk.X,
                                                        expand=True)
        tk.Button(row, text="选…", command=lambda: self._pick_file(self.chk_video, False)
                  ).pack(side=tk.LEFT, padx=4)
        row2 = tk.Frame(win)
        row2.pack(fill=tk.X, padx=10, pady=4)
        tk.Label(row2, text="字幕:", width=6).pack(side=tk.LEFT)
        self.chk_srt = tk.StringVar(value="")
        tk.Entry(row2, textvariable=self.chk_srt).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(row2, text="选…", command=lambda: self._pick_file(self.chk_srt, True)
                  ).pack(side=tk.LEFT, padx=4)
        row3 = tk.Frame(win)
        row3.pack(fill=tk.X, padx=10, pady=4)
        tk.Label(row3, text="方式:", width=6).pack(side=tk.LEFT)
        self.chk_mode = tk.StringVar(value="只报告")
        ttk.Combobox(row3, textvariable=self.chk_mode, width=18, state="readonly",
                     values=("只报告", "只报告+标记版SRT", "报告+删掉空行")
                     ).pack(side=tk.LEFT)
        tk.Label(row3, text="　删之前自动存 .bak;带 [Choice] 的行永不删", fg="#666"
                 ).pack(side=tk.LEFT)
        row4 = tk.Frame(win)
        row4.pack(fill=tk.X, padx=10, pady=8)
        tk.Button(row4, text="▶️ 开始复核", command=self.start_check, bg="#ddffdd",
                  font=("微软雅黑", 11, "bold")).pack(side=tk.LEFT)
        self.chk_bar = ttk.Progressbar(row4, mode="determinate")
        self.chk_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        tk.Label(win, justify=tk.LEFT, fg="#555",
                 text=("逐条跳到它自己的时间里抽几帧,看框里到底有没有文字。\n"
                       "判据 = 文字行结构 + 文字坐在气泡底色上 + OCR 读不读得出,三者都否才判可疑。\n"
                       "所以\"画面上有字、只是 OCR 没读出来\"的短句不会被误判。\n"
                       "报告写在字幕旁边:<名字>_check.txt;可疑行的截图在同名 _check 文件夹里。")
                 ).pack(anchor="w", padx=12, pady=4)

    def _pick_file(self, var, is_srt):
        parent = getattr(self, "chk_win", None)
        if is_srt:
            p = filedialog.askopenfilename(
                parent=parent, filetypes=[("字幕", "*.srt"), ("所有", "*.*")])
        else:
            p = filedialog.askopenfilename(parent=parent)
        if p:
            var.set(p)
        # 选完把复核窗口抬回前面(V17 里它会躲到主窗口后面,看着像被关掉了)
        try:
            if parent is not None:
                parent.deiconify()
                parent.lift()
                parent.focus_force()
        except Exception:
            pass

    def _set_check_progress(self, value):
        try:
            self.chk_bar.config(value=value)
        except Exception:
            pass

    def start_check(self):
        if self.is_processing:
            self.log("⚠️ 还有任务在跑,先等它结束或按停止")
            return
        video = (self.chk_video.get() or "").strip()
        srt_path = (self.chk_srt.get() or "").strip()
        if not video or not os.path.exists(video):
            self.log("⚠️ 复核:先选视频")
            return
        if not srt_path:
            guess = os.path.splitext(video)[0] + "_OCR.srt"
            if os.path.exists(guess):
                srt_path = guess
                self.chk_srt.set(guess)
        if not srt_path or not os.path.exists(srt_path):
            self.log("⚠️ 复核:先选字幕(默认会自动找同目录的 <视频名>_OCR.srt)")
            return
        mode = self.chk_mode.get()
        self.is_processing = True
        self.btn_run.config(state=tk.DISABLED, text="处理中...")
        self.btn_stop.config(state=tk.NORMAL)
        self.log("")
        self.log("🔍 === 复核开始(%s)===" % mode)
        threading.Thread(target=self.run_check, args=(video, srt_path, mode),
                         daemon=True).start()

    def run_check(self, video, srt_path, mode):
        try:
            cfg = dict(self.cfg)
            dark_on_light = (self.var_mode.get() == "BLACK")
            thr = float(self.s_bin.get())
            do_ocr = bool(self.var_ocr.get())
            cap = cv2.VideoCapture(video)
            if not cap.isOpened():
                self.log("❌ 复核:打不开视频")
                return
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            fps = float(fps) if fps and fps > 0 else 30.0
            w0 = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h0 = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            samples = []
            for frac in (0.02, 0.5, 0.95):
                f = grab_frame(cap, max(0, total * frac))
                if f is not None:
                    samples.append(f)
            try:
                content = detect_content_area(samples, w0, h0)
            except Exception:
                content = (0, 0, w0, h0)
            content_h = content[3]
            xd, yd, wd, hd = self.rect_px_in(content, "d")
            xc2, yc2, wc2, hc2 = self.rect_px_in(content, "c")
            self.log("ℹ️ 复核:内容区 %s,对话框 %s,选项框 %s"
                     % (content, [xd, yd, wd, hd], [xc2, yc2, wc2, hc2]))
            with open(srt_path, "r", encoding="utf-8-sig") as fp:
                subs = list(srt.parse(fp.read()))
            self.log("ℹ️ 复核:字幕 %d 条" % len(subs))
            base = os.path.splitext(srt_path)[0]
            shot_dir = base + "_check"
            report_path = base + "_check.txt"
            try:
                os.makedirs(shot_dir, exist_ok=True)
            except Exception:
                pass
            marks = cfg["check_mark"]
            fracs = (0.35, 0.55, 0.75, 0.9)[:max(1, int(cfg["check_frames"]))]
            # 复核用的判据要比打轴松一点:打轴要求"≥3 个字"是为了不误触发,
            # 但复核是在判断"这条到底有没有字",两个字的气泡(比如「嗯?」)
            # 也必须算有字 —— V17 用同一套严格判据,把它们当空行删掉了。
            chk_cfg = dict(cfg)
            chk_cfg["min_glyphs"] = max(1, int(cfg["check_min_glyphs"]))
            chk_cfg["row_span_min_ratio"] = float(cfg["check_span_ratio"])
            rows = []
            for i, sub in enumerate(subs):
                if not self.is_processing:
                    self.log("⚠️ 复核被停止(已做 %d/%d 条)" % (i, len(subs)))
                    break
                if i % 5 == 0:
                    pct = (i * 100.0) / max(1, len(subs))
                    self.root.after(0, lambda v=pct: self._set_check_progress(v))
                t0 = sub.start.total_seconds()
                t1 = sub.end.total_seconds()
                text = (sub.content or "").strip()
                # 选项行要拿"选项框"去核,不能用对话框的框 ——
                # 否则周围的对话会替它作证,V17 里 12 条假选项只揪出 1 条就是这个原因
                if "[Choice]" in text:
                    x, y, w, h = xc2, yc2, wc2, hc2
                else:
                    x, y, w, h = xd, yd, wd, hd
                hit = 0
                tried = 0
                ocr_text = ""
                shot = None
                for frac in fracs:
                    frame = grab_frame(cap, (t0 + (t1 - t0) * frac) * fps)
                    if frame is None:
                        continue
                    if y + h > frame.shape[0] or x + w > frame.shape[1]:
                        continue
                    roi = frame[y:y + h, x:x + w]
                    if roi.size == 0:
                        continue
                    tried += 1
                    if shot is None:
                        shot = roi.copy()
                    info = analyze_text(roi, dark_on_light, thr, content_h, chk_cfg)
                    if info and info.get("ok"):
                        hit += 1
                    elif do_ocr and tried <= int(cfg["check_ocr_frames"]):
                        txt = self.processor.ocr_image(prepare_ocr_image(roi, cfg))
                        if txt and len(txt.strip()) >= 2 and len(txt) > len(ocr_text):
                            ocr_text = txt.strip()
                dur_line = max(0.0, t1 - t0)
                too_short = dur_line < float(cfg["check_min_seconds"])
                rows.append({"n": i + 1, "t0": t0, "t1": t1, "text": text,
                             "choice": "[Choice]" in text,
                             "short": too_short,
                             # 太短的行证据不足,一律不删(宁可留给你手看)
                             "alive": (hit > 0) or bool(ocr_text) or too_short,
                             "hit": hit, "tried": tried, "ocr": ocr_text, "shot": shot})
            dead = [r for r in rows if not r["alive"]]
            dead_dialog = [r for r in dead if not r["choice"]]
            dead_choice = [r for r in dead if r["choice"]]
            saved = 0
            for r in dead_dialog:
                if r["shot"] is None:
                    continue
                name = "C%04d_%s.jpg" % (r["n"], fmt_timecode(r["t0"]).replace(":", "-"))
                if write_image_unicode(os.path.join(shot_dir, name), r["shot"]):
                    saved += 1
            try:
                with open(report_path, "w", encoding="utf-8-sig") as fp:
                    fp.write("复核报告 %s\n" % APP_VERSION)
                    fp.write("视频: %s\n字幕: %s\n" % (video, srt_path))
                    fp.write("内容区 %s / 对话框 %s / 阈值 %d / 判定=%s\n"
                             % (content, [xd, yd, wd, hd], int(thr),
                                self.var_detect.get()))
                    fp.write("共 %d 条,可疑 %d 条(对话框轨 %d / 选项轨 %d),存图 %d 张\n"
                             % (len(rows), len(dead), len(dead_dialog), len(dead_choice),
                                saved))
                    fp.write("=" * 78 + "\n【A. 建议删掉的空行(对话框轨)】\n")
                    for r in dead_dialog:
                        fp.write("#%-5d %s-%s  抽%d帧没文字  %s\n"
                                 % (r["n"], fmt_timecode(r["t0"]), fmt_timecode(r["t1"]),
                                    r["tried"], r["text"][:40]))
                    fp.write("\n【B. 可疑的选项行(不删,自己看一眼)】\n")
                    for r in dead_choice:
                        fp.write("#%-5d %s-%s  抽%d帧没文字  %s\n"
                                 % (r["n"], fmt_timecode(r["t0"]), fmt_timecode(r["t1"]),
                                    r["tried"], r["text"][:40]))
                    fp.write("\n【C. 画面上有字但字幕是空的(OCR 没读出来,建议手补)】\n")
                    for r in rows:
                        if r["alive"] and not r["text"]:
                            fp.write("#%-5d %s-%s  结构命中 %d 帧  OCR:%s\n"
                                     % (r["n"], fmt_timecode(r["t0"]),
                                        fmt_timecode(r["t1"]), r["hit"],
                                        (r["ocr"] or "无")[:24]))
                    fp.write("\n【D. 太短没敢删的(证据不足,自己看一眼)】\n")
                    for r in rows:
                        if r["short"]:
                            fp.write("#%-5d %s-%s  %.2fs  %s\n"
                                     % (r["n"], fmt_timecode(r["t0"]),
                                        fmt_timecode(r["t1"]), r["t1"] - r["t0"],
                                        r["text"][:40]))
            except Exception as exc:
                self.log("⚠️ 复核报告写入失败: %s" % exc)
            self.log("🔍 复核结束: 共 %d 条,可疑 %d 条(对话框 %d / 选项 %d),报告 %s"
                     % (len(rows), len(dead), len(dead_dialog), len(dead_choice),
                        report_path))
            if len(rows) != len(subs):
                self.log("ℹ️ 被中途停止,没动 SRT 文件(只出了报告)")
                return
            if mode.startswith("只报告+标记"):
                marked = base + "_check.srt"
                out = []
                for sub, r in zip(subs, rows):
                    c = sub.content
                    if (not r["alive"]) and (not r["choice"]):
                        c = marks + " " + c
                    out.append(srt.Subtitle(index=len(out) + 1, start=sub.start,
                                            end=sub.end, content=c))
                with open(marked, "w", encoding="utf-8-sig") as fp:
                    fp.write(srt.compose(out))
                self.log("📝 已另存标记版: %s(可疑行前面加了 %s)" % (marked, marks))
            if mode.startswith("报告+删掉"):
                drop = set(r["n"] for r in dead_dialog)
                keep = []
                for sub, r in zip(subs, rows):
                    if r["n"] in drop:
                        continue
                    keep.append(srt.Subtitle(index=len(keep) + 1, start=sub.start,
                                             end=sub.end, content=sub.content))
                try:
                    with open(srt_path, "rb") as a, open(srt_path + ".bak", "wb") as b:
                        b.write(a.read())
                    with open(srt_path, "w", encoding="utf-8-sig") as fp:
                        fp.write(srt.compose(keep))
                    self.log("🧹 删掉 %d 条空行,原文件备份为 %s.bak" % (len(drop), srt_path))
                except Exception as exc:
                    self.log("⚠️ 删除失败(原文件没动): %s" % exc)
            self.root.after(0, lambda: self._set_check_progress(100))
            self.log("✅ 复核完成(报告 %s)" % report_path)
            self.root.after(0, lambda n=len(rows), d=len(dead), dd=len(dead_dialog),
                            dc=len(dead_choice), rp=report_path:
                            messagebox.showinfo(
                                "复核完成",
                                "共 %d 条,可疑 %d 条(对话框 %d / 选项 %d)\n报告:\n%s"
                                % (n, d, dd, dc, rp)))
        except Exception as exc:
            self.log("❌ 复核出错: %s" % exc)
            self.log(traceback.format_exc())
        finally:
            self.is_processing = False
            self.root.after(0, lambda: self.btn_run.config(state=tk.NORMAL,
                                                           text="▶️ 开始处理"))
            self.root.after(0, lambda: self.btn_stop.config(state=tk.DISABLED))

    def stop_task(self):
        self.is_processing = False
        self.log("⚠️ 收到停止指令，正在安全退出...")

    def start_task(self):
        if not self.video_path:
            return
        self.is_processing = True
        self.btn_run.config(state=tk.DISABLED, text="处理中...")
        self.btn_stop.config(state=tk.NORMAL)
        self.log("")
        self.log("🚀 === %s 开始提取  %s ===" % (APP_VERSION,
                                                 time.strftime("%Y-%m-%d %H:%M:%S")))
        threading.Thread(target=self.run_process, daemon=True).start()

    # ---------------- 以下为主流程与复核 ----------------

    def run_process(self):
        cfg = dict(self.cfg)
        try:
            rect_d = self.rect_px("d")
            rect_c = self.rect_px("c")
            content = self.content
            content_h = content[3]
            dark_on_light = (self.var_mode.get() == "BLACK")
            thr = float(self.s_bin.get())
            p_diff = float(self.s_diff.get()) / 100.0
            do_ocr = bool(self.var_ocr.get())
            detect_mode = self.var_detect.get()
            use_bubble = detect_mode.startswith("泡泡")
            use_structure = (not use_bubble) and detect_mode.startswith("结构")
            review_mode = {"关闭": "off", "只报告": "report",
                           "报告并删除": "report+delete"}.get(
                               self.var_review.get(), "report")
            verbose = bool(self.var_verbose.get())
            require_anchor = dark_on_light or bool(cfg["require_anchor_in_white_mode"])
            use_choice_track = bool(self.var_choice.get())
            c_anchor_tpl = load_anchor_template()
            self.log("ℹ️ 圆钮: %s" % ("模板匹配(已载入 anchor_template.png)"
                                     if c_anchor_tpl is not None
                                     else "形状判据(没找到 anchor_template.png)"))
            drop_unreadable_choice = bool(cfg.get("drop_unreadable_choice", True))

            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                self.log("❌ 打不开视频(确认文件没被别的程序占用): %s" % self.video_path)
                return
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = self.fps if self.fps > 0 else 30.0
            # 帧数和时间的关系跟帧率有关:60fps 下"2 帧"只有 33ms,所以统一按秒换算,
            # 否则 60fps 的素材会被切得比 30fps 碎很多。
            f_miss = max(2, int(round(cfg["miss_seconds_to_cut"] * fps)))
            f_still = max(3, int(round(cfg["choice_still_seconds"] * fps)))
            f_absent = max(3, int(round(cfg["choice_absent_seconds"] * fps)))
            self.log("ℹ️ 帧率 %.2ffps → 连丢 %d 帧算一句结束 / 静止 %d 帧上锁 / 消失 %d 帧结算"
                     % (fps, f_miss, f_still, f_absent))
            recs = []
            retry_list = []
            base = os.path.splitext(self.video_path)[0]
            fail_dir = os.path.join(base + "_review", "ocr_fail")
            fail_count = [0]
            err_logged = [0]
            self.log("ℹ️ 对话框(像素) %s / 选项框(像素) %s" % (rect_d, rect_c))
            self.log("ℹ️ 判定=%s 阈值=%d 防连读=%.1f OCR=%s" % (
                self.var_detect.get(), int(thr), self.s_diff.get(), "开" if do_ocr else "关"))

            def ocr_of(roi, info, fallback, prefer):
                """给 OCR 的图,按 prefer 决定先试哪个。

                对话框 prefer="roi":V12 一直把整个框喂给 OCR(你那边 95% 能读出来);
                紧缩图实测会把一句话裁掉一截(比如"誰もいないコース。消え"这种),
                所以整个框优先,紧缩图只当备胎。
                选项框 prefer="tight":紧缩图正好把左边那个圆钮排除在外,
                免得被识别成怪字;读不出再退回整个框。
                两个都不行就把图存到 _review/ocr_fail/,方便回头看是什么样。
                """
                if not do_ocr or roi is None or roi.size == 0:
                    return False, fallback, roi
                tight = tight_crop(roi, info, cfg)
                if prefer == "tight":
                    cands = [("tight", tight), ("roi", roi)]
                else:
                    cands = [("roi", roi), ("tight", tight)]
                tried = []
                for tag, cand in cands:
                    if cand is None or getattr(cand, "size", 0) == 0:
                        continue
                    shape = (int(cand.shape[0]), int(cand.shape[1]))
                    if shape in tried:
                        continue          # 整个框和紧缩图一样大时不用试两遍
                    tried.append(shape)
                    text = self.processor.ocr_image(prepare_ocr_image(cand, cfg))
                    if text and len(text.strip()) >= 2:
                        if verbose:
                            self.log("   ✎ OCR(%s %dx%d): %s" % (
                                tag, shape[1], shape[0], text.strip()[:36]))
                        return True, text.strip(), cand
                    if self.processor.last_error and err_logged[0] < 8:
                        err_logged[0] += 1
                        self.log("⚠️ OCR没读出(%s, %dx%d): %s" % (
                            tag, shape[1], shape[0], self.processor.last_error))
                if (cfg.get("save_failed_crops", True)
                        and fail_count[0] < int(cfg.get("save_failed_crops_max", 40))):
                    fail_count[0] += 1
                    shot = tight if (tight is not None and tight.size) else roi
                    try:
                        os.makedirs(fail_dir, exist_ok=True)
                        write_image_unicode(
                            os.path.join(fail_dir, "fail%03d.jpg" % fail_count[0]), shot)
                    except Exception:
                        pass
                return False, fallback, roi

            # 对话轨状态
            d_active = False
            d_start = 0
            d_peak = 0.0
            d_miss = 0
            d_glyph_max = 0
            d_best_density = 0.0
            d_best_roi = None
            d_best_info = None
            d_mask_prev = None
            d_prev_density = 0.0
            d_stable = 99

            # 选项轨状态
            c_active = False
            c_start = 0
            c_empty = 0
            c_locked = False
            c_still = 0
            c_glyph_max = 0
            c_best_density = 0.0
            c_best_roi = None
            c_best_info = None
            c_fallback_roi = None
            c_fallback_info = None
            c_text = None
            c_text_roi = None
            c_text_info = None
            c_tries = 0
            c_mask_prev = None
            c_anchor_seen = False
            c_anchor_cache = None
            c_last_bubble_ok = False

            anchor_every = max(1, int(cfg.get("anchor_every", 3)))
            t_start = time.time()
            idx = 0
            while self.is_processing:
                ok, frame = cap.read()
                if not ok:
                    break
                if total > 0 and idx % 60 == 0:
                    prog = (idx / float(total)) * 100.0
                    self.root.after(0, lambda v=prog: self.progress.config(value=v))
                if verbose and total > 0 and idx > 0 and idx % 300 == 0:
                    # 挂机跑长片时,能看一眼"还要多久"很重要
                    elapsed = max(0.001, time.time() - t_start)
                    rate = idx / elapsed
                    left = (total - idx) / rate if rate > 0 else 0.0
                    self.log("⏱ %5.1f%%  %.0f 帧/秒  已跑 %.1f 分  预计剩余 %.1f 分"
                             % (idx * 100.0 / total, rate, elapsed / 60.0,
                                left / 60.0))

                # ---------- 对话轨 ----------
                x, y, w, h = rect_d
                d_info = None
                roi_d = None
                if (w > 1 and h > 1 and y + h <= frame.shape[0]
                        and x + w <= frame.shape[1]):
                    roi_d = frame[y:y + h, x:x + w]
                    if use_bubble:
                        d_info = bubble_density(roi_d, dark_on_light, thr, cfg,
                                                d_mask_prev)
                    elif use_structure:
                        d_info = analyze_text_auto(roi_d, dark_on_light, thr,
                                                   content_h, cfg, d_mask_prev)
                    else:
                        d_info = legacy_density(roi_d, dark_on_light, thr, cfg,
                                                d_mask_prev)
                    if d_info is not None:
                        d_mask_prev = d_info["mask"].copy()

                if d_info is not None:
                    has_text = bool(d_info["ok"])
                    density = d_info["ink_density"]
                    diff_score = d_info["diff_score"]
                    if not d_active:
                        if has_text and density >= cfg["text_start_density"]:
                            d_active = True
                            d_start = idx
                            d_peak = density
                            d_miss = 0
                            d_glyph_max = d_info["nglyph"]
                            d_best_density = density
                            d_best_roi = roi_d.copy()
                            d_best_info = d_info
                            d_prev_density = density
                            d_stable = 0
                    else:
                        if has_text:
                            d_miss = 0
                            d_peak = max(d_peak, density)
                            if density > d_best_density + 0.001:
                                d_best_density = density
                                d_best_roi = roi_d.copy()
                                d_best_info = d_info
                            d_glyph_max = max(d_glyph_max, d_info["nglyph"])
                        else:
                            d_miss += 1

                        should_cut = False
                        if d_miss >= f_miss:
                            should_cut = True
                        elif density < max(cfg["cut_abs_floor"],
                                           d_peak * cfg["cut_peak_ratio"]):
                            should_cut = True
                        elif (has_text and diff_score > p_diff
                              and d_stable >= int(cfg["motion_cut_stable_frames"])
                              and (idx - d_start) / fps > cfg["motion_cut_after"]):
                            should_cut = True

                        # 打字机效果会让墨水一路变多,那时候不是"换句",不能切。
                        # 连续若干帧墨水不再增长,才允许按"画面变化"切断。
                        if density > d_prev_density + 0.0005:
                            d_stable = 0
                        else:
                            d_stable += 1
                        d_prev_density = density

                        if should_cut:
                            dur = (idx - d_start) / fps
                            if dur > cfg["min_dur_dialog"]:
                                st = datetime.timedelta(seconds=d_start / fps)
                                et = datetime.timedelta(seconds=idx / fps)
                                ocr_ok, content_d, used_d = ocr_of(
                                    d_best_roi, d_best_info, "Line [Dialog]", "roi")
                                rec = Rec(st, et, content_d, "dialog")
                                rec.crop = used_d
                                rec.nglyph = d_glyph_max
                                rec.ocr_ok = ocr_ok
                                rec.i0, rec.i1 = d_start, idx
                                if not ocr_ok:
                                    # 这句的"墨水最多那一帧"可能是空气泡(实测有这种情况),
                                    # 等扫描结束后在它的时间范围内换几帧重试 OCR
                                    retry_list.append((rec, [x, y, w, h],
                                                       d_start / fps, idx / fps))
                                prev = recs[-1] if recs else None
                                same = (prev is not None and ocr_ok and prev.ocr_ok
                                        and prev.kind == "dialog"
                                        and (prev.content == content_d
                                             or similar_prefix(prev.content, content_d,
                                                                cfg["merge_prefix_ratio"]))
                                        and 0 <= (d_start - prev.i1) <= int(fps * 3))
                                if same:
                                    prev.et = et
                                    prev.i1 = idx
                                    if len(content_d) > len(prev.content):
                                        prev.content = content_d   # 打字机:留最完整那句
                                        prev.crop = rec.crop
                                    self.log("🔄 缝合对话碎片: %s..." % prev.content[:12])
                                else:
                                    recs.append(rec)
                                    self.log("✅ 对话: %s..." % content_d[:15])
                                if verbose:
                                    self.log("   └ idx=%d 时长=%.2fs 墨水=%.3f 峰值=%.3f 字形=%d"
                                             % (idx, dur, density, d_peak, d_glyph_max))
                            if has_text and density >= cfg["text_start_density"]:
                                d_active = True
                                d_start = idx
                                d_peak = density
                                d_miss = 0
                                d_glyph_max = d_info["nglyph"]
                                d_best_density = density
                                d_best_roi = roi_d.copy()
                                d_best_info = d_info
                                d_prev_density = density
                                d_stable = 0
                            else:
                                d_active = False
                                d_peak = 0.0
                                d_glyph_max = 0
                                d_best_density = 0.0
                                d_best_roi = None
                                d_best_info = None

                # ---------- 选项轨 ----------
                xc, yc, wc, hc = rect_c
                if not use_choice_track:
                    xc = yc = wc = hc = 0          # 关掉选项轨:整段跳过
                c_info = None
                roi_c = None
                anchor = None
                if (wc > 1 and hc > 1 and yc + hc <= frame.shape[0]
                        and xc + wc <= frame.shape[1]):
                    roi_c = frame[yc:yc + hc, xc:xc + wc]
                    if require_anchor:
                        # 圆钮是静止的,不用每帧都找:每 anchor_every 帧一次,中间帧沿用上次结果。
                        # 有模板时只在"上一帧泡泡判定通过"的帧才去匹配(匹配偏贵),
                        # 平时根本不会走到这里。
                        if c_anchor_cache is None or idx % anchor_every == 0:
                            if (c_anchor_tpl is None or c_last_bubble_ok
                                    or c_anchor_cache is None):
                                if c_anchor_tpl is not None:
                                    c_anchor_cache, tpl_score = find_anchor_tpl(
                                        frame, rect_c, content, cfg, c_anchor_tpl)
                                    if verbose and tpl_score and idx % 600 == 0:
                                        self.log("   🔍 模板匹配最高分 %.2f" % tpl_score)
                                else:
                                    c_anchor_cache = find_anchor(frame, rect_c, content,
                                                                 cfg)
                        anchor = c_anchor_cache
                    # 选项轨一律用结构判据,不跟着"判定"下拉框走。
                    # V17 把它跟着改成"墨水判定"之后,选项段在花花绿绿的背景上
                    # 永远关不掉 —— 实测出现过 97 秒、60 秒这种假选项段。
                    if use_bubble:
                        c_info = bubble_density(roi_c, dark_on_light, thr, cfg,
                                                c_mask_prev)
                    elif use_structure or cfg.get("choice_use_structure", True):
                        c_info = analyze_text_auto(roi_c, dark_on_light, thr,
                                                   content_h, cfg, c_mask_prev)
                    else:
                        c_info = legacy_density(roi_c, dark_on_light, thr, cfg,
                                                c_mask_prev)
                    if c_info is not None:
                        c_mask_prev = c_info["mask"].copy()
                        c_last_bubble_ok = bool(c_info["ok"])
                    if anchor is not None:
                        c_anchor_seen = True

                if c_info is not None:
                    density_c = c_info["ink_density"]
                    diff_c = c_info["diff_score"]
                    anchor_ok = (not require_anchor) or (anchor is not None)
                    if use_bubble:
                        # 泡泡判定下:平整浅色泡泡 + 有墨水,再加上"圆钮 或 文字行"
                        # 之一(天空也平整,但它既没圆钮也没字形,所以挡得住)
                        is_choice = (bool(c_info["ok"])
                                     and density_c >= cfg["choice_start_density"])
                        if is_choice and anchor is None:
                            text_row = analyze_text_auto(roi_c, dark_on_light, thr,
                                                         content_h, cfg, None)
                            is_choice = bool(text_row and text_row["ok"])
                    else:
                        is_choice = (bool(c_info["ok"]) and anchor_ok
                                     and density_c >= cfg["choice_start_density"])

                    if not c_active:
                        if is_choice:
                            c_active = True
                            c_start = idx
                            c_empty = 0
                            c_locked = False
                            c_still = 0
                            c_glyph_max = c_info["nglyph"]
                            c_best_density = density_c
                            c_best_roi = None
                            c_best_info = None
                            c_fallback_roi = roi_c.copy()
                            c_fallback_info = c_info
                            c_text = None
                            c_text_roi = None
                            c_text_info = None
                            c_tries = 0
                            c_anchor_seen = anchor is not None
                    else:
                        # "选项还在" = 框里有文字行 且 圆钮还在;超过保险丝时长也算它消失
                        visible = (is_choice
                                   and (not require_anchor or anchor is not None))
                        if (idx - c_start) / fps > cfg["choice_max_seconds"]:
                            visible = False
                            if verbose and idx % 60 == 0:
                                self.log("   ✂ 选项段超过 %.0f 秒,强制结算"
                                         % cfg["choice_max_seconds"])
                        if visible:
                            c_empty = 0
                            c_glyph_max = max(c_glyph_max, c_info["nglyph"])
                            # 备用帧固定用"第一次通过判定的那一帧"(激活时记下的),
                            # 不再按墨水最多去换 —— 按下选项时框会膨胀,那一帧字最大、
                            # 墨水最多,但 OCR 读出来不是日文。
                            if not c_locked:
                                if diff_c < cfg["still_diff"]:
                                    c_still += 1
                                    if (c_still >= f_still
                                            and c_tries < int(cfg["choice_max_tries"])):
                                        c_tries += 1
                                        # 锁定的同时立刻试一次 OCR:认不出字就说明这里不是真选项
                                        # (立绘的头发/护目镜、糖果装饰、黑影人物都能骗过前面几道
                                        # 判定,但都读不出文字),那就先不锁,等下一个静止瞬间再试。
                                        ok_now, text_now, roi_now = ocr_of(
                                            roi_c, c_info, "", "tight")
                                        if ok_now:
                                            c_best_roi = roi_c.copy()
                                            c_best_info = c_info
                                            c_text = text_now
                                            c_text_roi = roi_now
                                            c_text_info = c_info
                                            c_locked = True
                                            # 选项真正出现的时刻是这个静止窗口的开头,
                                            # 不是这段(可能被误判)开始的时候
                                            c_start = max(c_start, idx - f_still)
                                            self.log("📸[选项快门] 锁定并读出: %s"
                                                     % text_now[:20])
                                        else:
                                            c_still = 0
                                            if verbose:
                                                self.log("   ⏳ 静止了但读不出字,继续等"
                                                         "(第 %d 次尝试)" % c_tries)
                                else:
                                    c_still = 0
                        else:
                            c_empty += 1
                            if c_empty > f_absent:
                                c_active = False
                                real_end = max(c_start, idx - f_absent)
                                dur_c = (real_end - c_start) / fps
                                if dur_c > cfg["min_dur_choice"]:
                                    st_c = datetime.timedelta(seconds=c_start / fps)
                                    et_c = datetime.timedelta(seconds=real_end / fps)
                                    text_c = c_text
                                    used_c = c_text_roi
                                    if not text_c:
                                        # 整段都没锁上:拿"墨水最多那一帧"再试最后一次
                                        ok_last, text_last, roi_last = ocr_of(
                                            c_fallback_roi, c_fallback_info, "", "tight")
                                        if ok_last:
                                            text_c = text_last
                                            used_c = roi_last
                                    if (text_c and jp_char_count(text_c)
                                            < int(cfg["choice_min_jp_chars"])):
                                        if verbose:
                                            self.log("   ⚠️ 选项文字不像日语,当没读出: %r"
                                                     % text_c[:16])
                                        text_c = None
                                    if text_c:
                                        content_c = "%s [Choice]" % text_c
                                        ocr_ok_c = True
                                    else:
                                        content_c = "Line [Choice]"
                                        ocr_ok_c = False
                                    if (not ocr_ok_c) and drop_unreadable_choice:
                                        # 真选项一定有字;读不出字的这一整段基本都是立绘/背景
                                        # 装饰骗过判定,直接丢掉,不再产出 Line N [Choice]
                                        self.log("🗑️ 丢弃读不出文字的选项段(%.2fs,圆钮=%s)"
                                                 % (dur_c, "有" if c_anchor_seen else "无"))
                                    else:
                                        rec = Rec(st_c, et_c, content_c, "choice")
                                        rec.crop = used_c
                                        rec.nglyph = c_glyph_max
                                        rec.ocr_ok = ocr_ok_c
                                        rec.anchor = c_anchor_seen
                                        rec.i0, rec.i1 = c_start, real_end
                                        prev = recs[-1] if recs else None
                                        if (prev is not None and ocr_ok_c and prev.ocr_ok
                                                and prev.content == content_c
                                                and 0 <= (c_start - prev.i1) <= int(fps * 3)):
                                            prev.et = et_c
                                            prev.i1 = real_end
                                            self.log("🔄 缝合选项碎片: %s..."
                                                     % content_c[:10])
                                        else:
                                            recs.append(rec)
                                            self.log("🔹 选项结算: %s..." % content_c[:15])
                                        if verbose:
                                            self.log("   └ idx=%d 时长=%.2fs 锁=%s 字形=%d "
                                                     "圆钮=%s"
                                                     % (idx, dur_c,
                                                        "是" if c_locked else "否",
                                                        c_glyph_max,
                                                        "有" if c_anchor_seen else "无"))
                idx += 1

            # ---- 对话轨 OCR 补救:扫描结束后再补救那些读不出文字的句子 ----
            if (do_ocr and retry_list and cfg.get("retry_ocr_frames", 0) > 0
                    and self.is_processing):
                self.log("🔁 OCR 补救: %d 句要重试" % len(retry_list))
                fixed = 0
                tries = (0.5, 0.75, 0.9, 0.3)[:max(1, int(cfg["retry_ocr_frames"]))]
                for rec, rect, t0, t1 in retry_list:
                    if not self.is_processing:
                        break
                    rx, ry, rw, rh = rect
                    best = ""
                    for frac in tries:
                        frame = grab_frame(cap, (t0 + (t1 - t0) * frac) * fps)
                        if frame is None:
                            continue
                        if ry + rh > frame.shape[0] or rx + rw > frame.shape[1]:
                            continue
                        roi = frame[ry:ry + rh, rx:rx + rw]
                        if roi.size == 0:
                            continue
                        txt = self.processor.ocr_image(prepare_ocr_image(roi, cfg))
                        if txt and len(txt.strip()) >= 2 and len(txt.strip()) > len(best):
                            best = txt.strip()
                            rec.crop = roi.copy()
                        if len(best) >= 8:
                            break
                    if best:
                        rec.content = best
                        rec.ocr_ok = True
                        fixed += 1
                        self.log("   ✔ 补回: %s" % best[:26])
                self.log("🔁 补救完成: 补回 %d 句" % fixed)

            cap.release()
            if total > 0:
                self.root.after(0, lambda: self.progress.config(value=100.0))

            recs.sort(key=lambda r: r.st)
            for i, rec in enumerate(recs):
                if rec.content == "Line [Dialog]":
                    rec.content = "Line %d" % (i + 1)
                elif rec.content == "Line [Choice]":
                    rec.content = "Line %d [Choice]" % (i + 1)
            subs = [srt.Subtitle(index=i + 1, start=r.st, end=r.et, content=r.content)
                    for i, r in enumerate(recs)]

            base = os.path.splitext(self.video_path)[0]
            srt_path = base + ("_OCR.srt" if do_ocr else ".srt")
            with open(srt_path, "w", encoding="utf-8-sig") as fp:
                fp.write(srt.compose(subs))
            self.log("💾 已写入: %s（共 %d 条, 耗时 %.1f 分钟）"
                     % (srt_path, len(subs), (time.time() - t_start) / 60.0))

            if review_mode == "off":
                self.log("ℹ️ 复核已关闭")
            else:
                self.run_review(recs, base, srt_path, dark_on_light, thr,
                                content_h, cfg, review_mode)

            if self.is_processing:
                self.root.after(0, lambda p=srt_path: messagebox.showinfo(
                    "完成", "任务结束。\n文件已保存至:\n%s" % p))
        except Exception as exc:
            self.log("❌ [致命错误] %s" % exc)
            self.log(traceback.format_exc())
        finally:
            self.is_processing = False
            self.root.after(0, lambda: self.btn_run.config(state=tk.NORMAL,
                                                           text="▶️ 开始处理"))
            self.root.after(0, lambda: self.btn_stop.config(state=tk.DISABLED))

    def run_review(self, recs, base, srt_path, dark_on_light, thr, content_h,
                   cfg, review_mode):
        """对第一遍留下的候选帧再用更严格的判据看一遍。

        严格判据 = 多要一个字 + 打开宽度变异检查(防书架/栅栏那种整齐排列)。
        默认只报告;选 report+delete 才删除"严格判据认不出文字且 OCR 也没文本"的行。
        """
        strict = dict(cfg)
        strict["min_glyphs"] = int(cfg["min_glyphs"]) + 1
        strict["glyph_width_cv_min"] = max(0.18, float(cfg.get("glyph_width_cv_min", 0)))
        strict["try_opposite_polarity"] = False

        review_dir = base + "_review"
        report_path = base + "_review.txt"
        rows = []
        for i, rec in enumerate(recs):
            reasons = []
            strong = False
            if rec.crop is not None and getattr(rec.crop, "size", 0):
                info = analyze_text(rec.crop, dark_on_light, thr, content_h, strict)
                strong = bool(info and info["ok"])
            if not strong:
                reasons.append("严格判据无文字")
            if not rec.ocr_ok:
                reasons.append("OCR无文本")
            if rec.kind == "choice" and not rec.anchor:
                reasons.append("未见圆钮")
            rec.reason = reasons
            rows.append((i + 1, rec, strong))

        suspicious = [r for r in rows if r[1].reason]
        try:
            os.makedirs(review_dir, exist_ok=True)
        except Exception:
            pass
        saved = 0
        for number, rec, _strong in suspicious:
            if rec.crop is None or not getattr(rec.crop, "size", 0):
                continue
            name = "L%04d_%s.jpg" % (number, str(rec.st).replace(":", "-"))
            if write_image_unicode(os.path.join(review_dir, name), rec.crop):
                saved += 1

        try:
            with open(report_path, "w", encoding="utf-8-sig") as fp:
                fp.write("复核报告  构建 %s (%s)\n" % (APP_VERSION, BUILD_DATE))
                fp.write("共 %d 条,可疑 %d 条,存图 %d 张 -> %s\n" % (
                    len(recs), len(suspicious), saved, review_dir))
                fp.write("=" * 78 + "\n")
                fp.write("列: 序号 判定 起 止 原因 内容\n")
                for number, rec, strong in suspicious:
                    fp.write("#%-5d %s  %s -> %s  [%s]  %s\n" % (
                        number, "强" if strong else "弱", str(rec.st), str(rec.et),
                        ",".join(rec.reason), rec.content[:40]))
        except Exception as exc:
            self.log("⚠️ 复核报告写入失败: %s" % exc)
            return

        self.log("🔍 复核: 可疑 %d/%d 条,报告 %s" % (
            len(suspicious), len(recs), report_path))
        for number, rec, _strong in suspicious[:40]:
            self.log("   · #%d %s [%s] %s" % (
                number, rec.content[:20], ",".join(rec.reason), str(rec.st)))

        if review_mode != "report+delete":
            return
        keep = []
        deleted = 0
        for _number, rec, strong in rows:
            if (not strong) and (not rec.ocr_ok):
                deleted += 1
            else:
                keep.append(rec)
        if not deleted:
            self.log("🧹 没有需要删除的行")
            return
        try:
            with open(srt_path, "rb") as src, open(srt_path + ".bak", "wb") as dst:
                dst.write(src.read())
            subs = [srt.Subtitle(index=i + 1, start=r.st, end=r.et, content=r.content)
                    for i, r in enumerate(keep)]
            with open(srt_path, "w", encoding="utf-8-sig") as fp:
                fp.write(srt.compose(subs))
            self.log("🧹 已删除 %d 条空行，原文件备份为 %s.bak" % (deleted, srt_path))
        except Exception as exc:
            self.log("⚠️ 自动删除失败(原文件未改动): %s" % exc)


def main():
    cfg = load_config()
    root = tk.Tk()
    App(root, cfg)
    root.mainloop()


if __name__ == "__main__":
    main()
