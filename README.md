# moviepy_layout

Composable layout primitives for MoviePy, inspired by Flutter and CSS.

## Features

- `Layout.asset(...)`: Resize clips with modes like `cover`, `contain`, `fill`
- `Gradient`: Create RGBA gradient backgrounds with directional control
- `Layout.hex_to_rgba(...)` and `rgba_to_hex(...)`: Color conversion utilities

## Example

```python
from moviepy_layout import Layout, Gradient

gradient = Gradient(
    direction="top_to_bottom",
    stops=[
        ((255, 0, 0, 255), 0.0),
        ((0, 0, 255, 255), 1.0),
    ]
)

bg = ImageClip(gradient.render((1280, 720)), ismask=False)
clip = Layout.asset(bg, width=720, height=1280, mode="cover")
clip.preview()