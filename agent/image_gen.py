# agent/image_gen.py
#
# HOW IT WORKS:
# Pollinations.ai is a completely FREE image generation API.
# No account, no API key, no credit card needed.
# We simply build a URL with our image prompt encoded in it,
# make an HTTP GET request, and receive the image bytes back.
#
# After getting the image, we use Pillow (PIL) to:
#   1. Resize it to the exact platform dimensions
#   2. Draw a dark gradient overlay at the bottom (so white text is readable)
#   3. Render the headline, body copy, and CTA button on top
#
# KEY CONCEPT — Pillow image manipulation:
# Every pixel operation in Pillow works on a coordinate system
# where (0,0) is the TOP-LEFT corner.
# Images are composed in layers: base image → overlay → text.

import io
import requests
import urllib.parse
from PIL import Image, ImageDraw, ImageFont


def validate_ad_copy(ad_copy: dict) -> None:
    """Validate that ad_copy contains all required fields."""
    required = {"headline", "body", "cta", "image_prompt"}
    missing = required - set(ad_copy.keys())
    if missing:
        raise ValueError(f"ad_copy missing required fields: {missing}")


def validate_platform(platform: str) -> None:
    """Validate that platform is supported."""
    valid_platforms = {"Facebook Feed", "Instagram Square", "Instagram Story", "LinkedIn", "Twitter / X"}
    if platform not in valid_platforms:
        raise ValueError(f"Unsupported platform: {platform}. Must be one of {valid_platforms}")


def wrap_text(text: str, max_width: int, font, draw) -> list:
    """Wrap text to fit within max_width pixels. Returns list of text lines."""
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
    return lines


# Platform image dimensions (width x height in pixels)
PLATFORM_DIMENSIONS = {
    "Facebook Feed":    (1200, 628),
    "Instagram Square": (1080, 1080),
    "Instagram Story":  (1080, 1920),
    "LinkedIn":         (1200, 627),
    "Twitter / X":      (1600, 900),
}


def _get_font(size: int):
    """
    Try to load a system font. Fall back to Pillow's built-in default.
    The default font is tiny but always works on any OS.
    """
    font_paths = [
        # Linux (Hugging Face Spaces runs Linux)
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        # Windows
        "C:/Windows/Fonts/arialbd.ttf",
        # Mac
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()


def generate_flyer(ad_copy: dict, platform: str) -> Image.Image:
    """
    Generates a complete flyer image.
    
    ad_copy: dict from llm_core.generate_ad_copy (needs headline, body, cta, image_prompt)
    platform: string like "Instagram Square"
    Returns: PIL Image object (RGB)
    
    Steps:
    1. Fetch base image from Pollinations.ai
    2. Resize to platform dimensions
    3. Add dark gradient overlay
    4. Overlay text (headline, body, CTA button)
    """
    validate_ad_copy(ad_copy)
    validate_platform(platform)
    W, H = PLATFORM_DIMENSIONS[platform]

    # ── Step 1: Fetch image from Pollinations.ai ──────────────────────────
    # Encode the prompt for a URL (spaces → %20, etc.)
    # We append style keywords to get commercial-quality results
    full_prompt = ad_copy["image_prompt"] + ", commercial photography, vibrant, 4K, no text"
    encoded_prompt = urllib.parse.quote(full_prompt)
    
    # Pollinations URL format: https://image.pollinations.ai/prompt/{encoded_prompt}
    # width and height params control output size (it auto-adjusts)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={min(W,1024)}&height={min(H,1024)}&nologo=true"

    try:
        resp = requests.get(url, timeout=20)  # Pollinations typically responds in 10-15s
        resp.raise_for_status()
        base_img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
    except Exception as e:
        # If image fetch fails, create a solid colour background instead
        base_img = Image.new("RGBA", (W, H), (30, 30, 50, 255))

    # ── Step 2: Resize to exact platform dimensions ───────────────────────
    # LANCZOS = highest quality downscaling algorithm
    base_img = base_img.resize((W, H), Image.Resampling.LANCZOS)

    # ── Step 3: Dark gradient overlay (bottom 45% of image) ──────────────
    # We draw it onto a transparent layer then alpha-composite it
    # This ensures the white text will always be readable
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)
    bar_top = int(H * 0.55)  # gradient starts at 55% down
    for y in range(bar_top, H):
        # Alpha goes from 0 (transparent) to 200 (80% opaque) linearly
        alpha = int(200 * (y - bar_top) / (H - bar_top))
        draw_overlay.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    
    base_img = Image.alpha_composite(base_img, overlay)

    # ── Step 4: Draw text on top ──────────────────────────────────────────
    draw = ImageDraw.Draw(base_img)
    padding = int(W * 0.05)  # 5% of width as left/right padding

    # Font sizes scale with canvas width so they look right on any platform
    headline_font = _get_font(int(W * 0.052))
    body_font     = _get_font(int(W * 0.030))
    cta_font      = _get_font(int(W * 0.034))

    # Headline — white, positioned at 62% down, with text wrapping
    headline_y = int(H * 0.62)
    max_text_width = W - (padding * 2)
    headline_lines = wrap_text(ad_copy["headline"], max_text_width, headline_font, draw)
    for i, line in enumerate(headline_lines[:2]):
        draw.text((padding, headline_y + i * int(H * 0.05)), line,
                  font=headline_font, fill=(255, 255, 255, 245))

    # Body — light gray, positioned at 73% down, with text wrapping
    body_lines = wrap_text(ad_copy["body"], max_text_width, body_font, draw)
    body_y = int(H * 0.73)
    for i, line in enumerate(body_lines[:2]):
        draw.text((padding, body_y + i * int(H * 0.04)), line,
                  font=body_font, fill=(210, 210, 210, 220))

    # CTA Button — orange pill shape, positioned at 84% down
    cta_text = ad_copy["cta"]
    # Measure the text bounding box to size the pill correctly
    bbox = draw.textbbox((0, 0), cta_text, font=cta_font)
    text_w = bbox[2] - bbox[0]
    btn_pad_x = int(W * 0.04)
    btn_pad_y = int(H * 0.018)
    btn_x1 = padding
    btn_y1 = int(H * 0.84)
    btn_x2 = btn_x1 + text_w + btn_pad_x * 2
    btn_y2 = btn_y1 + (bbox[3] - bbox[1]) + btn_pad_y * 2

    draw.rounded_rectangle(
        [btn_x1, btn_y1, btn_x2, btn_y2],
        radius=(btn_y2 - btn_y1) // 2,
        fill=(255, 87, 34, 240)   # orange: RGB(255, 87, 34)
    )
    draw.text(
        (btn_x1 + btn_pad_x, btn_y1 + btn_pad_y),
        cta_text, font=cta_font, fill=(255, 255, 255, 255)
    )

    return base_img.convert("RGB")