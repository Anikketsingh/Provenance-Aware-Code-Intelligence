"""Backend tests. Live calls need a key and cost money, so they run only with `-m live`."""

import pytest

from provenance.synth import backend
from provenance.synth.backend import GeminiBackend, MissingKeyError


def test_missing_key_gives_clear_error(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr(backend, "load_dotenv", lambda *_: False)
    with pytest.raises(MissingKeyError):
        GeminiBackend()


@pytest.mark.live
def test_live_generate():
    reply = GeminiBackend().generate(
        "Reply with exactly the word: ready", max_tokens=200, temperature=0, seed=1
    )
    assert "ready" in reply.lower()
