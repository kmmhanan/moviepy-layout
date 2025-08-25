# moviepy-layout

Composable layout primitives for [MoviePy](https://zulko.github.io/moviepy/), inspired by **Flutter** and **CSS**.

## ✨ Features

- 🎨 **Gradient backgrounds** with directional control
- 🖼️ **Asset resizing** (`cover`, `contain`, `fit`, `fill`)
- 📦 **Box & Container layouts** with padding, margin, background color/gradient
- 📐 **Flex layouts** (`row`, `column`) with alignment & gaps
- 📚 **Stack layouts** for overlaying clips by z-index
- 🔤 **Text utilities** with alignment, wrapping, gradients, shadows
- 🎭 **Effects** like shadow, blur, inner shadow
- 🎨 **Color conversion** utilities (`hex ↔ rgba`)

---

## 📦 Installation

```bash
pip install moviepy-layout
```

---

## 🚀 Usage Example

```python
from moviepy.editor import ImageClip
from moviepy-layout import Layout, Gradient

# Create a gradient background
gradient = Gradient(
    direction="top_to_bottom",
    stops=[
        ((255, 0, 0, 255), 0.0),
        ((0, 0, 255, 255), 1.0),
    ]
)

bg = ImageClip(gradient.render((1280, 720)), ismask=False)

# Resize with cover mode
clip = Layout.asset(bg, width=720, height=1280, mode="cover")
clip.preview()
```

---

## 🛠️ API Reference

### 🎨 Gradient

```python
Gradient(
    direction="top_to_bottom",  # gradient direction
    stops=[((r,g,b,a), position), ...]  # color stops
).render((width, height))
```

Supported directions:
- `top_to_bottom`
- `bottom_to_top`
- `left_to_right`
- `right_to_left`
- `top_left_to_bottom_right`
- `bottom_right_to_top_left`
- `top_right_to_bottom_left`
- `bottom_left_to_top_right`

---

### 🎬 Layout Utilities

#### `Layout.asset(...)`
Resize a clip with a given mode.

- `cover`: fills container, crops excess
- `contain`: fits inside container, maintains aspect ratio
- `fit`: resizes to match one dimension
- `fill`: stretches to fill container

#### `Layout.box(...)`
Create a box with optional child.

```python
Layout.box(
    width=500,
    height=500,
    child=my_clip,
    padding=(10, 20, 10, 20),
    margin=(5, 5, 5, 5),
    bg_color=(255, 255, 255),
    duration=5.0,
    screen_size=(1080, 1920)
)
```

#### `Layout.container(...)`
A more advanced box with alignment, gradient, radius, and border options.

```python
Layout.container(
    child=my_clip,
    padding=20,  # or (top, right, bottom, left)
    margin=10,
    vertical_alignment="center",  # "top" | "center" | "bottom"
    horizontal_alignment="center",  # "left" | "center" | "right"
    gradient=my_gradient,  # optional Gradient instance
    bg_color=(255, 255, 255, 255),
    radius=10,  # rounded corners
    border={"color": (0, 0, 0, 255), "width": 2},
    size=(500, 500),
    duration=5.0
)
```

#### `Layout.flex(...)`
Arrange multiple clips in a row or column.

```python
Layout.flex(
    children=[clip1, clip2, clip3],
    direction="row",  # "row" | "column"
    vertical_alignment="center",  # for "column" direction
    horizontal_alignment="center",  # for "row" direction
    gap=20,  # space between children
    width="fit",   # "full" | "fit"
    height="fit",  # "full" | "fit"
    screen_size=(1080, 1920),
    duration=5.0
)
```

#### `Layout.stack(...)`
Overlay clips with z-order.

```python
Layout.stack(
    children=[(background_clip, 0), (overlay_clip, 1), (text_clip, 2)],
    size=(1080, 1920),
    duration=5.0
)
```

#### `Layout.text(...)`
Create styled text clips with gradient, shadows, alignment, wrapping.

```python
Layout.text(
    text="Hello World",
    font_size=64,
    font="Arial",
    width=500,  # optional, for wrapping
    gradient_hex="#ff0000ff,#0000ffff",  # optional gradient fill
    font_color=(255, 255, 255, 255),
    text_align="center",  # "left" | "center" | "right"
    text_wrap=True,
    shadow={
        "color": (0, 0, 0, 128),
        "offset": (4, 4),
        "blur": 5
    },
    duration=5.0
)
```

#### `Layout.effect(...)`
Apply visual effects (`shadow`, `blur`, `inner_shadow`) to clips.

- Shadow

```python
Layout.effect(my_clip, effect="shadow", effect_params={"color": (0, 0, 0, 128), "offset": (10, 10)})
```

- Blur

```python
Layout.effect(my_clip, effect="blur", effect_params={"radius": 5})
```

- Inner Shadow

```python
Layout.effect(my_clip, effect="inner_shadow", effect_params={"color": (0, 0, 0, 128), "offset": (5, 5), "blur": 10})
```

---

### 🎨 Color Utilities

```python
Layout.rgba_to_hex((255, 0, 0, 255))  # "#ff0000ff"
Layout.hex_to_rgba("#ff0000ff")       # (255, 0, 0, 255)
```

---

## 📖 Example Project Ideas

- Instagram story generators
- Slideshow editors
- Dynamic caption overlays
- UI-style compositions with MoviePy

---

## 📜 License

MIT License © 2025 Kmm Hanan
