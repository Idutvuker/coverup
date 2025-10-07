# Generated test file for coverup.llm.GeminiCaller

import sys
import importlib
import types


def _install_fake_genai(monkeypatch, response_text="ok"):
    google_mod = types.ModuleType("google")
    genai_mod = types.ModuleType("google.genai")

    class FakeModels:
        def __init__(self, recorder):
            self.recorder = recorder

        def generate_content(self, model, contents):
            self.recorder["model"] = model
            self.recorder["contents"] = contents
            return types.SimpleNamespace(text=response_text)

    class FakeClient:
        def __init__(self):
            self.models = FakeModels(recorder={})

    genai_mod.Client = FakeClient
    google_mod.genai = genai_mod

    monkeypatch.setitem(sys.modules, "google", google_mod)
    monkeypatch.setitem(sys.modules, "google.genai", genai_mod)


def _import_geminicaller():
    sys.modules.pop("coverup.llm.GeminiCaller", None)
    return importlib.import_module("coverup.llm.GeminiCaller")


def test_geminicaller_init_uses_genai_client_default(monkeypatch):
    _install_fake_genai(monkeypatch)
    mod = _import_geminicaller()
    GeminiCaller = mod.GeminiCaller

    gc = GeminiCaller()
    assert isinstance(gc.model, str)
    assert hasattr(gc.client, "models")


def test_geminicaller_call_returns_text_and_passes_args(monkeypatch):
    _install_fake_genai(monkeypatch, response_text="response here")
    mod = _import_geminicaller()
    GeminiCaller = mod.GeminiCaller

    gc = GeminiCaller(model="custom-model")
    result = gc.call("hello")
    assert result == "response here"
    assert gc.client.models.recorder == {"model": "custom-model", "contents": "hello"}