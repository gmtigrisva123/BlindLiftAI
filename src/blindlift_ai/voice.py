from __future__ import annotations


class VoiceInterface:
    """Simple placeholder for future speech integrations."""

    def transcribe(self, text: str) -> str:
        return text.strip()

    def speak(self, text: str) -> dict[str, str]:
        return {"mode": "text-fallback", "content": text}

