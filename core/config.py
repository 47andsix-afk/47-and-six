import os

USE_MOCK = os.getenv("USE_MOCK_RESPONSES", "false").lower() in ("1", "true", "yes")


def is_mock_enabled() -> bool:
    return USE_MOCK
