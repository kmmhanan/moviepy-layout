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

#### `Layout.flex(...)`
Arrange multiple clips in a row or column.

#### `Layout.stack(...)`
Overlay clips with z-order.

#### `Layout.text(...)`
Create styled text clips with gradient, shadows, alignment, wrapping.

#### `Layout.effect(...)`
Apply visual effects (`shadow`, `blur`, `inner_shadow`) to clips.

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

MIT License © 2025
