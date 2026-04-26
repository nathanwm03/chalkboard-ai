import os
import json
import anthropic


def generate_cards(content: str, topic: str) -> list[dict]:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    client = anthropic.Anthropic(api_key=api_key)

    system_prompt = (
        "You are an educational video script writer. Always reply with ONLY a raw JSON array. "
        "No markdown, no backticks, no explanation. Start with [ and end with ]."
    )

    user_prompt = f"""You are turning a document into a short 30-90 second educational video focused on: '{topic}'.

Document content:
---
{content[:4000]}
---

Generate 4-7 cards. Return ONLY this JSON format:
[
  {{
    "title": "Max 5 word title",
    "bullets": ["Key point one max 10 words", "Key point two", "Key point three"],
    "narration": "A full 2-3 sentence spoken explanation of this card, natural and engaging, as if a teacher is explaining it.",
    "emoji": "🎯",
    "drawingHint": "circle",
    "duration": 10
  }}
]

Rules:
- title: max 5 words
- bullets: 2-3 items, max 10 words each
- narration: 2-3 natural spoken sentences per card (this will be read aloud by TTS)
- emoji: one relevant emoji
- drawingHint: one of circle, arrow, underline, box, none
- duration: 6-14 seconds per card, total across all cards must be 30-90 seconds
- First card must introduce the topic
- Last card must be a key takeaway or summary
- Educational tone, plain conversational English"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = message.content[0].text.strip()

    # Strip accidental backticks or markdown fences
    raw = raw.replace("```json", "").replace("```", "").strip()

    # Find the first [ and last ] and parse that slice
    start = raw.find("[")
    end = raw.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"Could not find JSON array in response: {raw[:200]}")

    cards = json.loads(raw[start : end + 1])

    # Validate and sanitize each card
    for card in cards:
        card.setdefault("title", "Untitled")
        card.setdefault("bullets", [])
        card.setdefault("narration", "")
        card.setdefault("emoji", "📚")
        card.setdefault("drawingHint", "none")
        card.setdefault("duration", 10)
        card["duration"] = max(6, min(14, int(card["duration"])))

    return cards
