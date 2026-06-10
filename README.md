**English** | **[中文](README_zh.md)**

# AstroDX Skin Developer Tool

(Project Created with AI Assistance)

A desktop tool for developing, debugging, and previewing custom skins for [AstroDX](https://github.com/2394425147/astrodx). It combines 9-slice stretching preview, skin.json validation/generation, batch color variant generation, PPU calculation, a color picker, and Touch sprite composition into a single application.

## Features

### Hold 9-Slice Stretching

Preview and export vertically stretched Hold sprites while keeping top/bottom edges intact:

- Adjustable Top / Bottom region height (0–300 px)
- Stretch scale from 0.1x to 10.0x
- Side-by-side real-time preview: original with slice lines vs stretched result
- One-click PNG export

```
┌─────────────────────────────────────────────┐
│  [Select Image]  filename (WxH)    [EN/中文] │
├──────────────────┬──────────────────────────┤
│  Original + Slices│     Stretch Result       │
│  ┌────────────┐  │  ┌────────────────────┐  │
│  │  top region │  │  │  top (unchanged)    │  │
│  │────────────│  │  │────────────────────│  │
│  │  middle     │  │  │  middle (stretched) │  │
│  │────────────│  │  │────────────────────│  │
│  │  bottom     │  │  │  bottom (unchanged) │  │
│  └────────────┘  │  └────────────────────┘  │
├──────────────────┴──────────────────────────┤
│  Top:     [====●=========] 90               │
│  Bottom:  [====●=========] 90               │
│  Scale:   [=====●========] 3.0x            │
│  Stretchable: 120px (50.0%)  [Export...]    │
└─────────────────────────────────────────────┘
```

### skin.json Validation & Generation

Validate and generate the skin configuration file `skin.json`:

- Check required fields (`name`, `designer`)
- Validate color field format (`tap_color`, `each_color`, `break_color`, `mine_color`, `slide_color`)
- Verify numeric values in sprite definitions (`pivot_x`, `pivot_y`, `ppu`, `top`, `bottom`)
- Detect missing sprite file paths
- Identify unused images in the skin folder
- One-click generation of a compliant `skin.json`
- Auto PPU calculation by group (ring / fan / other)

### Batch Color Variant Generation

Automatically generate variant sprites (Each / Break / Mine / Slide / Alt / Active, etc.) from a base texture:

- Supports sprite families: `tap`, `star`, `hold`, `touch`, `touch_dot`, `arrow`, `fan`
- Auto-detects required variant types per family
- HSV color space processing preserves original brightness
- Supports compound variants like `each_active`, `break_active`

### Touch Sprite Composition

Compose diamond-layout Touch sprites from four rotated directions:

- Rotates source image at 0° / 90° / 180° / 270° into a diamond layout
- Adjustable gap and dot scale
- Real-time preview, exports merged PNG

### Touch Hold Composition

Compose Touch Hold combined sprites (4 corners + dot + background):

- **4 Corners mode** — import separate tr / br / bl / tl corner sprites
- **1 Source mode** — auto-generate four rotated corners from a single sprite (for break / mine, etc.)
- Background scaling, center dot scaling, gap adjustment
- Real-time preview and export

### PPU Calculator

Calculate in-game display size for sprites:

- Calculate PPU by width or height
- Reverse-calculate display size from PPU
- Built-in defaults (ring: 115, fan: 58)
- Auto-reads image pixel dimensions

### Color Picker

Lightweight HSV color picker:

- HSV sliders for precise color tuning
- 16 preset colors
- One-click HEX copy, live large color preview

### Bilingual UI

Interface supports English / Chinese with one-click language toggle.

## Installation

1. Clone or download this repository:

```bash
git clone <repo-url>
cd adxskin
```

2. Install dependencies (only Pillow is required):

```bash
pip install Pillow
```

## Usage

```bash
python AstroDX_Skin_Developer_Tool.py
```

A multi-tab Tkinter window will open, with each tab corresponding to a feature module.

## Project Structure

```
adxskin/
├── AstroDX_Skin_Developer_Tool.py   # Main tool (GUI)
├── DXskin/                           # Base skin example
├── DXskin_optimized/                 # Optimized skin example
├── SampleSkin/                       # Official sample skin
├── Sample Skin-Fumiko/               # Extended sample skin
├── dist/                             # Build artifacts
├── test_output/                      # Test output directory
├── README.md                         # This file
├── README_zh.md                      # Chinese README
└── skin.json                         # Skin config template
```

## Sample Skins

| Directory | Description |
|-----------|-------------|
| `DXskin/` | Base skin |
| `DXskin_optimized/` | Optimized skin |
| `SampleSkin/` | Official sample skin |
| `Sample Skin-Fumiko/` | Extended sample (Fumiko variant) |

## Requirements

- Python 3.10+
- Pillow

## License

GNU General Public License v3.0
