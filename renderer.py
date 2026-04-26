from PIL import Image, ImageDraw, ImageFont
import os

WIDTH, HEIGHT = 854, 480
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
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\calibrib.ttf",
        r"C:\Windows\Fonts\verdanab.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    paths_regular = [
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibri.ttf",
        r"C:\Windows\Fonts\verdana.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
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
    # Sizes scaled to 854x480 (~2/3 of original 1280x720)
    return {
        "title":  _load_font(True,  40),
        "body":   _load_font(False, 23),
        "small":  _load_font(False, 15),
        "number": _load_font(True,  60),
        "emoji":  _load_font(False, 47),
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
        return len(text) * 7


def _draw_ruled_lines(draw, theme):
    for y in range(0, HEIGHT, 24):
        draw.line([(0, y), (WIDTH, y)], fill=theme["lines"], width=1)


def _draw_margin_line(draw, theme):
    draw.line([(53, 0), (53, HEIGHT)], fill=theme["margin"], width=2)


def _draw_progress_bar(draw, p: float, theme):
    y = HEIGHT - 4
    draw.rectangle([(0, y), (WIDTH, HEIGHT)], fill=blend(theme["bg"], theme["lines"], 0.5))
    draw.rectangle([(0, y), (int(WIDTH * p), HEIGHT)], fill=theme["accent"])


# ── Whiteboard style renderer ──────────────────────────────────────────────────
def _render_whiteboard_frame(card, frame_idx, n_frames, card_num, total_cards, theme, fonts):
    p = frame_idx / max(n_frames - 1, 1)

    img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
    draw = ImageDraw.Draw(img)

    _draw_ruled_lines(draw, theme)
    _draw_margin_line(draw, theme)

    # Card number (faint, top right)
    num_col = alpha_col(theme["ink"], 0.08, theme["bg"])
    _draw_text_safe(draw, (WIDTH - 93, 7), str(card_num), fonts["number"], num_col)

    # Emoji fade in (0–30%)
    emoji_alpha = min(1.0, p / 0.30) if p < 0.30 else 1.0
    emoji_col = alpha_col(theme["ink"], emoji_alpha, theme["bg"])
    _draw_emoji_safe(draw, (67, 27), card.get("emoji", "📚"), fonts["emoji"], emoji_col)

    # Title types on (8%–50%)
    title = card.get("title", "")
    if p >= 0.08:
        title_progress = min(1.0, (p - 0.08) / 0.42)
        visible_title = title[:max(1, int(len(title) * title_progress))]
        tx = (WIDTH - _text_width(draw, title, fonts["title"])) // 2
        ty = 33
        _draw_text_safe(draw, (tx, ty), visible_title, fonts["title"], theme["ink"])

        # Underline draws left→right (40%–55%)
        if p >= 0.40:
            ul_prog = min(1.0, (p - 0.40) / 0.15)
            ul_x2 = tx + int(_text_width(draw, title, fonts["title"]) * ul_prog)
            draw.line([(tx, ty + 45), (ul_x2, ty + 45)], fill=theme["accent"], width=3)

    # Horizontal divider (30%–50%)
    if p >= 0.30:
        div_prog = min(1.0, (p - 0.30) / 0.20)
        draw.line([(60, 93), (60 + int((WIDTH - 73) * div_prog), 93)],
                  fill=theme["lines"], width=2)

    # Bullets at 38%, 57%, 76%
    bullets = card.get("bullets", [])
    for i, (bullet, start_p) in enumerate(zip(bullets, [0.38, 0.57, 0.76])):
        if p < start_p:
            break
        b_alpha = min(1.0, (p - start_p) / 0.08)
        bx = 73
        by = 113 + i * 87

        dot_col = alpha_col(theme["accent"], b_alpha, theme["bg"])
        draw.ellipse([(bx, by + 8), (bx + 9, by + 17)], fill=dot_col)

        guide_col = alpha_col(theme["lines"], b_alpha * 0.6, theme["bg"])
        guide_prog = min(1.0, (p - start_p) / 0.12)
        draw.line([(bx + 13, by + 13),
                   (bx + 13 + int((WIDTH - bx - 27) * guide_prog), by + 13)],
                  fill=guide_col, width=1)

        text_prog = min(1.0, (p - start_p) / 0.15)
        chars = max(1, int(len(bullet) * text_prog))
        text_col = alpha_col(theme["ink"], b_alpha, theme["bg"])
        _draw_text_safe(draw, (bx + 16, by), bullet[:chars], fonts["body"], text_col)

    # Decorative element bottom-right (last 12%)
    if p >= 0.88:
        deco_alpha = min(1.0, (p - 0.88) / 0.12)
        hint = card.get("drawingHint", "none")
        deco_col = alpha_col(theme["accent2"], deco_alpha * 0.25, theme["bg"])
        dx, dy = WIDTH - 133, HEIGHT - 107
        if hint == "circle":
            draw.ellipse([(dx, dy), (dx + 80, dy + 53)], outline=deco_col, width=2)
        elif hint == "box":
            draw.rectangle([(dx, dy), (dx + 80, dy + 53)], outline=deco_col, width=2)
        elif hint == "arrow":
            draw.line([(dx, dy + 27), (dx + 80, dy + 27)], fill=deco_col, width=2)
            draw.line([(dx + 60, dy + 13), (dx + 80, dy + 27), (dx + 60, dy + 40)],
                      fill=deco_col, width=2)
        elif hint == "underline":
            draw.line([(dx, dy + 47), (dx + 80, dy + 47)], fill=deco_col, width=3)

    _draw_progress_bar(draw, p, theme)
    return img


# ── Slides style renderer ──────────────────────────────────────────────────────
def _render_slides_frame(card, frame_idx, n_frames, card_num, total_cards, theme, fonts):
    p = frame_idx / max(n_frames - 1, 1)

    img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
    draw = ImageDraw.Draw(img)

    # Accent bar across top
    draw.rectangle([(0, 0), (WIDTH, 27)], fill=theme["accent"])

    # Card number top right
    num_str = f"{card_num}/{total_cards}"
    _draw_text_safe(draw, (WIDTH - 53, 7), num_str, fonts["small"], theme["bg"])

    # Emoji centered, fades in (0–25%)
    emoji_alpha = min(1.0, p / 0.25) if p < 0.25 else 1.0
    emoji_col = alpha_col(theme["ink"], emoji_alpha, theme["bg"])
    _draw_emoji_safe(draw, (WIDTH // 2 - 33, 40), card.get("emoji", "📚"),
                     fonts["emoji"], emoji_col)

    # Title: fade + slide up (15%–45%)
    title = card.get("title", "")
    if p >= 0.15:
        t_prog = min(1.0, (p - 0.15) / 0.30)
        slide_offset = int((1.0 - t_prog) * 13)
        ty = 113 - slide_offset
        tx = (WIDTH - _text_width(draw, title, fonts["title"])) // 2
        title_col = alpha_col(theme["ink"], t_prog, theme["bg"])
        _draw_text_safe(draw, (tx, ty), title, fonts["title"], title_col)

    # Bullets fade in from below (40%, 58%, 74%)
    bullets = card.get("bullets", [])
    for i, (bullet, start_p) in enumerate(zip(bullets, [0.40, 0.58, 0.74])):
        if p < start_p:
            break
        b_alpha = min(1.0, (p - start_p) / 0.10)
        slide_off = int((1.0 - b_alpha) * 10)
        bx = 107
        by = 180 + i * 60 + slide_off
        draw.rectangle([(bx - 15, by + 5), (bx - 4, by + 16)],
                       fill=alpha_col(theme["accent2"], b_alpha, theme["bg"]))
        _draw_text_safe(draw, (bx, by), bullet, fonts["body"],
                        alpha_col(theme["ink"], b_alpha, theme["bg"]))

    _draw_progress_bar(draw, p, theme)
    return img


# ── public API ─────────────────────────────────────────────────────────────────
def render_frames(cards: list, style: str, theme_name: str, frames_dir: str) -> list:
    """Render each frame as a JPEG in frames_dir. Returns list of file paths.
    Hold frames reuse the last path — no extra disk writes."""
    theme = THEMES.get(theme_name, THEMES["Clean"])
    fonts = _get_fonts()
    frame_paths = []
    total_cards = len(cards)
    counter = 0

    for card_num, card in enumerate(cards, 1):
        n_frames = card.get("duration", 10) * FPS
        last_path = None

        for fi in range(n_frames):
            if style == "Whiteboard":
                img = _render_whiteboard_frame(card, fi, n_frames, card_num, total_cards, theme, fonts)
            else:
                img = _render_slides_frame(card, fi, n_frames, card_num, total_cards, theme, fonts)

            path = os.path.join(frames_dir, f"frame_{counter:06d}.jpg")
            img.save(path, "JPEG", quality=85)
            img.close()
            frame_paths.append(path)
            last_path = path
            counter += 1

        # Hold last frame 0.4s — reuse same file, no copy
        for _ in range(HOLD_FRAMES):
            frame_paths.append(last_path)

    return frame_paths
