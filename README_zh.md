**[English](README.md)** | **中文**

# AstroDX Skin Developer Tool

（项目使用AI辅助创建）

一款用于开发、调试和预览 [AstroDX](https://github.com/2394425147/astrodx) 自定义皮肤的桌面工具。整合了九宫格拉伸预览、skin.json 验证/生成、颜色变体批量生成、PPU 计算、调色盘以及 Touch 贴图合成等多项功能。

## 功能

### Hold 九宫格拉伸

针对 `hold.png` 等纵向拉伸贴图，提供直观的九宫格切割与实时拉伸预览：

- 可调节 Top / Bottom 区域高度（0–300 px）
- 支持 0x ~ 10.0x 拉伸倍率
- 左右双视图实时对比：原图切分线 vs 拉伸结果
- 一键导出拉伸后的 PNG 贴图

```
┌─────────────────────────────────────────────┐
│  [选择图片]  文件名 (宽x高)                   │
├──────────────────┬──────────────────────────┤
│  原图 + 切分线    │     拉伸结果              │
│  ┌────────────┐  │  ┌────────────────────┐  │
│  │  top 区域   │  │  │  top（不变）        │  │
│  │────────────│  │  │────────────────────│  │
│  │  中间区域   │  │  │  中间区域（拉伸）   │  │
│  │────────────│  │  │────────────────────│  │
│  │  bottom区域 │  │  │  bottom（不变）     │  │
│  └────────────┘  │  └────────────────────┘  │
├──────────────────┴──────────────────────────┤
│  Top:     [====●=========] 90               │
│  Bottom:  [====●=========] 90               │
│  拉伸倍率: [=====●========] 3.0x            │
│  可拉伸区: 120px (50.0%)    [导出拉伸结果...] │
└─────────────────────────────────────────────┘
```

### skin.json 验证与生成

对皮肤配置文件 `skin.json` 进行结构校验，并支持自动生成：

- 检查必需字段（`name`, `designer`）
- 验证颜色字段格式（`tap_color`, `each_color`, `break_color`, `mine_color`, `slide_color`）
- 校验 sprite 定义中的 `pivot_x`, `pivot_y`, `ppu`, `top`, `bottom` 数值合法性
- 检测贴图路径是否存在
- 识别文件夹中未被引用的多余图片
- 一键生成符合规范的 `skin.json`
- 支持 PPU 自动计算（按 ring / fan / other 分组）

### 颜色变体批量生成

基于主贴图自动生成各类型变体贴图（Each / Break / Mine / Slide / Alt / Active 等）：

- 支持多种贴图族：`tap`, `star`, `hold`, `touch`, `touch_dot`, `arrow`, `fan`
- 自动识别当前贴图族所需的变体类型
- 使用 HSV 色彩空间保持原图明暗关系
- 支持复合变体如 `each_active`, `break_active` 等

### Touch 贴图合成

用于合成 Touch 贴图的菱形四方向组合贴图：

- 将原图旋转 0° / 90° / 180° / 270° 拼成菱形布局
- 支持自定义间距（Gap）与 Dot 缩放比例
- 实时预览合成效果，导出合并后的 PNG

### Touch Hold 合成

用于合成 Touch Hold 组合贴图（4 角 + dot + bg）：

- **4 角独立模式** — 分别导入 tr / br / bl / tl 四个角贴图
- **1 图复制模式** — 用单张贴图自动生成四个旋转角（适用于 break / mine 等）
- 支持背景贴图缩放、中心 dot 缩放、间距调节
- 实时预览与导出

### PPU 计算器

帮助皮肤作者计算贴图在游戏中的显示尺寸：

- 支持按宽度或高度计算 PPU
- 支持按 PPU 反算游戏单位显示尺寸
- 内置常用 PPU 默认值（ring: 115, fan: 58）
- 自动读取贴图像素尺寸

### 调色盘

轻量级 HSV 调色工具：

- HSV 滑块精确调色
- 16 种预设常用色
- 一键复制 HEX 色值，实时大色块预览

### 中英文切换

界面支持中文 / English 双语，一键切换。

## 安装

1. 克隆或下载本仓库：

```bash
git clone <repo-url>
cd adxskin
```

2. 安装依赖（仅需 Pillow）：

```bash
pip install Pillow
```

## 使用

```bash
python AstroDX_Skin_Developer_Tool.py
```

启动后显示多标签页的 Tkinter 窗口，每个标签对应一个功能模块。

## 项目结构

```
├── AstroDX_Skin_Developer_Tool.py   # 主工具（GUI）
├── README.md                         # English README
├── README_zh.md                      # 中文 README（本文件）
```

## 依赖

- Python 3.10+
- Pillow

## 许可证

GNU General Public License v3.0
