"""AstroDX Skin Developer Tool

把 Hold 九宫格拉伸、skin.json 验证/生成、颜色变体生成、PPU 计算和配色方案生成整合到一个 Tkinter App。
依赖：pip install Pillow
运行：python adx_skin_devtool.py
"""

from __future__ import annotations

import colorsys
import json
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from PIL import Image, ImageDraw, ImageTk


APP_NAME = "AstroDX Skin Developer Tool"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp"}
DEFAULT_LANG = "zh"

SPRITE_DEFAULTS: dict[str, dict] = {
    "ring": {"path": "ring.png", "ppu": 115},
    "tap": {"path": "tap.png"},
    "tap_each": {"path": "tap_each.png"},
    "tap_break": {"path": "tap_break.png"},
    "tap_mine": {"path": "tap_mine.png"},
    "star": {"path": "star.png"},
    "star_each": {"path": "star_each.png"},
    "star_break": {"path": "star_break.png"},
    "star_mine": {"path": "star_mine.png"},
    "hold": {"path": "hold.png"},
    "hold_each": {"path": "hold_each.png"},
    "hold_break": {"path": "hold_break.png"},
    "hold_mine": {"path": "hold_mine.png"},
    "hold_slide": {"path": "hold_slide.png"},
    "hold_active": {"path": "hold_active.png"},
    "hold_each_active": {"path": "hold_each_active.png"},
    "hold_break_active": {"path": "hold_break_active.png"},
    "hold_mine_active": {"path": "hold_mine_active.png"},
    "hold_slide_active": {"path": "hold_slide_active.png"},
    "touch": {"path": "touch.png"},
    "touch_each": {"path": "touch_each.png"},
    "touch_break": {"path": "touch_break.png"},
    "touch_mine": {"path": "touch_mine.png"},
    "touch_hit": {"path": "touch_hit.png"},
    "touch_stack": {"path": "touch_stack.png"},
    "touch_star": {"path": "touch_star.png"},
    "touch_star_alt": {"path": "touch_star_alt.png"},
    "touch_star_each": {"path": "touch_star_each.png"},
    "touch_star_break": {"path": "touch_star_break.png"},
    "touch_star_mine": {"path": "touch_star_mine.png"},
    "touch_star_hit": {"path": "touch_star_hit.png"},
    "touch_hold_tr": {"path": "touch_hold_tr.png"},
    "touch_hold_br": {"path": "touch_hold_br.png"},
    "touch_hold_bl": {"path": "touch_hold_bl.png"},
    "touch_hold_tl": {"path": "touch_hold_tl.png"},
    "touch_hold_break": {"path": "touch_hold_break.png"},
    "touch_hold_mine": {"path": "touch_hold_mine.png"},
    "touch_hold_bg": {"path": "touch_hold_bg.png"},
    "touch_hold_break_bg": {"path": "touch_hold_break_bg.png"},
    "touch_hold_mine_bg": {"path": "touch_hold_mine_bg.png"},
    "touch_dot": {"path": "touch_dot.png"},
    "touch_dot_each": {"path": "touch_dot_each.png"},
    "touch_dot_break": {"path": "touch_dot_break.png"},
    "touch_dot_mine": {"path": "touch_dot_mine.png"},
    "arrow": {"path": "arrow.png"},
    "arrow_each": {"path": "arrow_each.png"},
    "arrow_break": {"path": "arrow_break.png"},
    "fan": {"path": "fan.png", "ppu": 58},
    "fan_each": {"path": "fan_each.png", "ppu": 58},
    "fan_break": {"path": "fan_break.png", "ppu": 58},
    "fan_erosion": {"path": "fan_erosion.png", "ppu": 58},
    "star_alt": {"path": "star_alt.png"},
    "touch_hit_star": {"path": "touch_hit_star.png"},
}

COLOR_KEYS = ["tap_color", "each_color", "break_color", "mine_color", "slide_color"]

FAMILY_TARGETS = {
    "tap": ["tap", "tap_each", "tap_break", "tap_mine"],
    "star": ["star", "star_each", "star_break", "star_mine"],
    "hold": [
        "hold", "hold_each", "hold_break", "hold_mine", "hold_slide",
        "hold_active", "hold_each_active", "hold_break_active", "hold_mine_active", "hold_slide_active",
    ],
    "touch": ["touch", "touch_each", "touch_break", "touch_mine"],
    "touch_dot": ["touch_dot", "touch_dot_each", "touch_dot_break", "touch_dot_mine"],
    "arrow": ["arrow", "arrow_each", "arrow_break"],
    "fan": ["fan", "fan_each", "fan_break"],
}

# PPU 自动计算分组：ring / fan / other
PPU_GROUPS = {
    "ring": {"ring"},
    "fan": {"fan", "fan_each", "fan_break", "fan_erosion"},
}
# 不在以上任何分组中的 key 归入 "other"
# 默认游戏单位值（留空时使用，用于自动计算 PPU）
PPU_DEFAULT_UNITS = {"ring": 1.4, "fan": 2.56, "other": 1.6}

VARIANT_COLORS = {
    "each": "#FFD747",
    "break": "#FF5A19",
    "mine": "#102756",
    "slide": "#44ECFF",
    "alt": "#FF72A6",
    "active": "#FFFFFF",
    "each_active": "#FFE484",
    "break_active": "#FF561E",
    "mine_active": "#0A2254",
    "slide_active": "#00E5FF",
}

I18N = {
    "zh": {
        "select_image": "选择图片",
        "no_file": "未选择文件",
        "ref_panel": "原图 + 切分线",
        "stretch_panel": "拉伸结果",
        "top_label": "Top:",
        "bottom_label": "Bottom:",
        "scale_label": "拉伸倍率:",
        "export_btn": "导出拉伸结果...",
        "info_stretchable": "可拉伸区: {mid}px ({pct:.1f}%)",
        "info_error": "top+bottom ≥ 图像高度，无法拉伸",
        "lang_name": "中文",
        "tab_hold": "Hold 九宫格",
        "tab_skinjson": "skin.json 验证/生成",
        "tab_color": "颜色变体",
        "tab_ppu": "PPU 计算",
        "tab_palette": "调色盘",
        # SkinJsonFrame
        "sj_folder": "皮肤文件夹:",
        "sj_select": "选择...",
        "sj_group": "生成 skin.json",
        "sj_name": "name:",
        "sj_designer": "designer:",
        "sj_hold": "Hold top/bottom:",
        "sj_hold_hint": "留空则不写入参数",
        "sj_validate": "验证 skin.json",
        "sj_generate": "生成/覆盖 skin.json",
        "sj_ppu_group": "PPU 自动计算 (Alpha)",
        "sj_ppu_ring": "Ring 大小单位:",
        "sj_ppu_fan": "Fan 大小单位:",
        "sj_ppu_other": "其它Note 大小单位:",
        "sj_ppu_hint": "留空=不启用自动计算",
        # ColorVariantFrame
        "cv_src": "源基础贴图:",
        "cv_out": "输出文件夹:",
        "cv_family": "贴图族:",
        "cv_group": "变体目标色",
        "cv_generate": "生成颜色变体",
        "cv_auto_compose": "(自动合成)",
        # PpuFrame
        "ppu_image": "图片:",
        "ppu_select": "选择...",
        "ppu_manual": "手动宽/高 px:",
        "ppu_units": "游戏单位:",
        "ppu_units_default": "用于计算 PPU（ppu = px / 游戏单位）",
        "ppu_units_hint": "默认: 200 (ring:115, fan:58)",
        "ppu_current": "PPU:",
        "ppu_calc_h": "按高度计算 PPU",
        "ppu_calc_w": "按宽度计算 PPU",
        "ppu_calc_size": "计算当前显示尺寸",
        "ppu_hint": "请选择图片或输入像素尺寸。",
        "ppu_calc_result": "建议 PPU: {ppu}。显示尺寸约为 {w} x {h} 游戏单位。",
        "ppu_size_result": "当前 PPU={ppu} 时，显示尺寸约为 {w} x {h} 游戏单位。",
        # PaletteFrame
        "pal_hex": "主色 HEX:",
        "pal_apply": "应用",
        "pal_copy": "复制 HEX",
        "pal_hsv": "HSV 调色",
        "pal_h": "H (色相):",
        "pal_s": "S (饱和度):",
        "pal_v": "V (明度):",
        "pal_preset": "预设颜色",
        "success_copy": "已复制 {val} 到剪贴板",
        # messagebox
        "error_title": "错误",
        "warning_title": "提示",
        "success_title": "成功",
        "error_open_image": "无法打开图片:\n{e}",
        "warning_select_image": "请先选择图片",
        "warning_fill_fields": "请填写所有必填项",
        "error_export": "top + bottom >= 图像高度，无法生成拉伸结果",
        "success_export": "已保存到:\n{path}",
        "error_color_format": "无效的颜色格式: {e}",
        # validate_skin
        "val_no_manifest": "[错误] 找不到 skin.json",
        "val_parse_fail": "[错误] skin.json 解析失败: {e}",
        "val_missing_top": "[警告] 缺少顶层属性: {key}",
        "val_bad_color": "[错误] {key} 颜色格式无效: {e}",
        "val_bad_sprite_type": "[错误] {key} 必须是字符串路径或 SpriteDefinition 对象",
        "val_missing_file": "[警告] {key}.path 指向不存在的文件，将被游戏忽略: {path}",
        "val_pivot_nan": "[错误] {key}.{n} 必须是数字",
        "val_pivot_range": "[错误] {key}.{n} 必须在 0~1 之间",
        "val_num_nan": "[错误] {key}.{n} 必须是数字",
        "val_num_neg": "[错误] {key}.{n} 不能为负数",
        "val_extra_image": "[提示] 文件夹内有未被 manifest 默认表识别的图片: {name}",
        "val_pass": "[通过] skin.json 未发现严重问题",
        # generate
        "gen_success": "已生成: {path}",
        # color variant
        "cv_generated": "已生成: {name}  ({variant} -> {color})",
        # SkinJsonFrame labels
        "sj_name_label": "name:",
        "sj_designer_label": "designer:",
        "sj_hold_label": "Hold top/bottom:",
        # color key labels
        "ck_tap_color": "tap_color:",
        "ck_each_color": "each_color:",
        "ck_break_color": "break_color:",
        "ck_mine_color": "mine_color:",
        "ck_slide_color": "slide_color:",
        # file dialog titles
        "fd_select_hold": "选择 Hold 图片",
        "fd_save_stretch": "保存拉伸结果",
        "fd_select_image": "选择图片",
        "fd_image_files": "图片文件",
        "fd_all_files": "所有文件",
        "fd_select_touch": "选择 Touch 贴图",
        "fd_save_mirror": "保存合成结果",
        "fd_save_compose": "保存合成结果",
        "tab_mirror": "Touch 合成",
        "tm_src": "源贴图:",
        "tm_dot": "中心 dot:",
        "tm_gap": "间距 (px):",
        "tm_preview": "合成预览",
        "tm_dot_scale": "Dot 缩放:",
        "tm_export": "导出合并图...",
        "tm_info": "输出尺寸: {w} x {h} px",
        # TouchHoldComposeFrame
        "tab_holdcomp": "Touch Hold 合成",
        "hc_mode": "模式:",
        "hc_mode_4c": "4 角独立",
        "hc_mode_1s": "1 图复制 (break/mine)",
        "hc_src": "源贴图:",
        "hc_c1": "红 (右上/tr):",
        "hc_c2": "黄 (右下/br):",
        "hc_c3": "绿 (左下/bl):",
        "hc_c4": "蓝 (左上/tl):",
        "hc_dot": "中心 dot:",
        "hc_bg": "背景 bg:",
        "hc_gap": "间距 (px):",
        "hc_bg_scale": "Bg 缩放:",
        "hc_dot_scale": "Dot 缩放:",
        "hc_preview": "合成预览",
        "hc_export": "导出合成图...",
        "hc_info": "输出尺寸: {w} x {h} px",
    },
    "en": {
        "select_image": "Select Image",
        "no_file": "No file selected",
        "ref_panel": "Original + Slice Lines",
        "stretch_panel": "Stretch Result",
        "top_label": "Top:",
        "bottom_label": "Bottom:",
        "scale_label": "Stretch Scale:",
        "export_btn": "Export Result...",
        "info_stretchable": "Stretchable area: {mid}px ({pct:.1f}%)",
        "info_error": "top+bottom >= image height, cannot stretch",
        "lang_name": "English",
        "tab_hold": "Hold 9-Slice",
        "tab_skinjson": "skin.json Verify/Generate",
        "tab_color": "Color Variants",
        "tab_ppu": "PPU Calculator",
        "tab_palette": "Color Picker",
        # SkinJsonFrame
        "sj_folder": "Skin Folder:",
        "sj_select": "Browse...",
        "sj_group": "Generate skin.json",
        "sj_name": "name:",
        "sj_designer": "designer:",
        "sj_hold": "Hold top/bottom:",
        "sj_hold_hint": "Leave empty to skip params",
        "sj_validate": "Validate skin.json",
        "sj_generate": "Generate/Overwrite skin.json",
        "sj_ppu_group": "Auto PPU Calc (Alpha)",
        "sj_ppu_ring": "Ring Size Units:",
        "sj_ppu_fan": "Fan Size Units:",
        "sj_ppu_other": "Other Note Size Units:",
        "sj_ppu_hint": "Empty = auto calc disabled",
        # ColorVariantFrame
        "cv_src": "Source Base Image:",
        "cv_out": "Output Folder:",
        "cv_family": "Sprite Family:",
        "cv_group": "Variant Target Colors",
        "cv_generate": "Generate Color Variants",
        "cv_auto_compose": "(auto compose)",
        # PpuFrame
        "ppu_image": "Image:",
        "ppu_select": "Browse...",
        "ppu_manual": "Manual W/H px:",
        "ppu_units": "Game Units:",
        "ppu_units_default": "Used to calc PPU (ppu = px / units)",
        "ppu_units_hint": "Default: 200 (ring:115, fan:58)",
        "ppu_current": "PPU:",
        "ppu_calc_h": "Calc PPU by Height",
        "ppu_calc_w": "Calc PPU by Width",
        "ppu_calc_size": "Calc Display Size",
        "ppu_hint": "Select an image or enter pixel dimensions.",
        "ppu_calc_result": "Recommended PPU: {ppu}. Display size ≈ {w} x {h} game units.",
        "ppu_size_result": "With PPU={ppu}, display size ≈ {w} x {h} game units.",
        # PaletteFrame
        "pal_hex": "Main HEX:",
        "pal_apply": "Apply",
        "pal_copy": "Copy HEX",
        "pal_hsv": "HSV Picker",
        "pal_h": "H (Hue):",
        "pal_s": "S (Saturation):",
        "pal_v": "V (Value):",
        "pal_preset": "Preset Colors",
        "success_copy": "Copied {val} to clipboard",
        # messagebox
        "error_title": "Error",
        "warning_title": "Warning",
        "success_title": "Success",
        "error_open_image": "Cannot open image:\n{e}",
        "warning_select_image": "Please select an image first",
        "warning_fill_fields": "Please fill in all required fields",
        "error_export": "top + bottom >= image height, cannot generate stretch result",
        "success_export": "Saved to:\n{path}",
        "error_color_format": "Invalid color format: {e}",
        # validate_skin
        "val_no_manifest": "[Error] skin.json not found",
        "val_parse_fail": "[Error] Failed to parse skin.json: {e}",
        "val_missing_top": "[Warning] Missing top-level property: {key}",
        "val_bad_color": "[Error] {key} invalid color format: {e}",
        "val_bad_sprite_type": "[Error] {key} must be a string path or SpriteDefinition object",
        "val_missing_file": "[Warning] {key}.path points to a non-existent file, will be ignored by the game: {path}",
        "val_pivot_nan": "[Error] {key}.{n} must be a number",
        "val_pivot_range": "[Error] {key}.{n} must be between 0 and 1",
        "val_num_nan": "[Error] {key}.{n} must be a number",
        "val_num_neg": "[Error] {key}.{n} cannot be negative",
        "val_extra_image": "[Info] Image in folder not recognized by manifest defaults: {name}",
        "val_pass": "[Pass] skin.json has no critical issues",
        # generate
        "gen_success": "Generated: {path}",
        # color variant
        "cv_generated": "Generated: {name}  ({variant} -> {color})",
        # SkinJsonFrame labels
        "sj_name_label": "name:",
        "sj_designer_label": "designer:",
        "sj_hold_label": "Hold top/bottom:",
        # color key labels
        "ck_tap_color": "tap_color:",
        "ck_each_color": "each_color:",
        "ck_break_color": "break_color:",
        "ck_mine_color": "mine_color:",
        "ck_slide_color": "slide_color:",
        # file dialog titles
        "fd_select_hold": "Select Hold Image",
        "fd_save_stretch": "Save Stretch Result",
        "fd_select_image": "Select Image",
        "fd_image_files": "Image Files",
        "fd_all_files": "All Files",
        "fd_select_touch": "Select Touch Image",
        "fd_save_mirror": "Save Compose Result",
        "fd_save_compose": "Save Composed Result",
        "tab_mirror": "Touch Compose",
        "tm_src": "Source Image:",
        "tm_dot": "Center dot:",
        "tm_gap": "Gap (px):",
        "tm_preview": "Compose Preview",
        "tm_dot_scale": "Dot Scale:",
        "tm_export": "Export Combined...",
        "tm_info": "Output size: {w} x {h} px",
        # TouchHoldComposeFrame
        "tab_holdcomp": "Touch Hold Compose",
        "hc_mode": "Mode:",
        "hc_mode_4c": "4 Corners",
        "hc_mode_1s": "1 Source (break/mine)",
        "hc_src": "Source:",
        "hc_c1": "tr (top-right):",
        "hc_c2": "br (bottom-right):",
        "hc_c3": "bl (bottom-left):",
        "hc_c4": "tl (top-left):",
        "hc_dot": "Center dot:",
        "hc_bg": "Bg:",
        "hc_gap": "Gap (px):",
        "hc_bg_scale": "Bg Scale:",
        "hc_dot_scale": "Dot Scale:",
        "hc_preview": "Compose Preview",
        "hc_export": "Export Composed...",
        "hc_info": "Output size: {w} x {h} px",
    },
}


def nine_slice_stretch(img: Image.Image, top: int, bottom: int, target_h: int) -> Image.Image:
    w, h = img.size
    mid_h = h - top - bottom
    if mid_h <= 0:
        return img.copy()
    top_part = img.crop((0, 0, w, top))
    mid_part = img.crop((0, top, w, h - bottom))
    bottom_part = img.crop((0, h - bottom, w, h))
    new_mid_h = max(0, target_h - top - bottom)
    result = Image.new("RGBA", (w, target_h), (0, 0, 0, 0))
    result.paste(top_part, (0, 0))
    if new_mid_h > 0:
        result.paste(mid_part.resize((w, new_mid_h), Image.LANCZOS), (0, top))
    result.paste(bottom_part, (0, top + new_mid_h))
    return result


def draw_slice_lines(img: Image.Image, top: int, bottom: int) -> Image.Image:
    w, h = img.size
    marked = img.copy()
    draw = ImageDraw.Draw(marked)
    draw.line([(0, top), (w, top)], fill=(255, 50, 50), width=2)
    draw.line([(0, h - bottom), (w, h - bottom)], fill=(50, 100, 255), width=2)
    draw.text((4, top + 3), f"top={top}", fill=(255, 50, 50))
    draw.text((4, h - bottom - 16), f"bottom={bottom}", fill=(50, 100, 255))
    if top + bottom < h:
        draw.rectangle([1, top, w - 1, h - bottom - 1], outline=(180, 180, 180), width=1)
    return marked


def parse_hex_color(value: str) -> tuple[int, int, int]:
    s = value.strip().lstrip("#")
    if len(s) not in (6, 8):
        raise ValueError("颜色必须是 #RRGGBB 或 #RRGGBBAA")
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def recolor_image(img: Image.Image, target_hex: str) -> Image.Image:
    target_r, target_g, target_b = parse_hex_color(target_hex)
    th, ts, tv = colorsys.rgb_to_hsv(target_r / 255, target_g / 255, target_b / 255)
    result = img.convert("RGBA")
    pixels = result.load()
    for y in range(result.height):
        for x in range(result.width):
            r, g, b, a = pixels[x, y]
            if a == 0:
                continue
            _, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            nr, ng, nb = colorsys.hsv_to_rgb(th, max(s, ts * 0.75), v * (0.75 + tv * 0.25))
            pixels[x, y] = (int(nr * 255), int(ng * 255), int(nb * 255), a)
    return result


def sprite_to_variant(sprite_key: str) -> str:
    """将贴图键名转换为变体名，支持复合变体如 break_active"""
    parts = sprite_key.split("_")
    # 先检查复合变体（优先匹配更长的）
    for compound in ("each_active", "break_active", "mine_active", "slide_active"):
        if compound in sprite_key:
            return compound
    for name in ("each", "break", "mine", "slide", "alt", "active"):
        if name in parts:
            return name
    return "normal"


def list_images(folder: Path) -> set[str]:
    if not folder.exists():
        return set()
    return {p.name for p in folder.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_skin(folder: Path, lang: str = "zh") -> list[str]:
    t = I18N[lang]
    messages: list[str] = []
    manifest_path = folder / "skin.json"
    if not manifest_path.exists():
        messages.append(t["val_no_manifest"])
        return messages

    try:
        data = load_json(manifest_path)
    except Exception as e:
        return [t["val_parse_fail"].format(e=e)]

    for key in ("name", "designer"):
        if key not in data or not str(data.get(key, "")).strip():
            messages.append(t["val_missing_top"].format(key=key))

    for color_key in COLOR_KEYS:
        if color_key in data:
            val = str(data[color_key]).strip()
            if not val:
                continue
            try:
                parse_hex_color(val)
            except Exception as e:
                messages.append(t["val_bad_color"].format(key=color_key, e=e))

    for key, value in data.items():
        if key not in SPRITE_DEFAULTS:
            continue
        if isinstance(value, str):
            sprite = {"path": value}
            path_is_explicit = True
        elif isinstance(value, dict):
            sprite = value
            path_is_explicit = "path" in sprite
        else:
            messages.append(t["val_bad_sprite_type"].format(key=key))
            continue

        rel_path = sprite.get("path", SPRITE_DEFAULTS[key]["path"])
        if path_is_explicit and rel_path and not (folder / rel_path).exists():
            messages.append(t["val_missing_file"].format(key=key, path=rel_path))
        for n in ("pivot_x", "pivot_y"):
            if n not in sprite:
                continue
            try:
                value_num = float(sprite[n])
            except (TypeError, ValueError):
                messages.append(t["val_pivot_nan"].format(key=key, n=n))
                continue
            if not (0 <= value_num <= 1):
                messages.append(t["val_pivot_range"].format(key=key, n=n))
        for n in ("ppu", "top", "bottom"):
            if n not in sprite:
                continue
            try:
                value_num = float(sprite[n])
            except (TypeError, ValueError):
                messages.append(t["val_num_nan"].format(key=key, n=n))
                continue
            if value_num < 0:
                messages.append(t["val_num_neg"].format(key=key, n=n))

    image_names = list_images(folder)
    declared = set()
    for key, value in data.items():
        if key in SPRITE_DEFAULTS:
            if isinstance(value, str):
                declared.add(value)
            elif isinstance(value, dict):
                declared.add(value.get("path", SPRITE_DEFAULTS[key]["path"]))
            else:
                declared.add(SPRITE_DEFAULTS[key]["path"])
    known_defaults = {v["path"] for v in SPRITE_DEFAULTS.values()}
    extras = sorted(image_names - declared - known_defaults)
    for name in extras:
        messages.append(t["val_extra_image"].format(name=name))

    real_errors = [m for m in messages if m.startswith("[错误]") or m.startswith("[Error]")]
    real_warnings = [m for m in messages if m.startswith("[警告]") or m.startswith("[Warning]")]
    if not real_errors and not real_warnings:
        messages.insert(0, t["val_pass"])
    return messages


def generate_skin_manifest(folder: Path, name: str, designer: str, colors: dict[str, str], hold_top: int | None, hold_bottom: int | None, ppu_units: dict[str, float] | None = None) -> dict:
    image_names = list_images(folder)
    data: dict = {}
    if name.strip():
        data["name"] = name.strip()
    if designer.strip():
        data["designer"] = designer.strip()
    for key, value in colors.items():
        value = value.strip()
        if value:
            parse_hex_color(value)
            data[key] = value.upper()

    for key, defaults in SPRITE_DEFAULTS.items():
        if defaults["path"] not in image_names:
            continue
        sprite = {"path": defaults["path"]}

        # 确定该 key 属于哪个 PPU 分组
        group_name = None
        for gname, gkeys in PPU_GROUPS.items():
            if key in gkeys:
                group_name = gname
                break
        if group_name is None:
            group_name = "other"

        # PPU: 用户填入游戏单位后自动计算，留空则不启用自动计算
        if ppu_units and group_name in ppu_units:
            units = ppu_units[group_name]
            img_path = folder / defaults["path"]
            try:
                with Image.open(img_path) as img:
                    ppu = round(img.width / units)
                if ppu != 200:
                    sprite["ppu"] = ppu
            except Exception:
                pass

        if key.startswith("hold") and hold_top is not None and hold_bottom is not None:
            sprite["top"] = hold_top
            sprite["bottom"] = hold_bottom

        # 构建默认 sprite 用于比较
        default_sprite = {"path": defaults["path"]}
        if sprite != default_sprite:
            data[key] = sprite

    return data


class Hold9SliceFrame(ttk.Frame):
    PREVIEW_MAX_H = 500

    def __init__(self, master):
        super().__init__(master, padding=8)
        self.image_path: str | None = None
        self.original_img: Image.Image | None = None
        self.photo_ref: ImageTk.PhotoImage | None = None
        self.photo_stretch: ImageTk.PhotoImage | None = None
        self._build_ui()

    @property
    def lang(self):
        return self.winfo_toplevel().lang

    def _t(self, key: str, **kwargs) -> str:
        return I18N[self.lang][key].format(**kwargs)

    def _apply_i18n(self):
        if not self.image_path:
            self.path_label.config(text=self._t("no_file"))
        self.frame_left.config(text=self._t("ref_panel"))
        self.frame_right.config(text=self._t("stretch_panel"))
        self.btn_select.config(text=self._t("select_image"))
        self.top_label.config(text=self._t("top_label"))
        self.bot_label.config(text=self._t("bottom_label"))
        self.scale_label.config(text=self._t("scale_label"))
        self.btn_export.config(text=self._t("export_btn"))
        self._update_preview()

    def _build_ui(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X)
        self.btn_select = ttk.Button(top_frame, text=self._t("select_image"), command=self._on_select_image)
        self.btn_select.pack(side=tk.LEFT, padx=(0, 8))
        self.path_label = ttk.Label(top_frame, text=self._t("no_file"), foreground="gray")
        self.path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        preview_frame = ttk.Frame(self, padding=(0, 8))
        preview_frame.pack(fill=tk.BOTH, expand=True)
        self.frame_left = ttk.LabelFrame(preview_frame, text=self._t("ref_panel"), padding=4)
        self.frame_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 4))
        self.canvas_left = tk.Canvas(self.frame_left, bg="#2a2a2a", highlightthickness=0)
        self.canvas_left.pack(fill=tk.BOTH, expand=True)
        self.frame_right = ttk.LabelFrame(preview_frame, text=self._t("stretch_panel"), padding=4)
        self.frame_right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 0))
        self.canvas_right = tk.Canvas(self.frame_right, bg="#2a2a2a", highlightthickness=0)
        self.canvas_right.pack(fill=tk.BOTH, expand=True)

        ctrl = ttk.Frame(self)
        ctrl.pack(fill=tk.X)
        self.top_var = tk.IntVar(value=52)
        self.bot_var = tk.IntVar(value=54)
        self.scale_var = tk.DoubleVar(value=3.0)
        self.top_label, self.top_value_label = self._add_slider(ctrl, self._t("top_label"), self.top_var, 0, 300)
        self.bot_label, self.bot_value_label = self._add_slider(ctrl, self._t("bottom_label"), self.bot_var, 0, 300)
        self.scale_label, self.scale_value_label = self._add_slider(ctrl, self._t("scale_label"), self.scale_var, 0.0, 10.0)
        row = ttk.Frame(ctrl)
        row.pack(fill=tk.X, pady=(8, 0))
        self.info_label = ttk.Label(row, text="", foreground="#666")
        self.info_label.pack(side=tk.LEFT)
        self.btn_export = ttk.Button(row, text=self._t("export_btn"), command=self._on_export)
        self.btn_export.pack(side=tk.RIGHT)

    def _add_slider(self, parent, label, var, from_, to):
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=2)
        name_label = ttk.Label(row, text=label, width=14)
        name_label.pack(side=tk.LEFT)
        slider = ttk.Scale(row, from_=from_, to=to, variable=var, orient=tk.HORIZONTAL, command=lambda _: self._update_preview())
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        value_label = ttk.Label(row, text=str(var.get()), width=8)
        value_label.pack(side=tk.LEFT)
        return name_label, value_label

    def _load_default_image(self):
        default = Path(__file__).resolve().parent / "DXskin" / "hold.png"
        if default.exists():
            self._open_image(str(default))

    def _on_select_image(self):
        path = filedialog.askopenfilename(
            title=self._t("fd_select_hold"),
            filetypes=[(self._t("fd_image_files"), "*.png *.jpg *.jpeg *.bmp"), (self._t("fd_all_files"), "*.*")],
        )
        if path:
            self._open_image(path)

    def _open_image(self, path: str):
        try:
            self.original_img = Image.open(path).convert("RGBA")
            self.image_path = path
            w, h = self.original_img.size
            self.path_label.config(text=f"{os.path.basename(path)}  ({w}x{h})")
            self._update_preview()
        except Exception as e:
            messagebox.showerror(self._t("error_title"), self._t("error_open_image", e=e))

    def _update_preview(self):
        if self.original_img is None:
            return
        img = self.original_img
        try:
            top = int(self.top_var.get())
            bottom = int(self.bot_var.get())
            scale = float(self.scale_var.get())
        except ValueError:
            return
        self.top_value_label.config(text=str(top))
        self.bot_value_label.config(text=str(bottom))
        self.scale_value_label.config(text=f"{scale:.1f}x")
        mid = img.height - top - bottom
        if mid <= 0:
            self.info_label.config(text=self._t("info_error"), foreground="red")
            stretched = img.copy()
        else:
            self.info_label.config(text=self._t("info_stretchable", mid=mid, pct=mid / img.height * 100), foreground="#666")
            target_h = round(top + bottom + mid * scale)
            stretched = nine_slice_stretch(img, top, bottom, max(top + bottom, target_h))
        self.photo_ref = self._fit_photo(draw_slice_lines(img, top, bottom))
        self.photo_stretch = self._fit_photo(stretched)
        self._show_on_canvas(self.canvas_left, self.photo_ref)
        self._show_on_canvas(self.canvas_right, self.photo_stretch)

    @classmethod
    def _fit_photo(cls, img: Image.Image) -> ImageTk.PhotoImage:
        if img.height > cls.PREVIEW_MAX_H:
            ratio = cls.PREVIEW_MAX_H / img.height
            img = img.resize((round(img.width * ratio), cls.PREVIEW_MAX_H), Image.LANCZOS)
        return ImageTk.PhotoImage(img)

    @staticmethod
    def _show_on_canvas(canvas: tk.Canvas, photo: ImageTk.PhotoImage):
        canvas.delete("all")
        canvas.update_idletasks()
        cw, ch = max(canvas.winfo_width(), 400), max(canvas.winfo_height(), 300)
        canvas.create_image((cw - photo.width()) // 2, (ch - photo.height()) // 2, anchor=tk.NW, image=photo)

    def _on_export(self):
        if self.original_img is None:
            messagebox.showwarning(self._t("warning_title"), self._t("warning_select_image"))
            return
        try:
            top = int(self.top_var.get())
            bottom = int(self.bot_var.get())
            scale = float(self.scale_var.get())
        except ValueError:
            messagebox.showwarning(self._t("warning_title"), self._t("warning_fill_fields"))
            return
        mid = self.original_img.height - top - bottom
        if mid <= 0:
            messagebox.showerror(self._t("error_title"), self._t("error_export"))
            return
        result = nine_slice_stretch(self.original_img, top, bottom, round(top + bottom + mid * scale))
        base = Path(self.image_path).stem if self.image_path else "output"
        path = filedialog.asksaveasfilename(
            title=self._t("fd_save_stretch"),
            initialfile=f"{base}_stretch_{scale:.1f}x_top{top}_bot{bottom}.png",
            defaultextension=".png",
            filetypes=[("PNG", "*.png")],
        )
        if path:
            result.save(path)
            messagebox.showinfo(self._t("success_title"), self._t("success_export", path=path))


class SkinJsonFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=8)
        self.folder_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.designer_var = tk.StringVar()
        self.hold_top_var = tk.StringVar()
        self.hold_bottom_var = tk.StringVar()
        self.color_vars = {key: tk.StringVar() for key in COLOR_KEYS}
        self.ppu_vars = {"ring": tk.StringVar(), "fan": tk.StringVar(), "other": tk.StringVar()}
        self._build_ui()

    @property
    def lang(self):
        return self.winfo_toplevel().lang

    def _t(self, key: str, **kwargs) -> str:
        return I18N[self.lang][key].format(**kwargs)

    def _apply_i18n(self):
        self.folder_label.config(text=self._t("sj_folder"))
        self.select_btn.config(text=self._t("sj_select"))
        self.form.config(text=self._t("sj_group"))
        self.hold_hint.config(text=self._t("sj_hold_hint"))
        self.validate_btn.config(text=self._t("sj_validate"))
        self.generate_btn.config(text=self._t("sj_generate"))
        self.name_label.config(text=self._t("sj_name_label"))
        self.designer_label.config(text=self._t("sj_designer_label"))
        self.hold_label.config(text=self._t("sj_hold_label"))
        for key, label in self._color_labels.items():
            label.config(text=self._t("ck_" + key))
        self.ppu_frame.config(text=self._t("sj_ppu_group"))
        self.ppu_hint_label.config(text=self._t("sj_ppu_hint"))
        for gkey, lbl in self._ppu_labels.items():
            lbl.config(text=self._t("sj_ppu_" + gkey))

    def _build_ui(self):
        folder_row = ttk.Frame(self)
        folder_row.pack(fill=tk.X)
        self.folder_label = ttk.Label(folder_row, text=self._t("sj_folder"), width=12)
        self.folder_label.pack(side=tk.LEFT)
        ttk.Entry(folder_row, textvariable=self.folder_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        self.select_btn = ttk.Button(folder_row, text=self._t("sj_select"), command=self._select_folder)
        self.select_btn.pack(side=tk.LEFT)

        self.form = ttk.LabelFrame(self, text=self._t("sj_group"), padding=8)
        self.form.pack(fill=tk.X, pady=(2, 8))
        self.hold_hint = ttk.Label(self, text=self._t("sj_hold_hint"), foreground="gray")
        self.hold_hint.pack(anchor='e')
        # PPU 自动计算组
        self.ppu_frame = ttk.LabelFrame(self.form, text=self._t("sj_ppu_group"), padding=4)
        self.ppu_frame.pack(fill=tk.X, pady=(2, 4))
        self.ppu_hint_label = ttk.Label(self.ppu_frame, text=self._t("sj_ppu_hint"), foreground="gray")
        self.ppu_hint_label.pack(anchor='e')
        self._ppu_labels: dict[str, ttk.Label] = {}
        for gkey, glabel_key in [("ring", "sj_ppu_ring"), ("fan", "sj_ppu_fan"), ("other", "sj_ppu_other")]:
            row = ttk.Frame(self.ppu_frame)
            row.pack(fill=tk.X, pady=1)
            lbl = ttk.Label(row, text=self._t(glabel_key), width=20)
            lbl.pack(side=tk.LEFT)
            ttk.Entry(row, textvariable=self.ppu_vars[gkey], width=8).pack(side=tk.LEFT, padx=4)
            self._ppu_labels[gkey] = lbl
        # name 行
        name_row = ttk.Frame(self.form)
        name_row.pack(fill=tk.X, pady=2)
        self.name_label = ttk.Label(name_row, text=self._t("sj_name_label"), width=16)
        self.name_label.pack(side=tk.LEFT)
        ttk.Entry(name_row, textvariable=self.name_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        # designer 行
        designer_row = ttk.Frame(self.form)
        designer_row.pack(fill=tk.X, pady=2)
        self.designer_label = ttk.Label(designer_row, text=self._t("sj_designer_label"), width=16)
        self.designer_label.pack(side=tk.LEFT)
        ttk.Entry(designer_row, textvariable=self.designer_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        # Hold top/bottom 行
        hold_row = ttk.Frame(self.form)
        hold_row.pack(fill=tk.X, pady=2)
        self.hold_label = ttk.Label(hold_row, text=self._t("sj_hold_label"), width=16)
        self.hold_label.pack(side=tk.LEFT)
        ttk.Entry(hold_row, textvariable=self.hold_top_var, width=8).pack(side=tk.LEFT, padx=4)
        ttk.Entry(hold_row, textvariable=self.hold_bottom_var, width=8).pack(side=tk.LEFT, padx=4)
        # 颜色键行
        self._color_labels: dict[str, ttk.Label] = {}
        for key, var in self.color_vars.items():
            row = ttk.Frame(self.form)
            row.pack(fill=tk.X, pady=2)
            lbl = ttk.Label(row, text=self._t("ck_" + key), width=16)
            lbl.pack(side=tk.LEFT)
            ttk.Entry(row, textvariable=var).pack(side=tk.LEFT, fill=tk.X, expand=True)
            self._color_labels[key] = lbl
        btns = ttk.Frame(self.form)
        btns.pack(fill=tk.X, pady=(6, 0))
        self.validate_btn = ttk.Button(btns, text=self._t("sj_validate"), command=self._validate)
        self.validate_btn.pack(side=tk.LEFT)
        self.generate_btn = ttk.Button(btns, text=self._t("sj_generate"), command=self._generate)
        self.generate_btn.pack(side=tk.LEFT, padx=8)

        self.output = tk.Text(self, height=22, wrap=tk.WORD)
        self.output.pack(fill=tk.BOTH, expand=True)

    def _select_folder(self):
        path = filedialog.askdirectory(title=self._t("sj_folder"))
        if path:
            self.folder_var.set(path)

    def _folder(self) -> Path:
        return Path(self.folder_var.get()).expanduser()

    def _write_output(self, text: str):
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, text)

    def _validate(self):
        self._write_output("\n".join(validate_skin(self._folder(), self.lang)))

    def _generate(self):
        try:
            top = int(self.hold_top_var.get()) if self.hold_top_var.get().strip() else None
            bottom = int(self.hold_bottom_var.get()) if self.hold_bottom_var.get().strip() else None
            ppu_units = {}
            for gkey, var in self.ppu_vars.items():
                val = var.get().strip()
                if val:
                    ppu_units[gkey] = float(val)
            data = generate_skin_manifest(
                self._folder(),
                self.name_var.get(),
                self.designer_var.get(),
                {k: v.get() for k, v in self.color_vars.items()},
                top,
                bottom,
                ppu_units if ppu_units else None,
            )
            text = json.dumps(data, ensure_ascii=False, indent=2)
            out = self._folder() / "skin.json"
            out.write_text(text + "\n", encoding="utf-8")
            self._write_output(f"{self._t('gen_success', path=out)}\n\n{text}")
        except Exception as e:
            messagebox.showerror(self._t("error_title"), str(e))


class ColorVariantFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=8)
        self.src_var = tk.StringVar()
        self.out_var = tk.StringVar()
        self.family_var = tk.StringVar(value="tap")
        self.color_vars = {k: tk.StringVar(value=v) for k, v in VARIANT_COLORS.items()}
        self._color_rows: dict[str, tuple] = {}  # key -> (frame, label, hint_label)
        self._build_ui()

    @property
    def lang(self):
        return self.winfo_toplevel().lang

    def _t(self, key: str, **kwargs) -> str:
        return I18N[self.lang][key].format(**kwargs)

    def _apply_i18n(self):
        self.src_label.config(text=self._t("cv_src"))
        self.src_btn.config(text=self._t("sj_select"))
        self.out_label.config(text=self._t("cv_out"))
        self.out_btn.config(text=self._t("sj_select"))
        self.family_label.config(text=self._t("cv_family"))
        self.form.config(text=self._t("cv_group"))
        self.generate_btn.config(text=self._t("cv_generate"))
        self._refresh_color_rows()

    def _get_family_variants(self) -> list[tuple[str, str, bool]]:
        """获取当前贴图族实际使用的变体列表，返回 (display_key, color_var_key, needs_color) 元组列表"""
        family = self.family_var.get()
        variants = set()
        for sprite_key in FAMILY_TARGETS.get(family, []):
            variants.add(sprite_to_variant(sprite_key))
        order = ["each", "break", "mine", "slide", "alt", "active",
                 "each_active", "break_active", "mine_active", "slide_active"]
        return [(v, v, True) for v in order if v in variants]

    def _refresh_color_rows(self):
        """根据当前贴图族刷新颜色输入行"""
        # 清除旧行
        for key, (frame, label, hint_label) in self._color_rows.items():
            frame.destroy()
        self._color_rows.clear()
        # 只显示当前族需要的变体
        for key, color_key, needs_color in self._get_family_variants():
            row = ttk.Frame(self.form)
            row.pack(fill=tk.X, pady=2)
            label = ttk.Label(row, text=key + ":", width=18)
            label.pack(side=tk.LEFT)
            if needs_color:
                ttk.Entry(row, textvariable=self.color_vars[color_key], width=12).pack(side=tk.LEFT)
                default_val = VARIANT_COLORS.get(color_key, "")
                hint_label = ttk.Label(row, text=f"({default_val})", foreground="gray")
                hint_label.pack(side=tk.LEFT, padx=4)
            else:
                hint_label = ttk.Label(row, text=self._t("cv_auto_compose"), foreground="gray")
                hint_label.pack(side=tk.LEFT, padx=4)
            self._color_rows[key] = (row, label, hint_label)

    def _build_ui(self):
        self.src_label, self.src_btn = self._path_row(self._t("cv_src"), self.src_var, self._select_src)
        self.out_label, self.out_btn = self._path_row(self._t("cv_out"), self.out_var, self._select_out)
        row = ttk.Frame(self)
        row.pack(fill=tk.X, pady=4)
        self.family_label = ttk.Label(row, text=self._t("cv_family"), width=12)
        self.family_label.pack(side=tk.LEFT)
        combo = ttk.Combobox(row, textvariable=self.family_var, values=list(FAMILY_TARGETS), state="readonly", width=18)
        combo.pack(side=tk.LEFT)
        combo.bind("<<ComboboxSelected>>", lambda _: self._refresh_color_rows())
        self.form = ttk.LabelFrame(self, text=self._t("cv_group"), padding=8)
        self.form.pack(fill=tk.X, pady=8)
        self._refresh_color_rows()
        self.generate_btn = ttk.Button(self, text=self._t("cv_generate"), command=self._generate)
        self.generate_btn.pack(anchor=tk.W)
        self.output = tk.Text(self, height=18, wrap=tk.WORD)
        self.output.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

    def _path_row(self, label, var, command):
        row = ttk.Frame(self)
        row.pack(fill=tk.X, pady=2)
        lbl = ttk.Label(row, text=label, width=12)
        lbl.pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        btn = ttk.Button(row, text=self._t("sj_select"), command=command)
        btn.pack(side=tk.LEFT)
        return lbl, btn

    def _select_src(self):
        path = filedialog.askopenfilename(title=self._t("cv_src"), filetypes=[("Image", "*.png *.jpg *.jpeg *.bmp")])
        if path:
            self.src_var.set(path)

    def _select_out(self):
        path = filedialog.askdirectory(title=self._t("cv_out"))
        if path:
            self.out_var.set(path)

    def _generate(self):
        try:
            src = Path(self.src_var.get())
            out_dir = Path(self.out_var.get())
            out_dir.mkdir(parents=True, exist_ok=True)
            img = Image.open(src).convert("RGBA")
            lines = []
            family = self.family_var.get()
            for sprite_key in FAMILY_TARGETS[family]:
                variant = sprite_to_variant(sprite_key)
                if variant == "normal":
                    result = img
                    color = "original"
                else:
                    color = self.color_vars.get(variant).get()
                    result = recolor_image(img, color)
                out_path = out_dir / SPRITE_DEFAULTS[sprite_key]["path"]
                result.save(out_path, optimize=True)
                lines.append(self._t("cv_generated", name=out_path.name, variant=variant, color=color))
            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, "\n".join(lines))
        except Exception as e:
            messagebox.showerror(self._t("error_title"), str(e))


class TouchMirrorFrame(ttk.Frame):
    """导入 touch 贴图，自动合成四个拼在一起（2×2 网格）"""
    PREVIEW_MAX_H = 500

    def __init__(self, master):
        super().__init__(master, padding=8)
        self.src_var = tk.StringVar()
        self.dot_var = tk.StringVar()
        self.src_img: Image.Image | None = None
        self.dot_img: Image.Image | None = None
        self.photo_ref: ImageTk.PhotoImage | None = None
        self.gap_var = tk.IntVar(value=0)
        self.dot_scale_var = tk.DoubleVar(value=1.0)
        self._canvas_img_id = None
        self._build_ui()

    @property
    def lang(self):
        return self.winfo_toplevel().lang

    def _t(self, key: str, **kwargs) -> str:
        return I18N[self.lang][key].format(**kwargs)

    def _apply_i18n(self):
        if not self.src_var.get():
            self.path_label.config(text=self._t("no_file"))
        if not self.dot_var.get():
            self.dot_path_label.config(text=self._t("no_file"))
        self.src_label.config(text=self._t("tm_src"))
        self.btn_select.config(text=self._t("sj_select"))
        self.dot_label.config(text=self._t("tm_dot"))
        self.btn_select_dot.config(text=self._t("sj_select"))
        self.gap_label.config(text=self._t("tm_gap"))
        self.dot_scale_label.config(text=self._t("tm_dot_scale"))
        self.frame_preview.config(text=self._t("tm_preview"))
        self.btn_export.config(text=self._t("tm_export"))
        self._update_preview()

    def _build_ui(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X)
        self.src_label = ttk.Label(top_frame, text=self._t("tm_src"), width=12)
        self.src_label.pack(side=tk.LEFT)
        self.btn_select = ttk.Button(top_frame, text=self._t("sj_select"), command=self._on_select)
        self.btn_select.pack(side=tk.LEFT, padx=(0, 8))
        self.path_label = ttk.Label(top_frame, text=self._t("no_file"), foreground="gray")
        self.path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        dot_frame = ttk.Frame(self)
        dot_frame.pack(fill=tk.X)
        self.dot_label = ttk.Label(dot_frame, text=self._t("tm_dot"), width=12)
        self.dot_label.pack(side=tk.LEFT)
        self.btn_select_dot = ttk.Button(dot_frame, text=self._t("sj_select"), command=self._on_select_dot)
        self.btn_select_dot.pack(side=tk.LEFT, padx=(0, 8))
        self.dot_path_label = ttk.Label(dot_frame, text=self._t("no_file"), foreground="gray")
        self.dot_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ctrl = ttk.Frame(self)
        ctrl.pack(fill=tk.X, pady=(4, 0))
        self.gap_label = ttk.Label(ctrl, text=self._t("tm_gap"), width=12)
        self.gap_label.pack(side=tk.LEFT)
        self.gap_slider = ttk.Scale(ctrl, from_=-100, to=100, variable=self.gap_var, orient=tk.HORIZONTAL,
                                    command=lambda _: self._update_preview())
        self.gap_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        self.gap_value_label = ttk.Label(ctrl, text="0", width=6)
        self.gap_value_label.pack(side=tk.LEFT)

        ds_ctrl = ttk.Frame(self)
        ds_ctrl.pack(fill=tk.X, pady=(2, 0))
        self.dot_scale_label = ttk.Label(ds_ctrl, text=self._t("tm_dot_scale"), width=12)
        self.dot_scale_label.pack(side=tk.LEFT)
        self.dot_scale_slider = ttk.Scale(ds_ctrl, from_=0.1, to=3.0, variable=self.dot_scale_var, orient=tk.HORIZONTAL,
                                          command=lambda _: self._update_preview())
        self.dot_scale_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        self.dot_scale_value_label = ttk.Label(ds_ctrl, text="1.0", width=6)
        self.dot_scale_value_label.pack(side=tk.LEFT)

        self.frame_preview = ttk.LabelFrame(self, text=self._t("tm_preview"), padding=4)
        self.frame_preview.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        self.canvas = tk.Canvas(self.frame_preview, bg="#2a2a2a", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        bottom = ttk.Frame(self)
        bottom.pack(fill=tk.X, pady=(8, 0))
        self.info_label = ttk.Label(bottom, text="", foreground="#666")
        self.info_label.pack(side=tk.LEFT)
        self.btn_export = ttk.Button(bottom, text=self._t("tm_export"), command=self._on_export)
        self.btn_export.pack(side=tk.RIGHT)

    def _on_select(self):
        path = filedialog.askopenfilename(
            title=self._t("fd_select_touch"),
            filetypes=[(self._t("fd_image_files"), "*.png *.jpg *.jpeg *.bmp"), (self._t("fd_all_files"), "*.*")],
        )
        if path:
            try:
                self.src_img = Image.open(path).convert("RGBA")
                self.src_var.set(path)
                w, h = self.src_img.size
                self.path_label.config(text=f"{os.path.basename(path)}  ({w}x{h})")
                self._update_preview()
            except Exception as e:
                messagebox.showerror(self._t("error_title"), self._t("error_open_image", e=e))

    def _on_select_dot(self):
        path = filedialog.askopenfilename(
            title=self._t("tm_dot"),
            filetypes=[(self._t("fd_image_files"), "*.png *.jpg *.jpeg *.bmp"), (self._t("fd_all_files"), "*.*")],
        )
        if path:
            try:
                self.dot_img = Image.open(path).convert("RGBA")
                self.dot_var.set(path)
                w, h = self.dot_img.size
                self.dot_path_label.config(text=f"{os.path.basename(path)}  ({w}x{h})")
                self._update_preview()
            except Exception as e:
                messagebox.showerror(self._t("error_title"), self._t("error_open_image", e=e))

    def _mirror_combine(self) -> Image.Image | None:
        if self.src_img is None:
            return None
        img = self.src_img
        w, h = img.size
        gap = int(self.gap_var.get())
        # 旋转四个方向：原图(▼)、180°(▲)、90°CCW(▶)、90°CW(◀)
        rot_180 = img.rotate(180, expand=True)
        rot_90 = img.rotate(90, expand=True)    # CCW → 指向右
        rot_270 = img.rotate(270, expand=True)  # CW  → 指向左
        # 紧凑十字排列：画布 2h + gap，菱形遮罩避免重叠
        size = 2 * h + gap
        combined = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ox = (size - w) // 2  # 原图水平居中偏移
        oy = (size - w) // 2  # 旋转图垂直居中偏移
        # 生成菱形遮罩：画布被两条对角线分成上/下/左/右四个三角区
        masks = self._diamond_masks(size)
        for src, pos, region in [
            (img, (ox, 0), "top"),
            (rot_180, (ox, h + gap), "bottom"),
            (rot_90, (0, oy), "left"),
            (rot_270, (h + gap, oy), "right"),
        ]:
            layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            layer.paste(src, pos)
            r, g, b, a = layer.split()
            a = Image.composite(a, Image.new("L", (size, size), 0), masks[region])
            layer.putalpha(a)
            combined = Image.alpha_composite(combined, layer)
        # 中心 dot（使用用户手动缩放滑块）
        if self.dot_img is not None:
            dot = self.dot_img
            dot_scale = self.dot_scale_var.get()
            dot_scale = max(0.1, min(3.0, dot_scale))
            dot_w = max(1, round(dot.width * dot_scale))
            dot_h = max(1, round(dot.height * dot_scale))
            dot_resized = dot.resize((dot_w, dot_h), Image.LANCZOS)
            dx = (size - dot_w) // 2
            dy = (size - dot_h) // 2
            dot_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            dot_layer.paste(dot_resized, (dx, dy))
            combined = Image.alpha_composite(combined, dot_layer)
        return combined

    @staticmethod
    def _diamond_masks(size: int) -> dict[str, Image.Image]:
        """生成菱形四区域遮罩：上/下/左/右三角形"""
        c = size // 2
        corners = [(0, 0), (size - 1, 0), (size - 1, size - 1), (0, size - 1)]
        regions = {
            "top":    [corners[0], corners[1], (c, c)],
            "bottom": [corners[2], corners[3], (c, c)],
            "left":   [corners[0], corners[3], (c, c)],
            "right":  [corners[1], corners[2], (c, c)],
        }
        masks = {}
        for name, polygon in regions.items():
            mask = Image.new("L", (size, size), 0)
            ImageDraw.Draw(mask).polygon(polygon, fill=255)
            masks[name] = mask
        return masks

    def _update_preview(self):
        if self.src_img is None:
            return
        self.gap_value_label.config(text=str(int(self.gap_var.get())))
        self.dot_scale_value_label.config(text=f"{self.dot_scale_var.get():.1f}")
        result = self._mirror_combine()
        if result is None:
            return
        cw, ch = result.size
        self.info_label.config(text=self._t("tm_info", w=cw, h=ch))
        preview = result
        if preview.height > self.PREVIEW_MAX_H:
            ratio = self.PREVIEW_MAX_H / preview.height
            preview = preview.resize((round(preview.width * ratio), self.PREVIEW_MAX_H), Image.LANCZOS)
        new_photo = ImageTk.PhotoImage(preview)
        self.canvas.update_idletasks()
        canvas_w = max(self.canvas.winfo_width(), 400)
        canvas_h = max(self.canvas.winfo_height(), 300)
        px = (canvas_w - new_photo.width()) // 2
        py = (canvas_h - new_photo.height()) // 2
        new_id = self.canvas.create_image(px, py, anchor=tk.NW, image=new_photo)
        if self._canvas_img_id is not None:
            self.canvas.delete(self._canvas_img_id)
        self._canvas_img_id = new_id
        self.photo_ref = new_photo

    def _on_export(self):
        if self.src_img is None:
            messagebox.showwarning(self._t("warning_title"), self._t("warning_select_image"))
            return
        result = self._mirror_combine()
        if result is None:
            return
        base = Path(self.src_var.get()).stem if self.src_var.get() else "output"
        path = filedialog.asksaveasfilename(
            title=self._t("fd_save_mirror"),
            initialfile=f"{base}_compose.png",
            defaultextension=".png",
            filetypes=[("PNG", "*.png")],
        )
        if path:
            result.save(path)
            messagebox.showinfo(self._t("success_title"), self._t("success_export", path=path))


class TouchHoldComposeFrame(ttk.Frame):
    """合成 touch_hold 组合贴图：4 角 + dot + bg"""
    PREVIEW_MAX_H = 500

    def __init__(self, master):
        super().__init__(master, padding=8)
        self.mode_var = tk.StringVar(value="4corners")
        self.c1_var = tk.StringVar()
        self.c2_var = tk.StringVar()
        self.c3_var = tk.StringVar()
        self.c4_var = tk.StringVar()
        self.src_var = tk.StringVar()
        self.dot_var = tk.StringVar()
        self.bg_var = tk.StringVar()
        self.c1_img: Image.Image | None = None
        self.c2_img: Image.Image | None = None
        self.c3_img: Image.Image | None = None
        self.c4_img: Image.Image | None = None
        self.src_img: Image.Image | None = None
        self.dot_img: Image.Image | None = None
        self.bg_img: Image.Image | None = None
        self.photo_ref: ImageTk.PhotoImage | None = None
        self.gap_var = tk.IntVar(value=0)
        self.bg_scale_var = tk.DoubleVar(value=1.0)
        self.dot_scale_var = tk.DoubleVar(value=1.0)
        self._canvas_img_id = None
        self._build_ui()

    @property
    def lang(self):
        return self.winfo_toplevel().lang

    def _t(self, key: str, **kwargs) -> str:
        return I18N[self.lang][key].format(**kwargs)

    def _apply_i18n(self):
        self.mode_label.config(text=self._t("hc_mode"))
        self.mode_4c.config(text=self._t("hc_mode_4c"))
        self.mode_1s.config(text=self._t("hc_mode_1s"))
        self.src_label.config(text=self._t("hc_src"))
        self.src_btn.config(text=self._t("sj_select"))
        self.c1_label.config(text=self._t("hc_c1"))
        self.c1_btn.config(text=self._t("sj_select"))
        self.c2_label.config(text=self._t("hc_c2"))
        self.c2_btn.config(text=self._t("sj_select"))
        self.c3_label.config(text=self._t("hc_c3"))
        self.c3_btn.config(text=self._t("sj_select"))
        self.c4_label.config(text=self._t("hc_c4"))
        self.c4_btn.config(text=self._t("sj_select"))
        self.dot_label.config(text=self._t("hc_dot"))
        self.btn_select_dot.config(text=self._t("sj_select"))
        self.bg_label.config(text=self._t("hc_bg"))
        self.btn_select_bg.config(text=self._t("sj_select"))
        self.gap_label.config(text=self._t("hc_gap"))
        self.bg_scale_label.config(text=self._t("hc_bg_scale"))
        self.dot_scale_label.config(text=self._t("hc_dot_scale"))
        self.frame_preview.config(text=self._t("hc_preview"))
        self.btn_export.config(text=self._t("hc_export"))
        self._update_preview()

    def _build_ui(self):
        # 模式选择
        mode_frame = ttk.Frame(self)
        mode_frame.pack(fill=tk.X)
        self.mode_label = ttk.Label(mode_frame, text=self._t("hc_mode"), width=12)
        self.mode_label.pack(side=tk.LEFT)
        self.mode_4c = ttk.Radiobutton(mode_frame, text=self._t("hc_mode_4c"), variable=self.mode_var, value="4corners", command=self._on_mode_change)
        self.mode_4c.pack(side=tk.LEFT, padx=4)
        self.mode_1s = ttk.Radiobutton(mode_frame, text=self._t("hc_mode_1s"), variable=self.mode_var, value="single", command=self._on_mode_change)
        self.mode_1s.pack(side=tk.LEFT, padx=4)

        # 4 角输入
        self._4c_frame = ttk.Frame(self)
        self._4c_frame.pack(fill=tk.X)
        self.c1_label, self.c1_path, self.c1_btn = self._image_row(self._4c_frame, self._t("hc_c1"), self.c1_var, self._on_select_c1)
        self.c2_label, self.c2_path, self.c2_btn = self._image_row(self._4c_frame, self._t("hc_c2"), self.c2_var, self._on_select_c2)
        self.c3_label, self.c3_path, self.c3_btn = self._image_row(self._4c_frame, self._t("hc_c3"), self.c3_var, self._on_select_c3)
        self.c4_label, self.c4_path, self.c4_btn = self._image_row(self._4c_frame, self._t("hc_c4"), self.c4_var, self._on_select_c4)

        # 单图输入
        self._1s_frame = ttk.Frame(self)
        self.src_label, self.src_path, self.src_btn = self._image_row(self._1s_frame, self._t("hc_src"), self.src_var, self._on_select_src)
        self._1s_frame.pack_forget()

        # dot + bg + gap
        self._dot_frame = ttk.Frame(self)
        self._dot_frame.pack(fill=tk.X)
        self.dot_label = ttk.Label(self._dot_frame, text=self._t("hc_dot"), width=12)
        self.dot_label.pack(side=tk.LEFT)
        self.btn_select_dot = ttk.Button(self._dot_frame, text=self._t("sj_select"), command=self._on_select_dot)
        self.btn_select_dot.pack(side=tk.LEFT, padx=(0, 8))
        self.dot_path_label = ttk.Label(self._dot_frame, text=self._t("no_file"), foreground="gray")
        self.dot_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self._bg_frame = ttk.Frame(self)
        self._bg_frame.pack(fill=tk.X)
        self.bg_label = ttk.Label(self._bg_frame, text=self._t("hc_bg"), width=12)
        self.bg_label.pack(side=tk.LEFT)
        self.btn_select_bg = ttk.Button(self._bg_frame, text=self._t("sj_select"), command=self._on_select_bg)
        self.btn_select_bg.pack(side=tk.LEFT, padx=(0, 8))
        self.bg_path_label = ttk.Label(self._bg_frame, text=self._t("no_file"), foreground="gray")
        self.bg_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ctrl = ttk.Frame(self)
        ctrl.pack(fill=tk.X, pady=(4, 0))
        self.gap_label = ttk.Label(ctrl, text=self._t("hc_gap"), width=12)
        self.gap_label.pack(side=tk.LEFT)
        self.gap_slider = ttk.Scale(ctrl, from_=0, to=300, variable=self.gap_var, orient=tk.HORIZONTAL, command=lambda _: self._update_preview())
        self.gap_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        self.gap_value_label = ttk.Label(ctrl, text="0", width=6)
        self.gap_value_label.pack(side=tk.LEFT)

        bg_ctrl = ttk.Frame(self)
        bg_ctrl.pack(fill=tk.X, pady=(2, 0))
        self.bg_scale_label = ttk.Label(bg_ctrl, text=self._t("hc_bg_scale"), width=12)
        self.bg_scale_label.pack(side=tk.LEFT)
        self.bg_scale_slider = ttk.Scale(bg_ctrl, from_=0.1, to=3.0, variable=self.bg_scale_var, orient=tk.HORIZONTAL, command=lambda _: self._update_preview())
        self.bg_scale_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        self.bg_scale_value_label = ttk.Label(bg_ctrl, text="1.0", width=6)
        self.bg_scale_value_label.pack(side=tk.LEFT)

        ds_ctrl = ttk.Frame(self)
        ds_ctrl.pack(fill=tk.X, pady=(2, 0))
        self.dot_scale_label = ttk.Label(ds_ctrl, text=self._t("hc_dot_scale"), width=12)
        self.dot_scale_label.pack(side=tk.LEFT)
        self.dot_scale_slider = ttk.Scale(ds_ctrl, from_=0.1, to=3.0, variable=self.dot_scale_var, orient=tk.HORIZONTAL, command=lambda _: self._update_preview())
        self.dot_scale_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        self.dot_scale_value_label = ttk.Label(ds_ctrl, text="1.0", width=6)
        self.dot_scale_value_label.pack(side=tk.LEFT)

        self.frame_preview = ttk.LabelFrame(self, text=self._t("hc_preview"), padding=4)
        self.frame_preview.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        self.canvas = tk.Canvas(self.frame_preview, bg="#2a2a2a", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        bottom = ttk.Frame(self)
        bottom.pack(fill=tk.X, pady=(8, 0))
        self.info_label = ttk.Label(bottom, text="", foreground="#666")
        self.info_label.pack(side=tk.LEFT)
        self.btn_export = ttk.Button(bottom, text=self._t("hc_export"), command=self._on_export)
        self.btn_export.pack(side=tk.RIGHT)

    def _image_row(self, parent, label_text, var, command):
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=1)
        lbl = ttk.Label(row, text=label_text, width=14)
        lbl.pack(side=tk.LEFT)
        btn = ttk.Button(row, text=self._t("sj_select"), command=command)
        btn.pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        path_lbl = ttk.Label(row, text="", foreground="gray")
        path_lbl.pack(side=tk.LEFT, padx=4)
        return lbl, path_lbl, btn

    def _on_mode_change(self):
        if self.mode_var.get() == "4corners":
            self._1s_frame.pack_forget()
            self._4c_frame.pack(fill=tk.X, before=self._dot_frame)
        else:
            self._4c_frame.pack_forget()
            self._1s_frame.pack(fill=tk.X, before=self._dot_frame)
        # 切换模式时清空预览
        self.canvas.delete("all")
        self.photo_ref = None
        self.info_label.config(text="")

    def _open_image(self, path: str) -> Image.Image | None:
        try:
            return Image.open(path).convert("RGBA")
        except Exception as e:
            messagebox.showerror(self._t("error_title"), self._t("error_open_image", e=e))
            return None

    def _on_select_c1(self):
        path = filedialog.askopenfilename(title="tr (top-right)", filetypes=[(self._t("fd_image_files"), "*.png *.jpg *.jpeg *.bmp"), (self._t("fd_all_files"), "*.*")])
        if path:
            img = self._open_image(path)
            if img:
                self.c1_img = img
                self.c1_var.set(path)
                self.c1_path.config(text=f"{os.path.basename(path)}  ({img.width}x{img.height})")
                self._update_preview()

    def _on_select_c2(self):
        path = filedialog.askopenfilename(title="br (bottom-right)", filetypes=[(self._t("fd_image_files"), "*.png *.jpg *.jpeg *.bmp"), (self._t("fd_all_files"), "*.*")])
        if path:
            img = self._open_image(path)
            if img:
                self.c2_img = img
                self.c2_var.set(path)
                self.c2_path.config(text=f"{os.path.basename(path)}  ({img.width}x{img.height})")
                self._update_preview()

    def _on_select_c3(self):
        path = filedialog.askopenfilename(title="bl (bottom-left)", filetypes=[(self._t("fd_image_files"), "*.png *.jpg *.jpeg *.bmp"), (self._t("fd_all_files"), "*.*")])
        if path:
            img = self._open_image(path)
            if img:
                self.c3_img = img
                self.c3_var.set(path)
                self.c3_path.config(text=f"{os.path.basename(path)}  ({img.width}x{img.height})")
                self._update_preview()

    def _on_select_c4(self):
        path = filedialog.askopenfilename(title="tl (top-left)", filetypes=[(self._t("fd_image_files"), "*.png *.jpg *.jpeg *.bmp"), (self._t("fd_all_files"), "*.*")])
        if path:
            img = self._open_image(path)
            if img:
                self.c4_img = img
                self.c4_var.set(path)
                self.c4_path.config(text=f"{os.path.basename(path)}  ({img.width}x{img.height})")
                self._update_preview()

    def _on_select_src(self):
        path = filedialog.askopenfilename(title=self._t("hc_src"), filetypes=[(self._t("fd_image_files"), "*.png *.jpg *.jpeg *.bmp"), (self._t("fd_all_files"), "*.*")])
        if path:
            img = self._open_image(path)
            if img:
                self.src_img = img
                self.src_var.set(path)
                self.src_path.config(text=f"{os.path.basename(path)}  ({img.width}x{img.height})")
                self._update_preview()

    def _on_select_dot(self):
        path = filedialog.askopenfilename(title="dot", filetypes=[(self._t("fd_image_files"), "*.png *.jpg *.jpeg *.bmp"), (self._t("fd_all_files"), "*.*")])
        if path:
            img = self._open_image(path)
            if img:
                self.dot_img = img
                self.dot_var.set(path)
                self.dot_path_label.config(text=f"{os.path.basename(path)}  ({img.width}x{img.height})")
                self._update_preview()

    def _on_select_bg(self):
        path = filedialog.askopenfilename(title="bg", filetypes=[(self._t("fd_image_files"), "*.png *.jpg *.jpeg *.bmp"), (self._t("fd_all_files"), "*.*")])
        if path:
            img = self._open_image(path)
            if img:
                self.bg_img = img
                self.bg_var.set(path)
                self.bg_path_label.config(text=f"{os.path.basename(path)}  ({img.width}x{img.height})")
                self._update_preview()

    def _get_corners(self) -> list[tuple[Image.Image, str]] | None:
        # 旋转角度：红315° 黄225° 绿135° 蓝45°
        # expand=True 保留完整内容，然后缩小 80% 避免过大
        SHRINK = 0.8
        def _rot(img: Image.Image, angle: int) -> Image.Image:
            rotated = img.rotate(angle, expand=True)
            return rotated.resize((round(rotated.width * SHRINK), round(rotated.height * SHRINK)), Image.LANCZOS)
        if self.mode_var.get() == "single":
            if self.src_img is None:
                return None
            src = self.src_img
            return [
                (_rot(src, 315), "tr"),   # 红
                (_rot(src, 225), "br"),   # 黄
                (_rot(src, 135), "bl"),   # 绿
                (_rot(src, 45), "tl"),    # 蓝
            ]
        else:
            result = []
            if self.c1_img is not None:
                result.append((_rot(self.c1_img, 315), "tr"))
            if self.c2_img is not None:
                result.append((_rot(self.c2_img, 225), "br"))
            if self.c3_img is not None:
                result.append((_rot(self.c3_img, 135), "bl"))
            if self.c4_img is not None:
                result.append((_rot(self.c4_img, 45), "tl"))
            return result if result else None

    def _compose(self) -> Image.Image | None:
        corners = self._get_corners()
        if corners is None:
            return None
        gap = int(self.gap_var.get())
        bg_scale = self.bg_scale_var.get()
        # 逻辑画布：由四角贴图决定
        if self.mode_var.get() == "single" and self.src_img is not None:
            inner = 2 * max(self.src_img.width, self.src_img.height)
        else:
            raw = [x for x in [self.c1_img, self.c2_img, self.c3_img, self.c4_img] if x is not None]
            if raw:
                inner = 2 * max(max(x.width for x in raw), max(x.height for x in raw))
            else:
                inner = 512
        # bg 尺寸（乘数模式）
        bg_size = 0
        if self.bg_img is not None:
            bg_size = max(1, round(inner * bg_scale))
        # 画布固定为 inner
        size = inner
        combined = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        # 背景 bg：完全独立，居中缩放
        if self.bg_img is not None:
            bg_resized = self.bg_img.resize((bg_size, bg_size), Image.LANCZOS)
            bg_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            bx = (size - bg_size) // 2
            by = (size - bg_size) // 2
            bg_layer.paste(bg_resized, (bx, by))
            combined = Image.alpha_composite(combined, bg_layer)
        # 四角放置：gap 控制向中心收缩
        for img, key in corners:
            if key == "tr":
                px = inner - img.width - max(0, gap)
                py = max(0, gap)
            elif key == "br":
                px = inner - img.width - max(0, gap)
                py = inner - img.height - max(0, gap)
            elif key == "bl":
                px = max(0, gap)
                py = inner - img.height - max(0, gap)
            else:  # tl
                px = max(0, gap)
                py = max(0, gap)
            layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            layer.paste(img, (px, py))
            combined = Image.alpha_composite(combined, layer)
        # dot 居中最上层
        if self.dot_img is not None:
            dot = self.dot_img
            dot_scale = self.dot_scale_var.get()
            dot_scale = max(0.1, min(3.0, dot_scale))
            dot_w = max(1, round(dot.width * dot_scale))
            dot_h = max(1, round(dot.height * dot_scale))
            dot_resized = dot.resize((dot_w, dot_h), Image.LANCZOS)
            dx = (size - dot_w) // 2
            dy = (size - dot_h) // 2
            dot_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            dot_layer.paste(dot_resized, (dx, dy))
            combined = Image.alpha_composite(combined, dot_layer)
        return combined

    def _update_preview(self):
        result = self._compose()
        if result is None:
            return
        self.gap_value_label.config(text=str(int(self.gap_var.get())))
        self.bg_scale_value_label.config(text=f"{self.bg_scale_var.get():.1f}")
        self.dot_scale_value_label.config(text=f"{self.dot_scale_var.get():.1f}")
        cw, ch = result.size
        self.info_label.config(text=self._t("hc_info", w=cw, h=ch))
        self.canvas.update_idletasks()
        canvas_w = max(self.canvas.winfo_width(), 400)
        canvas_h = max(self.canvas.winfo_height(), 300)
        # 缩放预览以适应 canvas
        scale = min(canvas_w / cw, canvas_h / ch, 1.0)
        preview = result.resize((round(cw * scale), round(ch * scale)), Image.LANCZOS)
        new_photo = ImageTk.PhotoImage(preview)
        px = (canvas_w - new_photo.width()) // 2
        py = (canvas_h - new_photo.height()) // 2
        new_id = self.canvas.create_image(px, py, anchor=tk.NW, image=new_photo)
        if self._canvas_img_id is not None:
            self.canvas.delete(self._canvas_img_id)
        self._canvas_img_id = new_id
        self.photo_ref = new_photo

    def _on_export(self):
        result = self._compose()
        if result is None:
            messagebox.showwarning(self._t("warning_title"), self._t("warning_select_image"))
            return
        base = "touch_hold"
        if self.mode_var.get() == "single" and self.src_var.get():
            base = Path(self.src_var.get()).stem
        path = filedialog.asksaveasfilename(
            title=self._t("fd_save_compose"),
            initialfile=f"{base}_compose.png",
            defaultextension=".png",
            filetypes=[("PNG", "*.png")],
        )
        if path:
            result.save(path)
            messagebox.showinfo(self._t("success_title"), self._t("success_export", path=path))


class PpuFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=8)
        self.image_var = tk.StringVar()
        self.units_var = tk.StringVar()
        self.ppu_var = tk.StringVar()
        self.result_var = tk.StringVar()
        self.manual_w_var = tk.StringVar()
        self.manual_h_var = tk.StringVar()
        self._build_ui()

    @property
    def lang(self):
        return self.winfo_toplevel().lang

    def _t(self, key: str, **kwargs) -> str:
        return I18N[self.lang][key].format(**kwargs)

    def _apply_i18n(self):
        self.image_label.config(text=self._t("ppu_image"))
        self.select_btn.config(text=self._t("ppu_select"))
        self.manual_label.config(text=self._t("ppu_manual"))
        self.units_label.config(text=self._t("ppu_units"))
        self.units_hint_label.config(text=self._t("ppu_units_default"))
        self.ppu_label.config(text=self._t("ppu_current"))
        self.ppu_hint_label.config(text=self._t("ppu_units_hint"))
        self.calc_h_btn.config(text=self._t("ppu_calc_h"))
        self.calc_w_btn.config(text=self._t("ppu_calc_w"))
        self.calc_size_btn.config(text=self._t("ppu_calc_size"))

    def _build_ui(self):
        row = ttk.Frame(self)
        row.pack(fill=tk.X, pady=2)
        self.image_label = ttk.Label(row, text=self._t("ppu_image"), width=14)
        self.image_label.pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.image_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        self.select_btn = ttk.Button(row, text=self._t("ppu_select"), command=self._select_image)
        self.select_btn.pack(side=tk.LEFT)
        self.manual_label = self._entry(self._t("ppu_manual"), self.manual_w_var, self.manual_h_var)
        self.units_label, self.units_hint_label = self._single_entry(self._t("ppu_units"), self.units_var, hint_key="ppu_units_default")
        self.ppu_label, self.ppu_hint_label = self._single_entry(self._t("ppu_current"), self.ppu_var, hint_key="ppu_units_hint")
        btns = ttk.Frame(self)
        btns.pack(fill=tk.X, pady=6)
        self.calc_h_btn = ttk.Button(btns, text=self._t("ppu_calc_h"), command=lambda: self._calc("h"))
        self.calc_h_btn.pack(side=tk.LEFT)
        self.calc_w_btn = ttk.Button(btns, text=self._t("ppu_calc_w"), command=lambda: self._calc("w"))
        self.calc_w_btn.pack(side=tk.LEFT, padx=8)
        self.calc_size_btn = ttk.Button(btns, text=self._t("ppu_calc_size"), command=self._calc_size)
        self.calc_size_btn.pack(side=tk.LEFT)
        ttk.Label(self, textvariable=self.result_var, foreground="#333", wraplength=900).pack(fill=tk.X, pady=8)

    def _entry(self, label, var1, var2):
        row = ttk.Frame(self)
        row.pack(fill=tk.X, pady=2)
        lbl = ttk.Label(row, text=label, width=14)
        lbl.pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=var1, width=10).pack(side=tk.LEFT, padx=4)
        ttk.Entry(row, textvariable=var2, width=10).pack(side=tk.LEFT, padx=4)
        return lbl

    def _single_entry(self, label, var, hint_key=None):
        row = ttk.Frame(self)
        row.pack(fill=tk.X, pady=2)
        lbl = ttk.Label(row, text=label, width=14)
        lbl.pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=var, width=12).pack(side=tk.LEFT, padx=4)
        hint_lbl = None
        if hint_key:
            hint_lbl = ttk.Label(row, text=self._t(hint_key), foreground="gray")
            hint_lbl.pack(side=tk.LEFT)
        return lbl, hint_lbl

    def _select_image(self):
        path = filedialog.askopenfilename(title=self._t("fd_select_image"), filetypes=[(self._t("fd_image_files"), "*.png *.jpg *.jpeg *.bmp")])
        if path:
            self.image_var.set(path)
            with Image.open(path) as img:
                self.manual_w_var.set(str(img.width))
                self.manual_h_var.set(str(img.height))

    def _dims(self) -> tuple[float, float]:
        if self.manual_w_var.get() and self.manual_h_var.get():
            try:
                return float(self.manual_w_var.get()), float(self.manual_h_var.get())
            except ValueError:
                raise ValueError(self._t("warning_fill_fields"))
        if not self.image_var.get():
            raise ValueError(self._t("ppu_hint"))
        with Image.open(self.image_var.get()) as img:
            return float(img.width), float(img.height)

    def _calc(self, axis: str):
        try:
            w, h = self._dims()
            if not self.units_var.get():
                raise ValueError(self._t("warning_fill_fields"))
            units = float(self.units_var.get())
            ppu = (h if axis == "h" else w) / units
            self.ppu_var.set(f"{ppu:.2f}")
            self.result_var.set(self._t("ppu_calc_result", ppu=f"{ppu:.2f}", w=f"{w / ppu:.3f}", h=f"{h / ppu:.3f}"))
        except ValueError as e:
            messagebox.showwarning(self._t("warning_title"), str(e))
        except Exception as e:
            messagebox.showerror(self._t("error_title"), str(e))

    def _calc_size(self):
        try:
            w, h = self._dims()
            if not self.ppu_var.get():
                raise ValueError(self._t("warning_fill_fields"))
            ppu = float(self.ppu_var.get())
            self.result_var.set(self._t("ppu_size_result", ppu=f"{ppu:.2f}", w=f"{w / ppu:.3f}", h=f"{h / ppu:.3f}"))
        except ValueError as e:
            messagebox.showwarning(self._t("warning_title"), str(e))
        except Exception as e:
            messagebox.showerror(self._t("error_title"), str(e))


class PaletteFrame(ttk.Frame):
    PRESET_COLORS_ZH = [
        ("#FF4A4A", "红"), ("#FF8C2E", "橙"), ("#FFD84A", "黄"), ("#7AFF70", "绿"),
        ("#5AD7FF", "蓝"), ("#8A7AFF", "紫"), ("#FF7ADE", "粉"), ("#FFFFFF", "白"),
        ("#00E5FF", "青"), ("#FF5733", "朱"), ("#C678DD", "薰"), ("#E5C07B", "杏"),
        ("#528BFF", "靛"), ("#61AFEF", "天"), ("#98C379", "苔"), ("#D19A66", "棕"),
    ]
    PRESET_COLORS_EN = [
        ("#FF4A4A", "Red"), ("#FF8C2E", "Orng"), ("#FFD84A", "Yelw"), ("#7AFF70", "Grn"),
        ("#5AD7FF", "Blue"), ("#8A7AFF", "Purp"), ("#FF7ADE", "Pink"), ("#FFFFFF", "Wht"),
        ("#00E5FF", "Cyan"), ("#FF5733", "Coral"), ("#C678DD", "Plum"), ("#E5C07B", "Gold"),
        ("#528BFF", "Indg"), ("#61AFEF", "Sky"), ("#98C379", "Moss"), ("#D19A66", "Brwn"),
    ]

    def __init__(self, master):
        super().__init__(master, padding=8)
        self._updating = False
        self.main_var = tk.StringVar()
        self.h_var = tk.IntVar(value=0)
        self.s_var = tk.IntVar(value=100)
        self.v_var = tk.IntVar(value=100)
        self.preset_canvas_texts: list[tuple[tk.Canvas, int]] = []
        self._build_ui()
        self._sync_from_hex()

    @property
    def lang(self):
        return self.winfo_toplevel().lang

    def _t(self, key: str, **kwargs) -> str:
        return I18N[self.lang][key].format(**kwargs)

    def _apply_i18n(self):
        self.hex_label.config(text=self._t("pal_hex"))
        self.apply_btn.config(text=self._t("pal_apply"))
        self.copy_btn.config(text=self._t("pal_copy"))
        self.hsv_frame.config(text=self._t("pal_hsv"))
        self.h_label.config(text=self._t("pal_h"))
        self.s_label.config(text=self._t("pal_s"))
        self.v_label.config(text=self._t("pal_v"))
        self.preset_frame.config(text=self._t("pal_preset"))
        presets = self.PRESET_COLORS_EN if self.lang == "en" else self.PRESET_COLORS_ZH
        for (canvas, text_id), (_, label) in zip(self.preset_canvas_texts, presets):
            canvas.itemconfig(text_id, text=label)

    def _build_ui(self):
        # --- 顶部：手动输入 + 按钮 ---
        row = ttk.Frame(self)
        row.pack(fill=tk.X, pady=2)
        self.hex_label = ttk.Label(row, text=self._t("pal_hex"), width=10)
        self.hex_label.pack(side=tk.LEFT)
        self.hex_entry = ttk.Entry(row, textvariable=self.main_var, width=14)
        self.hex_entry.pack(side=tk.LEFT)
        self.hex_entry.bind("<Return>", lambda _: self._sync_from_hex())
        self.apply_btn = ttk.Button(row, text=self._t("pal_apply"), command=self._sync_from_hex)
        self.apply_btn.pack(side=tk.LEFT, padx=4)
        self.copy_btn = ttk.Button(row, text=self._t("pal_copy"), command=self._copy_hex)
        self.copy_btn.pack(side=tk.LEFT, padx=8)

        # --- 调色盘区域：左侧 HSV 滑块 + 右侧色彩预览 ---
        picker_frame = ttk.Frame(self)
        picker_frame.pack(fill=tk.X, pady=(8, 4))

        # 左侧：HSV 滑块
        self.hsv_frame = ttk.LabelFrame(picker_frame, text=self._t("pal_hsv"), padding=8)
        self.hsv_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        self.h_label = self._add_hsv_slider(self.hsv_frame, self._t("pal_h"), self.h_var, 0, 360)
        self.s_label = self._add_hsv_slider(self.hsv_frame, self._t("pal_s"), self.s_var, 0, 100)
        self.v_label = self._add_hsv_slider(self.hsv_frame, self._t("pal_v"), self.v_var, 0, 100)

        # 右侧：大色块预览 + hex 显示
        preview_right = ttk.Frame(picker_frame)
        preview_right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.color_preview = tk.Canvas(preview_right, height=120, width=220, bg="#5AD7FF", highlightthickness=1, highlightbackground="#999")
        self.color_preview.pack(anchor=tk.CENTER, pady=(8, 4))
        self.hex_display = ttk.Label(preview_right, text="#5AD7FF", font=("Consolas", 16, "bold"), anchor=tk.CENTER)
        self.hex_display.pack(anchor=tk.CENTER)
        self.hsv_display = ttk.Label(preview_right, text="H=200  S=100  V=100", font=("Consolas", 10), anchor=tk.CENTER, foreground="#666")
        self.hsv_display.pack(anchor=tk.CENTER, pady=(2, 0))

        # --- 预设色块 ---
        self.preset_frame = ttk.LabelFrame(self, text=self._t("pal_preset"), padding=6)
        self.preset_frame.pack(fill=tk.X, pady=(4, 4))
        preset_grid = ttk.Frame(self.preset_frame)
        preset_grid.pack(anchor=tk.W)
        self.preset_canvas_texts.clear()
        for i, (hex_val, label) in enumerate(self.PRESET_COLORS_ZH):
            row_i = i // 8
            col_i = i % 8
            btn = tk.Canvas(preset_grid, width=36, height=28, highlightthickness=1, highlightbackground="#bbb", cursor="hand2")
            btn.grid(row=row_i, column=col_i, padx=3, pady=3)
            btn.create_rectangle(1, 1, 35, 27, fill=hex_val, outline="#888")
            text_id = btn.create_text(18, 15, text=label, fill="#000" if sum(int(hex_val[j:j+2], 16) for j in (1, 3, 5)) > 420 else "#fff", font=("微软雅黑", 7))
            self.preset_canvas_texts.append((btn, text_id))
            btn.bind("<Button-1>", lambda _, h=hex_val: self._pick_preset(h))

    def _add_hsv_slider(self, parent, label, var, from_, to):
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=2)
        lbl = ttk.Label(row, text=label, width=12)
        lbl.pack(side=tk.LEFT)
        slider = ttk.Scale(row, from_=from_, to=to, variable=var, orient=tk.HORIZONTAL, length=180,
                           command=lambda _: self._on_slider_change())
        slider.pack(side=tk.LEFT, padx=4)
        val_label = ttk.Label(row, text=str(var.get()), width=5)
        val_label.pack(side=tk.LEFT)
        var._val_label = val_label
        slider.bind("<ButtonRelease-1>", lambda _: self._on_slider_change())
        return lbl

    def _on_slider_change(self):
        if self._updating:
            return
        self._updating = True
        self.h_var._val_label.config(text=str(self.h_var.get()))
        self.s_var._val_label.config(text=str(self.s_var.get()))
        self.v_var._val_label.config(text=str(self.v_var.get()))
        h = self.h_var.get() / 360.0
        s = self.s_var.get() / 100.0
        v = self.v_var.get() / 100.0
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        hex_val = rgb_to_hex((int(r * 255), int(g * 255), int(b * 255)))
        self.main_var.set(hex_val)
        self._update_color_display(hex_val)
        self._updating = False

    def _sync_from_hex(self):
        if self._updating:
            return
        if not self.main_var.get().strip():
            return
        self._updating = True
        try:
            r, g, b = parse_hex_color(self.main_var.get())
            h_val, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            self.h_var.set(round(h_val * 360))
            self.s_var.set(round(s * 100))
            self.v_var.set(round(v * 100))
            self.h_var._val_label.config(text=str(self.h_var.get()))
            self.s_var._val_label.config(text=str(self.s_var.get()))
            self.v_var._val_label.config(text=str(self.v_var.get()))
            self._update_color_display(self.main_var.get().upper())
        except Exception as e:
            messagebox.showerror(self._t("error_title"), self._t("error_color_format", e=e))
        self._updating = False

    def _update_color_display(self, hex_val: str):
        self.color_preview.config(bg=hex_val)
        self.hex_display.config(text=hex_val.upper())
        self.hsv_display.config(text=f"H={self.h_var.get()}  S={self.s_var.get()}  V={self.v_var.get()}")

    def _pick_preset(self, hex_val: str):
        self.main_var.set(hex_val)
        self._sync_from_hex()

    def _copy_hex(self):
        hex_val = self.main_var.get().strip().upper()
        self.clipboard_clear()
        self.clipboard_append(hex_val)
        messagebox.showinfo(self._t("success_title"), self._t("success_copy", val=hex_val))


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.resizable(True, True)
        self.lang = "zh"
        self._build_ui()

    def _build_ui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=(0, 80))

        self.lang_btn = ttk.Button(self, text=I18N[self.lang]["lang_name"], command=self._toggle_lang)
        self.lang_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-8, y=0)

        tab_keys = ["tab_hold", "tab_skinjson", "tab_color", "tab_mirror", "tab_holdcomp", "tab_ppu", "tab_palette"]
        self.frames = [
            Hold9SliceFrame(self.notebook),
            SkinJsonFrame(self.notebook),
            ColorVariantFrame(self.notebook),
            TouchMirrorFrame(self.notebook),
            TouchHoldComposeFrame(self.notebook),
            PpuFrame(self.notebook),
            PaletteFrame(self.notebook),
        ]
        for frame, key in zip(self.frames, tab_keys):
            self.notebook.add(frame, text=I18N[self.lang][key])

    def _toggle_lang(self):
        self.lang = "en" if self.lang == "zh" else "zh"
        self.lang_btn.config(text=I18N[self.lang]["lang_name"])
        tab_keys = ["tab_hold", "tab_skinjson", "tab_color", "tab_mirror", "tab_holdcomp", "tab_ppu", "tab_palette"]
        for i, key in enumerate(tab_keys):
            self.notebook.tab(i, text=I18N[self.lang][key])
        for frame in self.frames:
            frame._apply_i18n()


def main():
    app = App()
    app.minsize(1000, 680)
    app.update_idletasks()
    sw = app.winfo_screenwidth()
    sh = app.winfo_screenheight()
    ww, wh = 1180, 760
    app.geometry(f"{ww}x{wh}+{(sw - ww) // 2}+{(sh - wh) // 2}")
    app.mainloop()


if __name__ == "__main__":
    main()
