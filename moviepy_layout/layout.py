import os
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from typing import Literal, Optional, Tuple, Union, List
from moviepy.editor import TextClip, CompositeVideoClip, ImageClip, ColorClip, VideoClip
from moviepy.video.fx.resize import resize

RGBAColor = Tuple[int, int, int, int]
Box = Tuple[int, int, int, int]
BorderSpec = Tuple[int, RGBAColor]
GradientStop = Tuple[RGBAColor, float]


# ^ Gradient class to create gradient backgrounds
class Gradient:
    def __init__(
        self,
        direction: Literal[
            "top_to_bottom",
            "bottom_to_top",
            "left_to_right",
            "right_to_left",
            "top_left_to_bottom_right",
            "bottom_right_to_top_left",
            "top_right_to_bottom_left",
            "bottom_left_to_top_right",
        ],
        stops: List[GradientStop],
    ):
        self.direction = direction
        self.stops = sorted(stops, key=lambda x: x[1])

    def render(self, size: Tuple[int, int]) -> np.ndarray:
        w, h = size
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))  # type: ignore
        draw = ImageDraw.Draw(img, "RGBA")

        axis_len = {
            "top_to_bottom": h,
            "bottom_to_top": h,
            "left_to_right": w,
            "right_to_left": w,
        }.get(self.direction, max(w, h))

        for i in range(axis_len):
            t = i / (axis_len - 1)
            color = self.interpolate(t)
            if self.direction == "top_to_bottom":
                draw.line([(0, i), (w, i)], fill=color)
            elif self.direction == "bottom_to_top":
                draw.line([(0, h - i - 1), (w, h - i - 1)], fill=color)
            elif self.direction == "left_to_right":
                draw.line([(i, 0), (i, h)], fill=color)
            elif self.direction == "right_to_left":
                draw.line([(w - i - 1, 0), (w - i - 1, h)], fill=color)
            elif self.direction == "top_left_to_bottom_right":
                draw.line([(0, i), (i, 0)], fill=color)
            elif self.direction == "bottom_right_to_top_left":
                draw.line([(w - i, h), (w, h - i)], fill=color)
            elif self.direction == "top_right_to_bottom_left":
                draw.line([(w - i, 0), (0, i)], fill=color)
            elif self.direction == "bottom_left_to_top_right":
                draw.line([(0, h - i), (i, h)], fill=color)

        return np.array(img)

    def interpolate(self, t: float) -> RGBAColor:
        for i in range(len(self.stops) - 1):
            c1, p1 = self.stops[i]
            c2, p2 = self.stops[i + 1]
            if p1 <= t <= p2:
                ratio = (t - p1) / (p2 - p1)
                return tuple(int(c1[j] + (c2[j] - c1[j]) * ratio) for j in range(4))  # type: ignore
        return self.stops[-1][0]


class Layout:
    # ^ Utility methods for color conversion
    @staticmethod
    def rgba_to_hex(rgba: Tuple[int, int, int, int]) -> str:
        r, g, b, a = rgba
        return "#%02x%02x%02x%02x" % (r, g, b, a)

    # ^ Convert hex color to RGBA tuple
    @staticmethod
    def hex_to_rgba(hex_color: str) -> Tuple[int, int, int, int]:
        hex_color = hex_color.lstrip("#")
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            a = 255
        elif len(hex_color) == 8:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            a = int(hex_color[6:8], 16)
        else:
            raise ValueError("Invalid hex color format")
        return (r, g, b, a)

    # ^ Method to create an asset with specified resizing mode
    @staticmethod
    def asset(
        clip: Union[VideoClip, ImageClip],
        width: float,
        height: float,
        mode: Literal["cover", "contain", "fit", "fill"] = "contain",
    ) -> VideoClip:

        if mode == "fill":
            resized = resize(clip, width=width, height=height)
        else:
            aspect_ratio = clip.w / clip.h
            target_ratio = width / height

            if mode in ["contain", "fit"]:
                resized = (
                    resize(clip, height=height)
                    if aspect_ratio > target_ratio
                    else resize(clip, width=width)
                )
            elif mode == "cover":
                resized = (
                    resize(clip, width=width)
                    if aspect_ratio > target_ratio
                    else resize(clip, height=height)
                )
            else:
                raise ValueError(f"Invalid mode: {mode}")

        asset = resized.set_position("center").on_color(
            size=(int(width), int(height)), color=(0, 0, 0), col_opacity=0
        )

        return asset.set_duration(clip.duration)

    # ^ Method to create a box layout with optional child clip
    @staticmethod
    def box(
        width: Union[float, Literal["full"]],
        height: Union[float, Literal["full"]],
        child: Optional[CompositeVideoClip] = None,
        padding: Tuple[int, int, int, int] = (0, 0, 0, 0),
        margin: Tuple[int, int, int, int] = (0, 0, 0, 0),
        bg_color: Optional[Tuple[int, int, int]] = None,
        duration: float = 5.0,
        screen_size: Tuple[int, int] = (1080, 1920),
    ) -> CompositeVideoClip:

        resolved_width = screen_size[0] if width == "full" else width
        resolved_height = screen_size[1] if height == "full" else height

        pad_top, pad_right, pad_bottom, pad_left = padding  # type: ignore
        mar_top, mar_right, mar_bottom, mar_left = margin  # type: ignore

        content_x = pad_left + mar_left
        content_y = pad_top + mar_top

        if bg_color is None:
            base_array = np.zeros(
                (int(resolved_height), int(resolved_width), 4), dtype=np.uint8
            )
        else:
            r, g, b = bg_color
            base_array = np.zeros(
                (int(resolved_height), int(resolved_width), 4), dtype=np.uint8
            )
            base_array[..., :3] = (r, g, b)
            base_array[..., 3] = 255

        base = ImageClip(base_array, ismask=False).set_duration(duration)

        if child:
            child = child.set_position((content_x, content_y))
            return CompositeVideoClip(
                [base, child], size=(resolved_width, resolved_height)
            )
        else:
            return base

    # ^ Method to create a container with various styling options
    @staticmethod
    def container(
        child: Optional[VideoClip] = None,
        padding: Union[int, Box] = 20,
        margin: Union[int, Box] = 0,
        vertical_alignment: Literal["top", "center", "bottom"] = "center",
        horizontal_alignment: Literal["left", "center", "right"] = "center",
        gradient: Optional[Gradient] = None,
        bg_color: Optional[RGBAColor] = None,
        radius: Union[int, Box] = 0,
        border: Optional[BorderSpec] = None,
        size: Optional[Tuple[int, int]] = None,
        duration: float = 5.0,
    ) -> CompositeVideoClip:

        def normalize_box(value: Union[int, Box]) -> Box:
            return (value, value, value, value) if isinstance(value, int) else value

        pad_top, pad_right, pad_bottom, pad_left = normalize_box(padding)
        mar_top, mar_right, mar_bottom, mar_left = normalize_box(margin)
        radius_top_left, radius_top_right, radius_bottom_right, radius_bottom_left = (
            normalize_box(radius)
        )

        child_w, child_h = (child.w, child.h) if child else (0, 0)
        padded_w = child_w + pad_left + pad_right
        padded_h = child_h + pad_top + pad_bottom
        container_w = padded_w + mar_left + mar_right
        container_h = padded_h + mar_top + mar_bottom

        if size:
            container_w, container_h = size

        if gradient:
            bg_array = gradient.render((container_w, container_h))
        elif bg_color:
            bg_array = np.zeros((container_h, container_w, 4), dtype=np.uint8)
            r, g, b, a = bg_color
            bg_array[..., :3] = (r, g, b)
            bg_array[..., 3] = a
        else:
            bg_array = np.zeros((container_h, container_w, 4), dtype=np.uint8)

        def create_mask(size: Tuple[int, int], radii: Box) -> np.ndarray:
            w, h = size
            tl, tr, br, bl = radii

            mask = Image.new("L", (w, h), 0)
            draw = ImageDraw.Draw(mask)

            if any(r > 0 for r in radii):
                draw.rectangle([(tl, 0), (w - tr, h)], fill=255)
                draw.rectangle([(0, tl), (w, h - bl)], fill=255)

                if tl > 0:
                    draw.pieslice([(0, 0), (tl * 2, tl * 2)], 180, 270, fill=255)
                if tr > 0:
                    draw.pieslice([(w - tr * 2, 0), (w, tr * 2)], 270, 360, fill=255)
                if br > 0:
                    draw.pieslice([(w - br * 2, h - br * 2), (w, h)], 0, 90, fill=255)
                if bl > 0:
                    draw.pieslice([(0, h - bl * 2), (bl * 2, h)], 90, 180, fill=255)
            else:
                draw.rectangle([(0, 0), (w, h)], fill=255)

            return np.array(mask)

        def create_border(
            size: Tuple[int, int], radii: Box, border: BorderSpec
        ) -> np.ndarray:
            w, h = size
            tl, tr, br, bl = radii
            border_width, border_color = border

            border_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))  # type: ignore
            border_draw = ImageDraw.Draw(border_img)

            if any(r > 0 for r in radii):
                border_draw.rectangle(
                    [(tl, 0), (w - tr, border_width)], fill=border_color
                )
                border_draw.rectangle(
                    [(w - border_width, tr), (w, h - br)], fill=border_color
                )
                border_draw.rectangle(
                    [(bl, h - border_width), (w - br, h)], fill=border_color
                )
                border_draw.rectangle(
                    [(0, tl), (border_width, h - bl)], fill=border_color
                )

                if tl > 0:
                    border_draw.arc(
                        [(0, 0), (tl * 2, tl * 2)],
                        180,
                        270,
                        fill=border_color,
                        width=border_width,
                    )
                if tr > 0:
                    border_draw.arc(
                        [(w - tr * 2, 0), (w, tr * 2)],
                        270,
                        360,
                        fill=border_color,
                        width=border_width,
                    )
                if br > 0:
                    border_draw.arc(
                        [(w - br * 2, h - br * 2), (w, h)],
                        0,
                        90,
                        fill=border_color,
                        width=border_width,
                    )
                if bl > 0:
                    border_draw.arc(
                        [(0, h - bl * 2), (bl * 2, h)],
                        90,
                        180,
                        fill=border_color,
                        width=border_width,
                    )
            else:
                border_draw.rectangle(
                    [(0, 0), (w, h)], outline=border_color, width=border_width
                )

            return np.array(border_img)

        if any(
            r > 0
            for r in [
                radius_top_left,
                radius_top_right,
                radius_bottom_right,
                radius_bottom_left,
            ]
        ):
            mask_array = create_mask(
                (container_w, container_h),
                (
                    radius_top_left,
                    radius_top_right,
                    radius_bottom_right,
                    radius_bottom_left,
                ),
            )
            bg_array[..., 3] = bg_array[..., 3] * (mask_array > 0)

        bg = ImageClip(bg_array, ismask=False).set_duration(duration)

        layers: List[VideoClip] = [bg]

        if border:
            border_array = create_border(
                (container_w, container_h),
                (
                    radius_top_left,
                    radius_top_right,
                    radius_bottom_right,
                    radius_bottom_left,
                ),
                border,
            )
            border_clip = ImageClip(border_array, ismask=False).set_duration(duration)
            layers.append(border_clip)

        if child:
            x = mar_left + pad_left
            y = mar_top + pad_top

            if horizontal_alignment == "center":
                x = (container_w - child_w) // 2
            elif horizontal_alignment == "right":
                x = container_w - child_w - mar_right - pad_right

            if vertical_alignment == "center":
                y = (container_h - child_h) // 2
            elif vertical_alignment == "bottom":
                y = container_h - child_h - mar_bottom - pad_bottom

            child = child.set_position((x, y))
            layers.append(child)  # type: ignore

        return CompositeVideoClip(layers, size=(container_w, container_h))

    # ^ Method to create a flex layout for arranging multiple clips
    @staticmethod
    def flex(
        children: List[CompositeVideoClip],
        direction: Literal["row", "column"],
        vertical_alignment: Literal["top", "center", "bottom"] = "center",
        horizontal_alignment: Literal["left", "center", "right"] = "center",
        gap: float = 0,
        width: Union[float, Literal["full", "fit"]] = "fit",
        height: Union[float, Literal["full", "fit"]] = "fit",
        screen_size: Optional[Tuple[int, int]] = None,
        duration: float = 5.0,
    ) -> CompositeVideoClip:

        total_main = 0
        max_cross = 0

        for clip in children:
            w, h = clip.size
            if direction == "row":
                total_main += w + gap
                max_cross = max(max_cross, h)
            else:
                total_main += h + gap
                max_cross = max(max_cross, w)

        total_main -= gap

        if screen_size:
            screen_width, screen_height = screen_size
        else:
            screen_width, screen_height = 1920, 1080

        if width == "full":
            resolved_width = screen_width
        elif width == "fit":
            resolved_width = total_main if direction == "row" else max_cross
        else:
            resolved_width = width

        if height == "full":
            resolved_height = screen_height
        elif height == "fit":
            resolved_height = max_cross if direction == "row" else total_main
        else:
            resolved_height = height

        positions = []

        if direction == "row":
            if horizontal_alignment == "left":
                x_start = 0
            elif horizontal_alignment == "center":
                x_start = (resolved_width - total_main) // 2
            else:
                x_start = resolved_width - total_main

            y_base = {
                "top": 0,
                "center": (resolved_height - max_cross) // 2,
                "bottom": resolved_height - max_cross,
            }[vertical_alignment]

            x = x_start
            for clip in children:
                positions.append(clip.set_position((x, y_base)))
                x += clip.w + gap

        else:
            if vertical_alignment == "top":
                y_start = 0
            elif vertical_alignment == "center":
                y_start = (resolved_height - total_main) // 2
            else:
                y_start = resolved_height - total_main

            x_base = {
                "left": 0,
                "center": (resolved_width - max_cross) // 2,
                "right": resolved_width - max_cross,
            }[horizontal_alignment]

            y = y_start
            for clip in children:
                positions.append(clip.set_position((x_base, y)))
                y += clip.h + gap

        return CompositeVideoClip(
            positions, size=(resolved_width, resolved_height)
        ).set_duration(duration)

    # ^ Method to stack clips vertically based on their order
    @staticmethod
    def stack(
        children: List[Tuple[VideoClip, int]],
        size: Tuple[int, int],
        duration: float = 5.0,
    ) -> VideoClip:
        sorted_clips = [
            clip.set_duration(duration)
            for clip, _ in sorted(children, key=lambda x: x[1])
        ]
        return CompositeVideoClip(sorted_clips, size=size).set_duration(duration)

    # ^ Method to create a text clip with various styling options
    @staticmethod
    def text(
        text: str,
        font_size: float,
        font: Union[str, os.PathLike] = "Arial",
        width: Optional[float] = None,
        gradient_hex: Optional[str] = None,
        font_color: Tuple[int, int, int, int] = (255, 255, 255, 255),
        text_align: Literal["left", "center", "right"] = "left",
        text_wrap: bool = True,
        shadow: Optional[dict] = None,
        duration: float = 5.0,
    ) -> CompositeVideoClip:
        gravity_map = {"left": "West", "center": "Center", "right": "East"}

        color_hex = Layout.rgba_to_hex(font_color)

        font_param = font
        if isinstance(font, os.PathLike) or (
            isinstance(font, str) and os.path.isfile(font)
        ):
            font_param = str(font)

        if text_wrap:
            if width is None:
                method = "label"
                size = None
            else:
                method = "caption"
                size = (width, None)
        else:
            method = "label"
            size = None

        txt_clip = TextClip(
            text,
            fontsize=font_size,
            font=font_param,  # type: ignore
            color=color_hex,
            align=gravity_map[text_align],
            method=method,
            size=size,
        ).set_duration(duration)

        shadow_params = {
            "offset": (2, 2),
            "blur_radius": 3,
            "color": (0, 0, 0, 128),
            "opacity": 0.7,
        }
        if shadow:
            shadow_params.update(shadow)

        layers = []

        if shadow:
            shadow_color = shadow_params["color"][:3]

            def create_blurred_shadow_mask(get_frame, t):
                mask_frame = txt_clip.mask.get_frame(t)

                try:
                    from scipy.ndimage import gaussian_filter

                    blurred_mask = gaussian_filter(
                        mask_frame, sigma=shadow_params["blur_radius"]
                    )
                except ImportError:
                    try:
                        mask_uint8 = (mask_frame * 255).astype(np.uint8)
                        pil_mask = Image.fromarray(mask_uint8, mode="L")

                        blurred_pil = pil_mask.filter(
                            ImageFilter.GaussianBlur(shadow_params["blur_radius"])
                        )

                        blurred_mask = np.array(blurred_pil).astype(np.float64) / 255.0
                    except Exception as e:
                        print(f"Warning: Could not blur shadow mask: {e}")
                        blurred_mask = mask_frame

                return blurred_mask

            blurred_shadow_mask = txt_clip.mask.fl(create_blurred_shadow_mask)

            shadow_color_clip = ColorClip(
                size=txt_clip.size, color=shadow_color, duration=duration
            )

            shadow_clip = shadow_color_clip.set_mask(blurred_shadow_mask)

            shadow_clip = shadow_clip.set_position(shadow_params["offset"])
            shadow_clip = shadow_clip.set_opacity(shadow_params["opacity"])
            layers.append(shadow_clip)

        layers.append(txt_clip)

        if gradient_hex:
            try:
                r, g, b, a = Layout.hex_to_rgba(gradient_hex)
                alpha = np.linspace(0, a, txt_clip.h).astype(np.uint8)
                alpha = np.tile(alpha[:, None], (1, txt_clip.w))

                rgba = np.stack(
                    [
                        np.full_like(alpha, r),
                        np.full_like(alpha, g),
                        np.full_like(alpha, b),
                        alpha,
                    ],
                    axis=2,
                )

                grad_clip = ImageClip(rgba, ismask=False).set_duration(duration)
                grad_clip = grad_clip.set_mask(txt_clip.mask)
                layers.append(grad_clip)
            except Exception as e:
                print(f"Error creating gradient: {e}")

        final_width = txt_clip.w
        final_height = txt_clip.h

        if shadow:
            offset_x, offset_y = shadow_params["offset"]
            blur_radius = shadow_params["blur_radius"]

            final_width = max(final_width, offset_x + txt_clip.w + blur_radius * 2)
            final_height = max(final_height, offset_y + txt_clip.h + blur_radius * 2)

        return CompositeVideoClip(layers, size=(final_width, final_height))

    # ^ Method to apply visual effects to a clip
    @staticmethod
    def effect(
        child: CompositeVideoClip,
        effect: Literal["shadow", "blur", "inner_shadow"],
        effect_params: Optional[dict] = None,
    ) -> CompositeVideoClip:

        if effect_params is None:
            effect_params = {}

        if effect == "shadow":
            return Layout._apply_shadow_effect(child, **effect_params)
        elif effect == "blur":
            return Layout._apply_blur_effect(child, **effect_params)
        elif effect == "inner_shadow":
            return Layout._apply_inner_shadow_effect(child, **effect_params)

    @staticmethod
    def _apply_shadow_effect(
        child: CompositeVideoClip,
        offset: Tuple[int, int] = (2, 2),
        blur_radius: int = 3,
        color: Tuple[int, int, int, int] = (0, 0, 0, 128),
        opacity: float = 0.5,
    ) -> CompositeVideoClip:
        """Apply drop shadow effect to a clip"""

        shadow_padding = blur_radius * 2
        offset_x, offset_y = offset

        left_padding = max(shadow_padding + abs(min(offset_x, 0)), 0)
        top_padding = max(shadow_padding + abs(min(offset_y, 0)), 0)
        right_padding = max(shadow_padding + max(offset_x, 0), 0)
        bottom_padding = max(shadow_padding + max(offset_y, 0), 0)

        new_width = child.w + left_padding + right_padding
        new_height = child.h + top_padding + bottom_padding

        def create_shadow_frame(t):
            if hasattr(child, "get_frame"):
                frame = child.get_frame(t)
                if len(frame.shape) == 3 and frame.shape[2] == 4:
                    alpha = frame[:, :, 3]
                else:
                    if len(frame.shape) == 3:
                        alpha = np.where(np.sum(frame, axis=2) > 0, 255, 0).astype(
                            np.uint8
                        )
                    else:
                        alpha = np.where(frame > 0, 255, 0).astype(np.uint8)
            else:
                alpha = np.ones((child.h, child.w), dtype=np.uint8) * 255

            shadow_canvas = np.zeros((new_height, new_width), dtype=np.uint8)

            child_x_in_canvas = left_padding
            child_y_in_canvas = top_padding
            shadow_canvas[
                child_y_in_canvas : child_y_in_canvas + child.h,
                child_x_in_canvas : child_x_in_canvas + child.w,
            ] = alpha

            try:
                from scipy.ndimage import gaussian_filter

                blurred_shadow = gaussian_filter(
                    shadow_canvas.astype(float), sigma=blur_radius
                )
            except ImportError:
                shadow_img = Image.fromarray(shadow_canvas, mode="L")
                shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(blur_radius))
                blurred_shadow = np.array(shadow_img).astype(float)

            shadow_rgb = np.zeros((new_height, new_width, 3), dtype=np.uint8)
            shadow_rgb[..., :3] = color[:3]

            alpha_channel = (blurred_shadow * (color[3] / 255) * opacity).astype(
                np.uint8
            )

            return shadow_rgb, alpha_channel

        def shadow_frame_func(t):
            rgb, alpha = create_shadow_frame(t)  # type: ignore
            return rgb

        def shadow_mask_func(t):
            rgb, alpha = create_shadow_frame(t)  # type: ignore
            return alpha / 255.0

        shadow_clip = VideoClip(shadow_frame_func, duration=child.duration).set_fps(24)
        shadow_mask = VideoClip(
            shadow_mask_func, duration=child.duration, ismask=True
        ).set_fps(24)
        shadow_clip = shadow_clip.set_mask(shadow_mask)

        shadow_clip = shadow_clip.set_position((offset_x, offset_y))

        child_positioned = child.set_position((left_padding, top_padding))

        return CompositeVideoClip(
            [shadow_clip, child_positioned], size=(new_width, new_height)
        )

    @staticmethod
    def _apply_blur_effect(
        child: CompositeVideoClip, blur_radius: int = 5
    ) -> CompositeVideoClip:

        def blur_frame(t):
            if hasattr(child, "get_frame"):
                frame = child.get_frame(t)
            else:
                frame = np.zeros((child.h, child.w, 3), dtype=np.uint8)

            if len(frame.shape) == 3 and frame.shape[2] == 4:
                rgb_frame = frame[:, :, :3]
                alpha_frame = frame[:, :, 3]

                img = Image.fromarray(rgb_frame, "RGB")
                blurred_img = img.filter(ImageFilter.GaussianBlur(blur_radius))
                blurred_rgb = np.array(blurred_img)

                alpha_img = Image.fromarray(alpha_frame, "L")
                blurred_alpha_img = alpha_img.filter(
                    ImageFilter.GaussianBlur(blur_radius)
                )
                blurred_alpha = np.array(blurred_alpha_img)

                result = np.zeros((frame.shape[0], frame.shape[1], 4), dtype=np.uint8)
                result[:, :, :3] = blurred_rgb
                result[:, :, 3] = blurred_alpha
                return result

            elif len(frame.shape) == 3 and frame.shape[2] == 3:
                img = Image.fromarray(frame, "RGB")
            else:
                img = Image.fromarray(frame, "L")

            blurred_img = img.filter(ImageFilter.GaussianBlur(blur_radius))
            return np.array(blurred_img)

        blurred_clip = VideoClip(blur_frame, duration=child.duration).set_fps(24)
        return blurred_clip

    @staticmethod
    def _apply_inner_shadow_effect(
        child: CompositeVideoClip,
        offset: Tuple[int, int] = (2, 2),
        blur_radius: int = 3,
        color: Tuple[int, int, int, int] = (0, 0, 0, 128),
    ) -> CompositeVideoClip:
        """Apply inner shadow effect to a clip"""

        def create_inner_shadow_frame(t):
            if hasattr(child, "get_frame"):
                frame = child.get_frame(t)
                if len(frame.shape) == 3 and frame.shape[2] == 4:
                    alpha = frame[:, :, 3]
                else:
                    if len(frame.shape) == 3:
                        alpha = np.where(np.sum(frame, axis=2) > 0, 255, 0).astype(
                            np.uint8
                        )
                    else:
                        alpha = np.where(frame > 0, 255, 0).astype(np.uint8)
            else:
                alpha = np.ones((child.h, child.w), dtype=np.uint8) * 255

            shadow_mask = np.zeros_like(alpha)
            offset_x, offset_y = offset

            y_start = max(offset_y, 0)
            y_end = min(child.h, child.h + offset_y)
            x_start = max(offset_x, 0)
            x_end = min(child.w, child.w + offset_x)

            if y_end > y_start and x_end > x_start:
                source_y_end = y_end - offset_y if offset_y > 0 else child.h
                source_x_end = x_end - offset_x if offset_x > 0 else child.w
                source_y_start = 0 if offset_y > 0 else -offset_y
                source_x_start = 0 if offset_x > 0 else -offset_x

                shadow_mask[y_start:y_end, x_start:x_end] = alpha[
                    source_y_start:source_y_end, source_x_start:source_x_end
                ]

            shadow_mask = np.maximum(
                0, alpha.astype(int) - shadow_mask.astype(int)
            ).astype(np.uint8)

            try:
                from scipy.ndimage import gaussian_filter

                blurred_shadow = gaussian_filter(
                    shadow_mask.astype(float), sigma=blur_radius
                )
            except ImportError:
                shadow_img = Image.fromarray(shadow_mask, mode="L")
                shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(blur_radius))
                blurred_shadow = np.array(shadow_img).astype(float)

            shadow_rgb = np.zeros((child.h, child.w, 3), dtype=np.uint8)
            shadow_rgb[..., :3] = color[:3]

            final_alpha = (blurred_shadow * (color[3] / 255)).astype(np.uint8)
            final_alpha = np.minimum(final_alpha, alpha)

            return shadow_rgb, final_alpha

        def inner_shadow_frame_func(t):
            rgb, alpha = create_inner_shadow_frame(t)  # type: ignore
            return rgb

        def inner_shadow_mask_func(t):
            rgb, alpha = create_inner_shadow_frame(t)  # type: ignore
            return alpha / 255.0

        inner_shadow_clip = VideoClip(
            inner_shadow_frame_func, duration=child.duration
        ).set_fps(24)
        inner_shadow_mask = VideoClip(
            inner_shadow_mask_func, duration=child.duration, ismask=True
        ).set_fps(24)
        inner_shadow_clip = inner_shadow_clip.set_mask(inner_shadow_mask)

        return CompositeVideoClip([inner_shadow_clip, child], size=(child.w, child.h))
