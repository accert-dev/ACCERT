import json
import threading
import time

from tutorial.gui.scenario_cache import ScenarioCache


def test_cache_key_includes_payload_and_file_content(tmp_path):
    source = tmp_path / "source.csv"
    source.write_text("value,1\n", encoding="utf-8")
    cache = ScenarioCache(tmp_path / "cache")

    first = cache.key_for({"workflow": "crt_only", "input_csv": str(source)})
    source.write_text("value,2\n", encoding="utf-8")
    second = cache.key_for({"workflow": "crt_only", "input_csv": str(source)})

    assert first != second


def test_cache_round_trip_and_artifact_validation(tmp_path):
    output = tmp_path / "result.csv"
    output.write_text("result\n1\n", encoding="utf-8")
    cache = ScenarioCache(tmp_path / "cache")
    result = {"workflow": "crt_only", "files": {"results": {"path": str(output)}}}

    cache.put("abc", result)

    assert cache.get("abc") == result
    output.unlink()
    assert cache.get("abc") is None


def test_corrupt_cache_entry_is_ignored(tmp_path):
    cache = ScenarioCache(tmp_path / "cache")
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    (cache_dir / "bad.json").write_text("not json", encoding="utf-8")

    assert cache.get("bad") is None
    assert cache.stats()["misses"] == 1


def test_cache_key_is_stable_for_mapping_order(tmp_path):
    cache = ScenarioCache(tmp_path / "cache")

    first = cache.key_for({"b": 2, "a": 1})
    second = cache.key_for({"a": 1, "b": 2})

    assert first == second


def test_key_lock_serializes_identical_in_flight_work(tmp_path):
    cache = ScenarioCache(tmp_path / "cache")
    active = 0
    maximum = 0
    guard = threading.Lock()

    def worker():
        nonlocal active, maximum
        with cache.key_lock("same"):
            with guard:
                active += 1
                maximum = max(maximum, active)
            time.sleep(0.01)
            with guard:
                active -= 1

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert maximum == 1


def test_result_affecting_inputs_and_versions_invalidate_key(tmp_path):
    cache = ScenarioCache(tmp_path / "cache")
    base = {
        "country": "United States",
        "num_orders": 10,
        "year_dollar": 2025,
    }
    first = cache.key_for(base, model_version="model-a")

    assert cache.key_for({**base, "country": "China"}, model_version="model-a") != first
    assert cache.key_for({**base, "num_orders": 20}, model_version="model-a") != first
    assert cache.key_for({**base, "year_dollar": 2024}, model_version="model-a") != first
    assert cache.key_for(base, model_version="model-b") != first
