from PIL import Image, ImageDraw, ImageFont
import os

WIDTH, HEIGHT = 1280, 720
FPS = 24
HOLD_FRAMES = int(0.4 * FPS)  # 9 frames between cards

# ── theme definitions ──────────────────────────────────────────────────────────
THEMES = {
    "Clean": {
        "bg": (245, 240, 232),
        "lines": (232, 224, 208),
        "ink": (44, 44, 44),
        "accent": (232, 89, 60),
        "accent2": (59, 130, 246),
        "margin": (255, 204, 204),
    },
    "Colorful": {
        "bg": (255, 254, 247),
        "lines": (187, 228, 187),
        "ink": (26, 26, 46),
        "accent": (249, 115, 22),
        "accent2": (22, 163, 74),
        "margin": (187, 228, 187),
    },
    "Dark": {
        "bg": (26, 26, 46),
        "lines": (40, 30, 60),
        "ink": (232, 232, 240),
        "accent": (96, 165, 250),
        "accent2": (52, 211, 153),
        "margin": (50, 40, 70),
    },
}


def blend(c1: tuple, c2: tuple, t: float) -> tuple:
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def alpha_col(color: tuple, alpha: float, bg: tuple) -> tuple:
    return blend(bg, color, alpha)


# ── font loading ───────────────────────────────────────────────────────────────
def _load_font(bold: bool, size: int) -> ImageFont.FreeTypeFont:
    paths_bold = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    paths_regular = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    candidates = paths_bold if bold else paths_regular
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def _get_fonts():
    return {
        "title": _load_font(True, 60),
        "body": _load_font(False, 34),
        "small": _load_font(False, 22),
        "number": _load_font(True, 90),
        "emoji": _load_font(False, 70),
    }


# ── helpers ────────────────────────────────────────────────────────────────────
def _draw_text_safe(draw, pos, text, font, fill):
    try:
        draw.text(pos, text, font=font, fill=fill)
    except Exception:
        pass


def _draw_emoji_safe(draw, pos, emoji, font, fill):
    try:
        draw.text(pos, emoji, font=font, fill=fill, embedded_color=True)
    except Exception:
        try:
            draw.text(pos, emoji, font=font, fill=fill)
        except Exception:
            pass


def _text_width(draw, text, font):
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0]
    except Exception:
        return len(text) * 10


def _draw_ruled_lines(draw, theme, y_start=0):
    for y in range(y_start, HEIGHT, 36):
        draw.line([(0, y), (WIDTH, y)], fill=theme["lines"], width=1)


def _draw_margin_line(draw, theme):
    draw.line([(80, 0), (80, HEIGHT)], fill=theme["margin"], width=2)


def _draw_progress_bar(draw, p: float, theme, y=HEIGHT - 6):
    draw.rectangle([(0, y), (WIDTH, HEIGHT)], fill=blend(theme["bg"], theme["lines"], 0.5))
    draw.rectangle([(0, y), (int(WIDTH * p), HEIGHT)], fill=theme["accent"])


# ── Whiteboard style renderer ──────────────────────────────────────────────────
def _render_whiteboard_frame(card: dict, frame_idx: int, n_frames: int, card_num: int, total_cards: int, theme: dict, fonts: dict) -> Image.Image:
    p = frame_idx / max(n_frames - 1, 1)

    img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
    draw = ImageDraw.Draw(img)

    _draw_ruled_lines(draw, theme)
    _draw_margin_line(draw, theme)

    # Card number (faint, top right)
    num_alpha = 0.08
    num_col = alpha_col(theme["ink"], num_alpha, theme["bg"])
    _draw_text_safe(draw, (WIDTH - 140, 10), str(card_num), fonts["number"], num_col)

    # Emoji fade in (0–30% of p)
    if p >= 0.0:
        emoji_alpha = min(1.0, p / 0.30) if p < 0.30 else 1.0
        emoji_col = alpha_col(theme["ink"], emoji_alpha, theme["bg"])
        _draw_emoji_safe(draw, (100, 40), card.get("emoji", "📚"), fonts["emoji"], emoji_col)

    # Title types on (8%–50%)
    title = card.get("title", "")
    if p >= 0.08:
        title_progress = min(1.0, (p - 0.08) / (0.50 - 0.08))
        chars_to_show = max(1, int(len(title) * title_progress))
        visible_title = title[:chars_to_show]
        tx = (WIDTH - _text_width(draw, title, fonts["title"])) // 2
        ty = 50
        _draw_text_safe(draw, (tx, ty), visible_title, fonts["title"], theme["ink"])

        # Colored underline draws left→right after title appears (40%–55%)
        if p >= 0.40:
            ul_prog = min(1.0, (p - 0.40) / (0.55 - 0.40))
            ul_x1 = tx
            ul_x2 = tx + int(_text_width(draw, title, fonts["title"]) * ul_prog)
            ul_y = ty + 68
            draw.line([(ul_x1, ul_y), (ul_x2, ul_y)], fill=theme["accent"], width=4)

    # Horizontal divider (30%–50%)
    if p >= 0.30:
        div_prog = min(1.0, (p - 0.30) / (0.50 - 0.30))
        div_y = 140
        draw.line([(90, div_y), (90 + int((WIDTH - 110) * div_prog), div_y)], fill=theme["lines"], width=2)

    # Bullets appear at 38%, 57%, 76%
    bullets = card.get("bullets", [])
    bullet_starts = [0.38, 0.57, 0.76]
    for i, (bullet, start_p) in enumerate(zip(bullets, bullet_starts)):
        if p < start_p:
            break
        bullet_alpha = min(1.0, (p - start_p) / 0.08)
        bx = 110
        by = 170 + i * 130

        # Dot
        dot_col = alpha_col(theme["accent"], bullet_alpha, theme["bg"])
        draw.ellipse([(bx, by + 12), (bx + 14, by + 26)], fill=dot_col)

        # Guide line fades in
        guide_col = alpha_col(theme["lines"], bullet_alpha * 0.6, theme["bg"])
        guide_prog = min(1.0, (p - start_p) / 0.12)
        draw.line([(bx + 20, by + 19), (bx + 20 + int((WIDTH - bx - 40) * guide_prog), by + 19)],
                  fill=guide_col, width=1)

        # Text types on
        text_prog = min(1.0, (p - start_p) / 0.15)
        chars = max(1, int(len(bullet) * text_prog))
        text_col = alpha_col(theme["ink"], bullet_alpha, theme["bg"])
        _draw_text_safe(draw, (bx + 24, by), bullet[:chars], fonts["body"], text_col)

    # Decorative element at bottom right (last 12%)
    if p >= 0.88:
        deco_alpha = min(1.0, (p - 0.88) / 0.12)
        hint = card.get("drawingHint", "none")
        deco_col = alpha_col(theme["accent2"], deco_alpha * 0.25, theme["bg"])
        dx, dy = WIDTH - 200, HEIGHT - 160
        if hint == "circle":
            draw.ellipse([(dx, dy), (dx + 120, dy + 80)], outline=deco_col, width=3)
        elif hint == "box":
            draw.rectangle([(dx, dy), (dx + 120, dy + 80)], outline=deco_col, width=3)
        elif hint == "arrow":
            draw.line([(dx, dy + 40), (dx + 120, dy + 40)], fill=deco_col, width=3)
            draw.line([(dx + 100, dy + 20), (dx + 120, dy + 40), (dx + 100, dy + 60)], fill=deco_col, width=3)
        elif hint == "underline":
            draw.line([(dx, dy + 70), (dx + 120, dy + 70)], fill=deco_col, width=4)

    _draw_progress_bar(draw, p, theme)
    return img


# ── Slides style renderer ──────────────────────────────────────────────────────
def _render_slides_frame(card: dict, frame_idx: int, n_frames: int, card_num: int, total_cards: int, theme: dict, fonts: dict) -> Image.Image:
    p = frame_idx / max(n_frames - 1, 1)

    # Slides use dark theme bg regardless, unless theme overrides
    bg = theme["bg"]
    img = Image.new("RGB", (WIDTH, HEIGHT), bg)
    draw = ImageDraw.Draw(img)

    # Accent bar across top
    draw.rectangle([(0, 0), (WIDTH, 40)], fill=theme["accent"])

    # Card number top right
    num_str = f"{card_num}/{total_cards}"
    _draw_text_safe(draw, (WIDTH - 80, 10), num_str, fonts["small"], theme["bg"])

    # Emoji centered, large, fades in (0–25%)
    emoji_alpha = min(1.0, p / 0.25) if p < 0.25 else 1.0
    emoji_col = alpha_col(theme["ink"], emoji_alpha, bg)
    emoji = card.get("emoji", "📚")
    _draw_emoji_safe(draw, (WIDTH // 2 - 50, 60), emoji, fonts["emoji"], emoji_col)

    # Title: fade + slight upward slide (15%–45%)
    title = card.get("title", "")
    if p >= 0.15:
        t_prog = min(1.0, (p - 0.15) / (0.45 - 0.15))
        title_alpha = t_prog
        slide_offset = int((1.0 - t_prog) * 20)
        ty = 170 - slide_offset
        tx = (WIDTH - _text_width(draw, title, fonts["title"])) // 2
        title_col = alpha_col(theme["ink"], title_alpha, bg)
        _draw_text_safe(draw, (tx, ty), title, fonts["title"], title_col)

    # Colored square bullet markers + text fade in (40%, 58%, 74%)
    bullets = card.get("bullets", [])
    bullet_starts = [0.40, 0.58, 0.74]
    for i, (bullet, start_p) in enumerate(zip(bullets, bullet_starts)):
        if p < start_p:
            break
        b_alpha = min(1.0, (p - start_p) / 0.10)
        slide_off = int((1.0 - b_alpha) * 15)
        bx = 160
        by = 270 + i * 90 + slide_off
        b_col = alpha_col(theme["ink"], b_alpha, bg)
        sq_col = alpha_col(theme["accent2"], b_alpha, bg)
        draw.rectangle([(bx - 22, by + 8), (bx - 6, by + 24)], fill=sq_col)
        _draw_text_safe(draw, (bx, by), bullet, fonts["body"], b_col)

    _draw_progress_bar(draw, p, theme)
    return img


# ── public API ─────────────────────────────────────────────────────────────────
def render_frames(cards: list[dict], style: str, theme_name: str) -> list[Image.Image]:
    theme = THEMES.get(theme_name, THEMES["Clean"])

    # For Slides style with non-Dark theme, still use the theme bg
    # For Dark theme + Slides, looks great as-is
    fonts = _get_fonts()
    frames: list[Image.Image] = []
    total_cards = len(cards)

    for card_num, card in enumerate(cards, 1):
        duration = card.get("duration", 10)
        n_frames = duration * FPS

        for fi in range(n_frames):
            if style == "Whiteboard":
                frame = _render_whiteboard_frame(card, fi, n_frames, card_num, total_cards, theme, fonts)
            else:
                frame = _render_slides_frame(card, fi, n_frames, card_num, total_cards, theme, fonts)
            frames.append(frame)

        # Hold last frame for 0.4s between cards
        last_frame = frames[-1].copy()
        for _ in range(HOLD_FRAMES):
            frames.append(last_frame)

    return frames
