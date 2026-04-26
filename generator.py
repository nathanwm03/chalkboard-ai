import os
import json
import anthropic

_SYSTEM = (
    "You are an educational video script writer. Always reply with ONLY a raw JSON array. "
    "No markdown, no backticks, no explanation. Start with [ and end with ]."
)

_CARD_RULES = """
Generate 4-7 cards. Return ONLY this JSON format:
[
  {
    "title": "Max 5 word title",
    "bullets": ["Key point one max 10 words", "Key point two", "Key point three"],
    "narration": "A full 2-3 sentence spoken explanation, natural and engaging, as if a teacher is explaining it.",
    "emoji": "🎯",
    "drawingHint": "circle",
    "duration": 10
  }
]

Rules:
- title: max 5 words
- bullets: 2-3 items, max 10 words each
- narration: 2-3 natural spoken sentences (read aloud by TTS)
- emoji: one relevant emoji
- drawingHint: one of circle, arrow, underline, box, none
- duration: 6-14 seconds per card, total 30-90 seconds
- First card must introduce the topic
- Last card must be a key takeaway or summary
- Educational tone, plain conversational English"""


def _parse_cards(raw: str) -> list:
    raw = raw.replace("```json", "").replace("```", "").strip()
    start = raw.find("[")
    end = raw.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON array in response: {raw[:200]}")
    cards = json.loads(raw[start:end + 1])
    for card in cards:
        card.setdefault("title", "Untitled")
        card.setdefault("bullets", [])
        card.setdefault("narration", "")
        card.setdefault("emoji", "📚")
        card.setdefault("drawingHint", "none")
        card.setdefault("duration", 10)
        card["duration"] = max(6, min(14, int(card["duration"])))
    return cards


def generate_cards(content: str, topic: str) -> list:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    client = anthropic.Anthropic(api_key=api_key)

    if content.startswith("IMAGE:"):
        b64 = content[len("IMAGE:"):]
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": b64,
                    },
                },
                {
                    "type": "text",
                    "text": (
                        f"You are an educational whiteboard video script writer. "
                        f"This image contains educational content. "
                        f"Focus on the topic: '{topic}'.\n"
                        f"Generate 4-7 whiteboard animation cards from this image."
                        f"{_CARD_RULES}"
                    ),
                },
            ],
        }]
    else:
        messages = [{
            "role": "user",
            "content": (
                f"You are turning a document into a short 30-90 second educational video "
                f"focused on: '{topic}'.\n\n"
                f"Document content:\n---\n{content[:4000]}\n---\n"
                f"{_CARD_RULES}"
            ),
        }]

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2048,
        system=_SYSTEM,
        messages=messages,
    )

    return _parse_cards(message.content[0].text.strip())
