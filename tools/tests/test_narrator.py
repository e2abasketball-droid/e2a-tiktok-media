"""E2A narrator standard guard (2026-11-27). Run: python3 -m pytest tools/tests/test_narrator.py -q"""
import importlib.util, json, os, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("narrator", os.path.join(ROOT, "tools", "narrator.py"))
n = importlib.util.module_from_spec(spec); spec.loader.exec_module(n)


def test_default_is_nathaniel_v4():
    assert n.CFG["voice"]["voice_id"] == "9rR45HW0vcBmpCbkc4m9"
    assert n.CFG["synthesis"]["model_id"] == "eleven_v4"
    assert n.CFG["narrator_override"] is False


def test_params_one_take_and_tags_only_on_change():
    p = n.params([["hook", "A."], ["hook", "B."], ["lesson", "C."]])
    assert p["generations_count"] == 1 and p["voice_id"] == "9rR45HW0vcBmpCbkc4m9"
    assert p["prompt"].count("[intriguing, confident]") == 1 and "[slower, confident teaching] C." in p["prompt"]


def test_check_rejects_other_voice_and_model():
    assert not n.check("DaueUomjhh8LFuAV8aGj", "eleven_v4")[0]
    assert not n.check("9rR45HW0vcBmpCbkc4m9", "eleven_v3")[0]
    assert n.check("9rR45HW0vcBmpCbkc4m9", "eleven_v4")[0]


def test_override_needs_owner_message():
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump({"narrator_override": True}, f)
    assert not n.check("other", "eleven_v3", f.name)[0]
    with open(f.name, "w") as g:
        json.dump({"narrator_override": True, "override_owner_message": "2026-12-01 thread X"}, g)
    assert n.check("other", "eleven_v3", f.name)[0]
