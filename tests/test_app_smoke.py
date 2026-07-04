import main


def test_main_imports() -> None:
    assert main.app is not None


def test_health_endpoint() -> None:
    payload = main.health_check()

    assert payload["status"] == "ok"