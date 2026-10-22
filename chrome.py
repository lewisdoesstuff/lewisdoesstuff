"""Wraps gifos frames in terminal-emulator window chrome with a transparent outside."""

import subprocess
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

TITLE_HEIGHT = 32
RADIUS = 10
SUPERSAMPLE = 4

# Catppuccin colors for the chrome, plus the GitHub page background the
# anti-aliased corner pixels are blended against (GIF has no partial alpha)
THEMES = {
    "dark": {
        "scheme": "catppuccin-mocha",
        "page": "#0d1117",
        "title_bg": "#181825",
        "title_fg": "#7f849c",
        "border": "#313244",
        "lights": ["#f38ba8", "#f9e2af", "#a6e3a1"],
    },
    "light": {
        "scheme": "catppuccin-latte",
        "page": "#ffffff",
        "title_bg": "#e6e9ef",
        "title_fg": "#8c8fa1",
        "border": "#ccd0da",
        "lights": ["#d20f39", "#df8e1d", "#40a02b"],
    },
}


def _window_mask(size):
    """Anti-aliased rounded-rectangle mask covering the whole window."""
    w, h = size
    big = Image.new("L", (w * SUPERSAMPLE, h * SUPERSAMPLE), 0)
    ImageDraw.Draw(big).rounded_rectangle(
        (0, 0, w * SUPERSAMPLE - 1, h * SUPERSAMPLE - 1),
        radius=RADIUS * SUPERSAMPLE,
        fill=255,
    )
    return big.resize(size, Image.LANCZOS)


def _chrome_overlay(size, theme, title, font_path):
    """Title bar, traffic lights and border, transparent over the terminal body."""
    w, h = size
    s = SUPERSAMPLE
    big = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(big)

    # Title bar with rounded top corners only
    draw.rounded_rectangle(
        (0, 0, w * s - 1, TITLE_HEIGHT * s),
        radius=RADIUS * s,
        fill=theme["title_bg"],
        corners=(True, True, False, False),
    )
    draw.line(
        (0, TITLE_HEIGHT * s, w * s, TITLE_HEIGHT * s),
        fill=theme["border"],
        width=s,
    )
    for i, color in enumerate(theme["lights"]):
        cx, cy, r = (20 + i * 20) * s, TITLE_HEIGHT // 2 * s, 6 * s
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)

    draw.rounded_rectangle(
        (0, 0, w * s - 1, h * s - 1),
        radius=RADIUS * s,
        outline=theme["border"],
        width=s,
    )
    overlay = big.resize(size, Image.LANCZOS)

    # Text is drawn at native size so it stays crisp
    font = ImageFont.truetype(str(font_path), 13)
    ImageDraw.Draw(overlay).text(
        (w // 2, TITLE_HEIGHT // 2), title, fill=theme["title_fg"], font=font, anchor="mm"
    )
    return overlay


def render_gif(frames_dir, out_path, mode, title, font_path, fps, transparent_body=False):
    """With `transparent_body`, frames must be drawn on the page color, which is
    then knocked out so the GitHub page shows through the terminal."""
    theme = THEMES[mode]
    frames = sorted(
        Path(frames_dir).glob("frame_*.png"), key=lambda p: int(p.stem.split("_")[1])
    )
    term_w, term_h = Image.open(frames[0]).size
    size = (term_w, term_h + TITLE_HEIGHT)

    mask = _window_mask(size)
    outside = mask.point(lambda v: 0 if v else 255)
    overlay = _chrome_overlay(size, theme, title, font_path)
    page = Image.new("RGB", size, theme["page"])
    page_rgb = page.getpixel((0, 0))

    def framed(frame_path):
        window = Image.new("RGBA", size)
        window.paste(Image.open(frame_path).convert("RGB"), (0, TITLE_HEIGHT))
        window.alpha_composite(overlay)
        return Image.composite(window.convert("RGB"), page, mask)

    def transparent(im):
        if not transparent_body:
            return outside
        # Exact page-colored pixels; the title bar and border never use it
        r, g, b = (
            band.point(lambda v, c=c: 255 if v == c else 0)
            for band, c in zip(im.split(), page_rgb)
        )
        body = ImageChops.multiply(ImageChops.multiply(r, g), b)
        return ImageChops.lighter(outside, body)

    # One shared palette built from a sample of frames, with the last index
    # reserved for transparency
    sample = [framed(f) for f in frames[::10]]
    montage = Image.new("RGB", (size[0], size[1] * len(sample)))
    for i, im in enumerate(sample):
        montage.paste(im, (0, i * size[1]))
    palette = montage.quantize(255, method=Image.Quantize.MEDIANCUT)
    palette.putpalette(palette.getpalette()[: 255 * 3] + [0, 0, 0])

    def quantized():
        for frame_path in frames:
            rgb = framed(frame_path)
            im = rgb.quantize(palette=palette, dither=Image.Dither.NONE)
            im.paste(255, mask=transparent(rgb))
            yield im

    # Every frame is written whole and cleared after display, which is correct
    # but huge; gifsicle then works out the minimal per-frame updates and
    # disposals, which Pillow can't do once pixels go back to transparent
    images = quantized()
    next(images).save(
        out_path,
        save_all=True,
        append_images=images,
        duration=1000 / fps,
        loop=0,
        transparency=255,
        disposal=2,
        optimize=False,
    )
    subprocess.run(["gifsicle", "--batch", "-O3", str(out_path)], check=True)
    print(f"INFO: Generated {out_path} ({len(frames)} frames)")
