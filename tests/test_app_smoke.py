from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import main


def test_main_imports() -> None:
    assert main.app is not None


def test_health_endpoint() -> None:
    payload = main.health_check()

    assert payload["status"] == "ok"