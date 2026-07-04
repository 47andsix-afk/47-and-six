import os


class Settings:
    def __init__(self) -> None:
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


settings = Settings()
